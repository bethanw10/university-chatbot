import codecs
import time
import urllib

import gc

import bs4
import pandas as pd
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextLine
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser

from university_chatbot import *

# Date uni website uses for week one (different from actual week one date)
week_one = date(2017, 8, 28)


def scrape_module_timetable(module_code):
    url = "http://www3.wlv.ac.uk/timetable/testmahi2_1.asp"
    r = requests.post(url, data={'module': module_code})
    page = BeautifulSoup(r.text, "html.parser")

    # Scrape module name
    list_items = page.find_all("li")
    if len(list_items) < 1 or module_code not in list_items[0].text:
        # Invalid module code
        return "", []

    full_module_name = list_items[0].text
    module_name = full_module_name.replace(module_code, "").strip()

    # Scrape module timetable
    timetable = []
    table = page.findAll("table", class_="filtered")

    if len(table) < 1:
        # No timetable found
        return module_name, []

    rows = table[0].find_all('tr')

    for row in rows:
        columns = row.findAll('td')

        # Ignore empty rows
        if not columns:
            continue

        columns = [element.text.strip() for element in columns]
        timetable.append([element for element in columns])

    df = pd.DataFrame(timetable, columns=["Module", "Instance", "Activity", "Weeks", "Day", "Start",
                                          "Finishes", "Campus", "Room", "Lecturer", "Group/cohort details"])
    # Module, Instance, Activity, Weeks, Day, Start, Finishes, Campus, Room, Lecturer, Group/cohort details.
    return module_name, df


def get_week_number(for_date):
    difference = for_date - week_one
    return 1 + (difference.days // 7)


def get_date_by_week_number(week_number, day="Monday"):
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    if day not in days:
        raise ValueError(day + "is not a valid day of the week")

    day_number = days.index(day)

    start_date = week_one + timedelta(weeks=week_number - 1, days=day_number)
    return start_date


def print_all_activity_dates(module_code):
    _, timetable = scrape_module_timetable(module_code)

    for row in timetable:
        activity = row[2]
        week_ranges = row[3].split(",")
        day = row[4]
        start_time = row[5]

        for week_range in week_ranges:
            # Range of weeks e.g. 6 ~ 16
            if '~' in week_range:
                start_and_end = [number.strip() for number in week_range.split('~')]
                print(start_and_end)

                start = int(start_and_end[0])
                end = int(start_and_end[1])

                for week_number in range(start, end):
                    d = get_date_by_week_number(week_number, day)
                    t = time.strptime(start_time, "%H:%M")
                    dt = datetime.datetime(year=d.year, month=d.month, day=d.day,
                                           hour=t.tm_hour, minute=t.tm_min)
                    print(activity + ": " + dt.strftime('%d %b %Y %I:%M%p'))

            # Single week e.g. 6
            else:
                week_number = int(week_range)
                d = get_date_by_week_number(week_number, day)
                t = time.strptime(start_time, "%H:%M")
                dt = datetime.datetime(year=d.year, month=d.month, day=d.day,
                                       hour=t.tm_hour, minute=t.tm_min)
                print(activity + ": " + dt.strftime('%d %b %Y %I:%M%p'))


def print_next_activity(module_code):
    print("Next activity for " + module_code + ": ")

    now = datetime.datetime.now()
    current_week = get_week_number(now.date())

    _, timetable = scrape_module_timetable(module_code)

    # Loop through each activity to find the first activity that occurs after the current date
    for row in timetable:
        activity = row[2]
        week_ranges = row[3].split(",")
        day = row[4]
        start_time = row[5]

        for week_range in week_ranges:
            # Range of weeks e.g. 6 ~ 16
            if '~' in week_range:
                start_and_end = [number.strip() for number in week_range.split('~')]

                start = int(start_and_end[0])
                end = int(start_and_end[1])

                if end < current_week:
                    continue

                for week_number in range(start, end):
                    if week_number < current_week:
                        continue

                    d = get_date_by_week_number(week_number, day)
                    t = time.strptime(start_time, "%H:%M")
                    dt = datetime.datetime(year=d.year, month=d.month, day=d.day,
                                           hour=t.tm_hour, minute=t.tm_min)

                    if dt > now:
                        print("\t" + activity + ": " + dt.strftime('%d %b %Y %I:%M%p'))
                        return

            # Single week e.g. 6
            else:
                week_number = int(week_range)
                if week_number < current_week:
                    continue

                d = get_date_by_week_number(week_number, day)
                t = time.strptime(start_time, "%H:%M")
                dt = datetime.datetime(year=d.year, month=d.month, day=d.day,
                                       hour=t.tm_hour, minute=t.tm_min)

                if dt > now:
                    print("\t" + activity + ": " + dt.strftime('%d %b %Y %I:%M%p'))
                    return


def import_modules_peewee(courses):
    for course_name, module_codes in courses.items():

        # Save each course
        course, _ = Course.get_or_create(name=course_name)
        print(course.name)

        for module_code in module_codes:

            module_name, timetables = scrape_module_timetable(module_code)

            print(module_code)

            # Skip modules with no timetables
            if len(timetables) == 0:
                continue

            semester = timetables.ix[0, 'Instance']

            # Save module if it doesn't already exist
            module, is_new_module = Module.get_or_create(name=module_name, code=module_code, semester=semester)
            Course_Module.create(module=module, course=course)

            # if not is_new_module:
            # continue

            for index, row in timetables.iterrows():
                timetable = Timetable.create(module=module, activity=row["Activity"], day=row['Day'],
                                             start=row['Start'], finishes=row['Finishes'], campus=row['Campus'],
                                             room=row['Room'], lecturer=row['Lecturer'],
                                             group_details=row['Group/cohort details'])

                # if not is_new:
                #    continue

                week_ranges = row['Weeks'].split(",")
                day = row['Day']

                print(week_ranges)

                # Here we go
                for week_range in week_ranges:

                    # Range of weeks e.g. 6 ~ 16
                    if '~' in week_range:
                        start_and_end = [number.strip() for number in week_range.split('~')]
                        start = int(start_and_end[0])
                        end = int(start_and_end[1])

                        start_week = get_date_by_week_number(start, day)
                        end_week = get_date_by_week_number(end, day)

                    # Single week e.g. 6
                    else:
                        week_number = int(week_range)
                        start_week = end_week = get_date_by_week_number(week_number, day)

                    check = Week_Range.select().where(
                        (
                                Week_Range.timetable == timetable) & Week_Range.start_week == start_week & Week_Range.end_week == end_week)

                    if len(check) != 0:
                        continue

                    Week_Range.get_or_create(timetable=timetable, start_week=start_week, end_week=end_week)


# Get module codes from course guide pdfs
def get_module_codes(url):
    r = requests.get(url, stream=True)

    with open("temp/" + url[-20:], 'wb') as f:
        f.write(r.content)

    with open("temp/" + url[-20:], 'rb') as f:
        parser = PDFParser(f)
        document = PDFDocument(parser)

        # Create PDFResourceManager object that stores shared resources such as fonts or images
        resource_manager = PDFResourceManager()
        la_params = LAParams()

        # Extract the device to page aggregator to get LT object elements
        device = PDFPageAggregator(resource_manager, laparams=la_params)

        # Interpreter needs to be connected to resource manager for shared resources and device
        interpreter = PDFPageInterpreter(resource_manager, device)

        module_codes = []

        for page in PDFPage.create_pages(document):
            first = True

            interpreter.process_page(page)

            # The device renders the layout from interpreter
            layout = device.get_result()
            for lt_obj in layout:
                if isinstance(lt_obj, LTTextBox) or isinstance(lt_obj, LTTextLine):
                    text = lt_obj.get_text().strip()

                    if re.match("\d\w{2}\d{3}", text):
                        if len(text) > 6:
                            print("],")

                            parser.close()
                            return module_codes

                        if not first:
                            print(", ", end=''),
                        else:
                            first = False

                        print("\"" + text + "\"", end=''),

    parser.close()
    return module_codes


def get_timetables():
    file = open("temp/Faculty of Science and Engineering.html")

    page = BeautifulSoup(file, "html.parser")
    list_items = page.find_all("li")

    for child in list_items:
        pdf_url = child.find("a", href=True)["href"]
        if "Sandwich" not in child.string \
                and "Foundation" not in child.string \
                and "Top-up" not in child.string \
                and "Top-Up" not in child.string:
            print("\"" + child.string + "\": [")
            get_module_codes(pdf_url)
            gc.collect()


# Prints all courses in format required for DialogFlow entities
def print_courses():
    courses = Course.select(Course)

    for course in courses:
        print("\"" + course.name + "\",", end='')

        synonym = course.name.replace("(", "").replace(")", "").strip()

        print("\"" + synonym + "\",", end='')

        synonym2 = synonym.replace("MEng", "").replace("BSc", "").replace("BEng", "").replace("HNC", "") \
            .replace("HND", "") \
            .replace("MSci", "").replace("MSc", "").replace("Hons", "").strip()

        print("\"" + synonym2 + "\"")


# Prints all modules in format required for DialogFlow entities
def print_modules():
    modules = Module.select(Module)

    for module in modules:
        print("\"" + module.code + "\",", end='')
        print("\"" + module.name.replace("(", "").replace(")", "") + "\"")


def print_lecturers():
    timetables = Timetable.select(Timetable.lecturer).distinct()

    for timetable in timetables:
        print("\"" + timetable.lecturer.split(" ")[0] + "\",", end='')
        print("\"" + timetable.lecturer.replace(" (Dr)", "") + "\"", end='')
        print("\"" + timetable.lecturer.replace(" (Dr)", "") + "\"")


def add_dummy_module():
    courses = Course.select(Course)

    module_name, timetable = scrape_dummy_timetable()
    module_codes = ["6AA000", "5AA000", "4AA000"]

    for module_code in module_codes:
        for course in courses:
            print(module_name)

            semester = "Semester 3"

            # Save module if it doesn't already exist
            module, is_new_module = Module.get_or_create(name=module_name, code=module_code, semester=semester)

            Course_Module.create(module=module, course=course)

            if not is_new_module:
                continue

            for index, row in timetable.iterrows():
                timetableDb = Timetable.create(module=module, activity=row["Activity"], day=row['Day'],
                                               start=row['Start'], finishes=row['Finishes'], campus=row['Campus'],
                                               room=row['Room'], lecturer=row['Lecturer'],
                                               group_details=row['Group/cohort details'])

                week_ranges = row['Weeks'].split(",")
                day = row['Day']

                print(week_ranges)

                # Here we go
                for week_range in week_ranges:

                    # Range of weeks e.g. 6 ~ 16
                    if '~' in week_range:
                        start_and_end = [number.strip() for number in week_range.split('~')]
                        start = int(start_and_end[0]) + 17
                        end = int(start_and_end[1]) + 17

                        start_week = get_date_by_week_number(start, day)
                        end_week = get_date_by_week_number(end, day)

                    # Single week e.g. 6
                    else:
                        week_number = int(week_range) + 17
                        start_week = end_week = get_date_by_week_number(week_number, day)

                    check = Week_Range.select().where(
                        (
                                    Week_Range.timetable == timetableDb) & Week_Range.start_week == start_week & Week_Range.end_week == end_week)

                    if len(check) != 0:
                        continue

                    Week_Range.get_or_create(timetable=timetableDb, start_week=start_week, end_week=end_week)


def scrape_dummy_timetable():
    url = "../UoW Timetable - Produced Timetable.html"
    f = codecs.open(url, 'r', 'utf-8')
    page = BeautifulSoup(f.read(), "html.parser")
    module_code = "4AA000"

    # Scrape module name
    list_items = page.find_all("li")
    if len(list_items) < 1 or module_code not in list_items[0].text:
        # Invalid module code
        return "", []

    full_module_name = list_items[0].text
    module_name = full_module_name.replace(module_code, "").strip()

    # Scrape module timetable
    timetable = []
    table = page.findAll("table", class_="filtered")

    if len(table) < 1:
        # No timetable found
        return module_name, []

    rows = table[0].find_all('tr')

    for row in rows:
        columns = row.findAll('td')

        # Ignore empty rows
        if not columns:
            continue

        columns = [element.text.strip() for element in columns]
        timetable.append([element for element in columns])

    df = pd.DataFrame(timetable, columns=["Module", "Instance", "Activity", "Weeks", "Day", "Start",
                                          "Finishes", "Campus", "Room", "Lecturer", "Group/cohort details"])
    # Module, Instance, Activity, Weeks, Day, Start, Finishes, Campus, Room, Lecturer, Group/cohort details.
    return "Example Module", df


print_lecturers()
