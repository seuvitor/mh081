from sqlalchemy import Table, Column, Integer, ForeignKey
import dbconfig

students_table = Table("students", dbconfig.metadata,\
        Column("id", Integer, primary_key=True))

events_table = Table("events", dbconfig.metadata,\
        Column("id", Integer, primary_key=True))

rooms_table = Table("rooms", dbconfig.metadata,\
        Column("id", Integer, primary_key=True),
        Column("capacity", Integer))

features_table = Table("features", dbconfig.metadata,\
        Column("id", Integer, primary_key=True))

event_features = Table('event_features', dbconfig.metadata,\
        Column('event_id', Integer, ForeignKey('events.id')),\
        Column('feature_id', Integer, ForeignKey('features.id')))

room_features = Table('room_features', dbconfig.metadata,\
        Column('room_id', Integer, ForeignKey('rooms.id')),\
        Column('feature_id', Integer, ForeignKey('features.id')))

event_students = Table('event_students', dbconfig.metadata,\
        Column('event_id', Integer, ForeignKey('events.id')),\
        Column('student_id', Integer, ForeignKey('students.id')))