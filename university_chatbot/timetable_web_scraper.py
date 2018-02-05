'''
Questions-
When's the next lecture/workshop/assessment for computer science?
What have I got next for 4CS001
What lectures are tomorrow?
what do I have week 2?

Activities  -
Lecture
Tutorial
Workshop
Assessment
Resit Assessment

weeks are written as
5, 6 ~ 12
'''
import time
import urllib

import gc
import pandas as pd
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextLine
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser

from university_chatbot import *

week_one = date(2017, 8, 28)

courses = {
    "BEng (Hons) Civil and Transportation Engineering": [
        "4CV003", "4CV010", "4CV002", "4CV005", "4CV001", "4CV009", "5CN022", "5CV005", "5CV001", "5CV003", "5CV006",
        "5CV009", "6CV011", "6CV013", "6CV005", "6CN020", "6CV003", "6CV008"],
    "BEng(Hons) Civil Engineering": [
        "4CV006", "4CV013", "4CV012", "4CV014", "4CV009", "4CV011", "5CV016", "5CV017", "5CV002", "5CV010", "5CV004",
        "5CV015", "6CV020", "6CV021", "6CV006", "6CV009", "6CV018", "6CV019"],
    "BSc (Hons) Building Surveying": [
        "4CN002", "4CN016", "4CN006", "4CN030", "4CN001", "4CN027", "5CN001", "5CN022", "5CN029", "5CN038", "5CN007",
        "5CN010", "6CN010", "6CN019", "6CN002", "6CN011", "6CN007", "6CN006", "6CN012""4CN002", "4CN016", "4CN006",
        "4CN030", "4CN001", "4CN027", "5CN001", "5CN022", "5CN029", "5CN038", "5CN007", "5CN010", "5CN004", "6CN010",
        "6CN019", "6CN002", "6CN011", "6CN007", "6CN006", "6CN012"],
    "BSc(Hons)  Interior Architecture and Property Development": [
        "4AT003", "4AT005", "4AT002", "4AT004", "4AT009", "4AT019", "5AT016", "5AT012", "5CN029", "5AT013", "5AT002",
        "5AT014", "6AT015", "6AT008", "6AT005", "6CN019", "6AT001"],
    "BSc(Hons) Architectural Design Technology": [
        "4AT003", "4AT005", "4AT002", "4AT004", "4AT009", "4AT019", "5AT019", "5AT018", "5CN018", "5AT013", "5AT002",
        "5AT014", "6AT015", "6AT016", "6AT005", "6CN007", "6AT001"],
    "BSc(Hons) Architecture": [
        "4AT014", "4AT016", "4AT017", "4AT018", "4AT015", "5AT021", "5AT024", "5AT022", "5AT020", "5AT023", "6AT009",
        "6AT012", "6AT013", "6AT014", "6AT011"],
    "BSc(Hons) Construction Management": [
        "4CN002", "4CN016", "4CN006", "4CN030", "4CN001", "4CN027", "5CN001", "5CN022", "5CN038", "5CN002", "5CN010",
        "5CN018", "6CN010", "6CN019", "6CN011", "6CN017", "6CN005", "6CN012", "6CN006""4CN002", "4CN016", "4CN006",
        "4CN030", "4CN001", "4CN027", "5CN001", "5CN022", "5CN038", "5CN002", "5CN010", "5CN018", "6CN010", "6CN019",
        "6CN011", "6CN017", "6CN018", "6CN005", "6CN012", "6CN006"],
    "BSc(Hons) Environmental Health": [
        "4EH003", "4EH004", "4EH002", "4EH001", "4EH009", "4HW002", "5EH002", "5EH004", "5EH005", "5EH008", "5EH009",
        "5EH003", "6EH004", "6EH002", "6EH008", "6EH005", "6EH001", "6EH003""4EH003", "4EH004", "4EH002", "4EH001",
        "4EH009", "4HW002", "5EH002", "5EH004", "5EH005", "5EH008", "5EH009", "5EH003", "6EH004", "6EH002", "6EH008",
        "6EH005", "6EH001", "6EH003"],
    "BSc(Hons) Geography, Urban Environments and Climate Change": [
        "4CN002", "4EA003", "4EH001", "4EH002", "4EA001", "4EA002", "5CV003", "5CN018", "5EA001", "5EA003", "5AT024",
        "5EA002", "6EA002", "6AT012", "6CV005", "6EA001", "6CN012", "6EA003", "6EA004"],
    "BSc(Hons) Property Management and Real Estate": [
        "4CN002", "4CN016", "4CN006", "4CN030", "4CN001", "4CN027", "5CN001", "5CN022", "5CN038", "5CN016", "5CN014",
        "5CN010", "6CN010", "6CN019", "6CN011", "6CN003", "6CN022", "6CN012", "6CN006"],
    "BSc(Hons) Quantity Surveying": [
        "4CN002", "4CN016", "4CN006", "4CN030", "4CN001", "4CN027", "5CN001", "5CN022", "5CN038", "5CN035", "5CN034",
        "5CN010", "6CN010", "6CN019", "6CN011", "6CN024", "6CN023"],
    "HNC Architectural Studies": [
        "4AT003", "4AT005", "4AT002", "4AT009", "4AT019"],
    "HNC Building Studies": [
        "4CN002", "4CN006", "4CN001", "4CN016", "4CN030", "4CN027"],
    "HND Architectural Design": [
        "4AT003", "4AT005", "4AT002", "4AT004", "4AT009", "4AT019", "5AT018", "5AT019", "5CN018", "5AT013", "5AT002",
        "5AT014"],
    "HND Construction and The Built Environment": [
        "4CN002", "4CN016", "4CN006", "4CN030", "4CN001", "4CN027", "5CN001", "5CN022", "5CN038", "5CN029", "5CN007",
        "5CN010"],
    "MSc Building Information Modelling for Integrated Construction": [
        "7AT003", "7ET022", "7AT005", "7AT001", "7AT006", "7ET023", "7CN003", "7CN010", "7CV003", "7CV004", "7CV007",
        "7EA006", "7EA007", "7EA016", "7EH004", "7AT002""7AT003", "7AT005", "7AT006", "7CN003", "7CN010", "7CV003",
        "7CV004", "7CV007", "7EA006", "7EA007", "7EA016", "7EH004", "7AT002"],
    "MSc Civil Engineering Management": [
        "7CV006", "7ET022", "7CV005", "7CV007", "7CN005", "7CV004", "7ET023"],
    "MSc Construction Law and Dispute Resolution": [
        "7CN013", "7CN011", "7CN017", "7CN012", "7CN001", "7CN010", "7CN008", "7ET022", "7ET023""7CN013", "7CN011",
        "7CN017", "7CN012", "7CN001", "7CN010", "7CN008", "7ET022", "7ET023"],
    "MSc Construction Project Management": [
        "7CN004", "7ET022", "7CN001", "7CN013", "7CN005", "7CN003", "7CN006", "7ET023"],
    "MSc Environmental Technology": [
        "7EA014", "7EA015", "7EA011", "7EH002", "7EA001", "7EA012", "7EA007", "7EA013", "7AB001"],
    "MSc Oil and Gas Management": [
        "7CM002", "7EA018", "7LW002", "7BE002", "7EA017", "7EA019", "7EA006", "7MG001"],
    "MSc Programme and Project Management": [
        "7CN015", "7ET022", "7CN017", "7HR006", "7CN018", "7CN016", "7ET023"],
    "Postgraduate Certificate Building Information Modelling": [
        "7AT003", "7AT007", "7AT006"],
    "Postgraduate Certificate Construction Law and Dispute Resolution": [
        "7CN011", "7CN010", "7CN008", "7CN012", "7CN013", "7CN017""7CN011", "7CN010", "7CN008", "7CN012", "7CN013",
        "7CN017"],
    "Postgraduate Certificate Project and Programme Management": [
        "7CN015", "7CN018", "7HR006"],
    "BEng (Hons) Aerospace Engineering": [
        "4MA007", "4MA008", "4MA009", "4MA010", "4MA011", "5MA005", "5MA006", "5MA007", "5MA009", "5MA010", "5MA016",
        "6MA008", "6MA009", "6MA011", "6MA012", "6MA017"],
    "BEng (Hons) Automotive Engineering": [
        "4MA007", "4MA008", "4MA013", "4MA014", "4MA015", "5MA005", "5MA006", "5MA007", "5MA017", "5MA018", "6MA010",
        "6MA011", "6MA019", "6MA020", "6MA017"],
    "BEng (Hons) Electronics and Telecommunications Engineering": [
        "4MA007", "4MA008", "4MA020", "4MA022", "4MA021", "5MA019", "5MA021", "5MA022", "5MA023", "5MA020", "5MA016",
        "6MA011", "6MA021", "6MA022", "6MA023", "6MA017""4MA007", "4MA008", "4MA020", "4MA022", "4MA021", "5MA019",
        "5MA021", "5MA022", "5MA023", "5MA020", "5MA016", "6MA011", "6MA021", "6MA022", "6MA023", "6MA017"],
    "BEng (Hons) Mechanical Engineering": [
        "4MA007", "4MA008", "4MA017", "4MA018", "4MA016", "5MA006", "5MA008", "5MA013", "5MA014", "5MA011", "6MA011",
        "6MA014", "6MA016", "6MA018", "6MA017"],
    "BEng (Hons) Mechatronics Engineering": [
        "4MA007", "4MA008", "4MA017", "4MA020", "4MA021", "5MA013", "5MA019", "5MA021", "5MA023", "5MA020", "5MA016",
        "6MA011", "6MA021", "6MA025", "6MA026", "6MA017"],
    "BEng (Hons) Motorsport Engineering": [
        "4MA007", "4MA008", "4MA014", "4MA019", "4MA015", "5MA005", "5MA006", "5MA007", "5MA015", "5MA012", "6MA010",
        "6MA011", "6MA015", "6MA013", "6MA017"],
    "MEng (Hons) Aerospace Engineering": [
        "4MA007", "4MA008", "4MA009", "4MA010", "4MA011", "5MA005", "5MA006", "5MA007", "5MA009", "5MA010", "5MA016",
        "6MA008", "6MA009", "6MA011", "6MA012", "6MA017", "7MA004", "7MA005", "7MA006", "7MA010", "7MA012""4MA007",
        "4MA008", "4MA009", "4MA010", "4MA011", "5MA005", "5MA006", "5MA007", "5MA009", "5MA010", "5MA016", "6MA008",
        "6MA009", "6MA011", "6MA012", "6MA017", "7MA004", "7MA005", "7MA006", "7MA010", "7MA012"],
    "MEng (Hons) Automotive Engineering": [
        "4MA007", "4MA008", "4MA013", "4MA014", "4MA015", "5MA005", "5MA006", "5MA007", "5MA017", "5MA018", "6MA010",
        "6MA011", "6MA019", "6MA020", "6MA017", "7MA005", "7MA006", "7MA007", "7MA010", "7MA012"],
    "MEng (Hons) Electronic and Telecommunications Engineering": [
        "4MA007", "4MA008", "4MA020", "4MA022", "4MA021", "5MA019", "5MA021", "5MA022", "5MA023", "5MA020", "5MA016",
        "6MA011", "6MA021", "6MA022", "6MA023", "6MA017", "7MA011", "7MA015", "7MA016", "7MA017", "7MA012"],
    "MEng (Hons) Mechanical Engineering": [
        "4MA007", "4MA008", "4MA017", "4MA018", "4MA016", "5MA006", "5MA008", "5MA013", "5MA014", "5MA011", "6MA018",
        "6MA016", "6MA011", "6MA014", "6MA017", "7MA010", "7MA011", "7MA012", "7MA013", "7MA018"],
    "MEng (Hons) Mechatronics Engineering": [
        "4MA007", "4MA008", "4MA017", "4MA020", "4MA021", "5MA013", "5MA019", "5MA021", "5MA023", "5MA020", "5MA016",
        "6MA011", "6MA021", "6MA025", "6MA026", "6MA017", "7MA011", "7MA014", "7MA016", "7MA017", "7MA012"],
    "MEng (Hons) Motorsport Engineering": [
        "4MA007", "4MA008", "4MA014", "4MA019", "4MA015", "5MA005", "5MA006", "5MA007", "5MA015", "5MA012", "6MA010",
        "6MA011", "6MA013", "6MA015", "6MA017", "7MA006", "7MA007", "7MA009", "7MA010", "7MA012"],
    "MSc Advanced Technology Management (Engineering Analysis)": [
        "7ET022", "7CM002", "7AT004", "7CM003", "7CM001", "7ET032", "7ET023"],
    "MSc Advanced Technology Management (Manufacturing)": [
        "7ET022", "7CM002", "7ET019", "7CM003", "7AT004", "7ET020",
        "7ET023"],
    "MSc Advanced Technology Management (Sustainability)": [
        "7ET022", "7CM002", "7CM004", "7CM003",
        "7AT004", "7ET026", "7ET023"],
    "MSc Manufacturing Engineering": [
        "7ET022", "7CM004", "7ET019", "7MA001", "7AT004", "7CM003", "7ET023"],
    "Postgraduate Certificate Manufacturing Engineering": [
        "7ET019", "7AT004", "7MA001"],
    "BSc (Hons) Computer Science with Secondary Education (QTS)": [
        "4CS001", "4CS015", "4CI018", "4CS014", "4CS016", "4SE001", "5CS019", "5CS021", "5CI022", "5SE001", "5SE002",
        "5CS016", "5CS028", "6CS020", "6SE007", "6SE008", "6CS014"],
    "BSc (Hons) Industrial Mathematics": [
        "4MM001", "4MM009", "4MM010", "4MM002", "4MM003", "4MM004", "5ET005", "5ET009", "5MM001", "5MM012", "5MM013",
        "5MM003", "5MM009", "6ET006", "6MM014", "6MM003", "6ET002", "6MM012", "6MM013", "6MM010", "6MM002"],
    "BSc (Hons) Mathematics with Secondary Education (QTS)": [
        "4MM001", "4MM002", "4MM010", "4MM004", "4MM003", "4MM009", "4SE001", "5MM001", "5MM011", "5MM012", "5SE001",
        "5SE002", "5MM003", "5SE003", "6MM003", "6MM011", "6MM014", "6SE007", "6SE008"],
    "BSc(Hons) Business Intelligence": [
        "4CS001", "4CS015", "4CI018", "4CS014", "4MM015", "4CI017", "5CI021", "5CI022", "5CS030", "5CS024", "5MM014",
        "5MM015", "6CS019", "6CS005", "6MM017", "6CS012", "6MM016"],
    "BSc(Hons) Cloud Computing": [
        "4CS001", "4CS015", "4CI018", "4CS014", "4CS012", "4CS016", "5CS032", "5CI022", "5CS030", "5CS022", "5CS031",
        "5CS024", "5CS016", "6CS023", "6CS026", "6CS005", "6CS030", "6CS029"],
    "BSc(Hons) Computer Science":
        ["4CS001", "4CS015", "4CI018", "4CS014", "4MM013", "4CS016",
         "5CS019", "5CS021", "5CI022", "5CS022", "5CS020", "5CS024", "5CS016",
         "6CS014", "6CS005", "6CS012", "6CS001", "6CS007", "6CS008", "6CS003"],

    "BSc(Hons) Computer Science (Games Development)":
        ["4CS001", "4CS015", "4CI018", "4CS014", "4MM013", "4CS016",
         "5CS019", "5CS021", "5CS025", "5CS027", "5CS020", "5CS024", "5CS016",
         "6CS013", "6CS004", "6CS005", "6CS001", "6CS012", "6CS007"],

    "BSc(Hons) Computer Science (Software Engineering)":
        ["4CS001", "4CS015", "4CI018", "4CS014", "4MM013", "4CS016",
         "5CS019", "5CS021", "5CI022", "5CS022", "5CS020", "5CS024",
         "5CS016", "6CS001", "6CS005", "6CS002", "6CS027", "6CS017"],
}

extra = {"BSc(Hons) Business Intelligence": [
    "4CS001", "4CS015", "4CI018", "4CS014", "4MM015", "4CI017", "5CI021", "5CI022", "5CS030", "5CS024", "5MM014",
    "5MM015", "6CS019", "6CS005", "6MM017", "6CS012", "6MM016"],
    "BSc(Hons) Cloud Computing": [
        "4CS001", "4CS015", "4CI018", "4CS014", "4CS012", "4CS016", "5CS032", "5CI022", "5CS030", "5CS022", "5CS031",
        "5CS024", "5CS016", "6CS023", "6CS026", "6CS005", "6CS030", "6CS029"],
    "BSc(Hons) Computer Science":
        ["4CS001", "4CS015", "4CI018", "4CS014", "4MM013", "4CS016",
         "5CS019", "5CS021", "5CI022", "5CS022", "5CS020", "5CS024", "5CS016",
         "6CS014", "6CS005", "6CS012", "6CS001", "6CS007", "6CS008", "6CS003"],

    "BSc(Hons) Computer Science (Games Development)":
        ["4CS001", "4CS015", "4CI018", "4CS014", "4MM013", "4CS016",
         "5CS019", "5CS021", "5CS025", "5CS027", "5CS020", "5CS024", "5CS016",
         "6CS013", "6CS004", "6CS005", "6CS001", "6CS012", "6CS007"],

    "BSc(Hons) Computer Science (Software Engineering)":
        ["4CS001", "4CS015", "4CI018", "4CS014", "4MM013", "4CS016",
         "5CS019", "5CS021", "5CI022", "5CS022", "5CS020", "5CS024",
         "5CS016", "6CS001", "6CS005", "6CS002", "6CS027", "6CS017"],
}


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
                    dt = datetime(year=d.year, month=d.month, day=d.day,
                                  hour=t.tm_hour, minute=t.tm_min)
                    print(activity + ": " + dt.strftime('%d %b %Y %I:%M%p'))

            # Single week e.g. 6
            else:
                week_number = int(week_range)
                d = get_date_by_week_number(week_number, day)
                t = time.strptime(start_time, "%H:%M")
                dt = datetime(year=d.year, month=d.month, day=d.day,
                              hour=t.tm_hour, minute=t.tm_min)
                print(activity + ": " + dt.strftime('%d %b %Y %I:%M%p'))


def print_next_activity(module_code):
    print("Next activity for " + module_code + ": ")

    now = datetime.now()
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
                    dt = datetime(year=d.year, month=d.month, day=d.day,
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
                dt = datetime(year=d.year, month=d.month, day=d.day,
                              hour=t.tm_hour, minute=t.tm_min)

                if dt > now:
                    print("\t" + activity + ": " + dt.strftime('%d %b %Y %I:%M%p'))
                    return


def import_modules_peewee(courses):
    for course_name, module_codes in courses.items():

        # Save each course
        course = Course.create(name=course_name)
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

            if not is_new_module:
                continue

            for index, row in timetables.iterrows():
                timetable = Timetable.create(module=module, activity=row["Activity"], day=row['Day'],
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
                        start = int(start_and_end[0])
                        end = int(start_and_end[1])

                        start_week = get_date_by_week_number(start, day)
                        end_week = get_date_by_week_number(end, day)

                    # Single week e.g. 6
                    else:
                        week_number = int(week_range)
                        start_week = end_week = get_date_by_week_number(week_number, day)

                    Week_Range.create(timetable=timetable, start_week=start_week, end_week=end_week)


def get_module_codes(url):
    r = requests.get(url, stream=True)

    with open("temp/temp.pdf", 'wb') as f:
        f.write(r.content)

    file = open("temp/temp.pdf", 'rb')
    parser = PDFParser(file)
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
                        return module_codes

                    if not first:
                        print(",", end=''),
                    else:
                        first = False

                    print("\"" + text + "\"", end=''),
                    # module_codes.append(text)

    document = None
    gc.collect()
    os.remove("temp/temp.pdf")
    return module_codes


def get_timetables():
    file = open("temp/Faculty of Science and Engineering.html")

    page = BeautifulSoup(file, "html.parser")
    list_items = page.find_all("li")

    course_modules = {}

    for child in list_items:
        pdf_url = child.find("a", href=True)["href"]
        if "Sandwich" not in child.string \
                and "Foundation" not in child.string \
                and "Top-up" not in child.string:
            print("\"" + child.string + "\": [")
            try:
                get_module_codes(pdf_url)
            except:
                pass


import_modules_peewee(extra)
# get_timetables()
print("done")
