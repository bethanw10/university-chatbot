import os

from peewee import *

package_dir = os.path.dirname(os.path.abspath(__file__))
database_path = os.path.join(package_dir, 'data/db.sqlite')
db = SqliteDatabase(database_path)


class BaseModel(Model):
    class Meta:
        database = db


class Course(BaseModel):
    name = CharField(unique=True)


class Module(BaseModel):
    name = CharField()
    code = CharField(unique=True)
    semester = CharField()

    class Meta:
        database = db


class Course_Module(BaseModel):
    course = ForeignKeyField(Course)
    module = ForeignKeyField(Module)


class Timetable(BaseModel):
    module = ForeignKeyField(Module)
    activity = CharField()
    day = CharField()
    start = CharField()
    finishes = CharField()
    campus = CharField()
    room = CharField()
    lecturer = CharField()
    group_details = CharField()


class Week_Range(BaseModel):
    timetable = ForeignKeyField(Timetable)
    start_week = CharField()
    end_week = CharField()


def create_tables():
    db.connect()
    db.create_tables([Course, Course_Module, Module, Timetable, Week_Range])


print(database_path)
print(db.get_tables())
