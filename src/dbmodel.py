from sqlalchemy import Table, Column, Integer, String, ForeignKey, Sequence
import dbconfig

students_table = Table("students", dbconfig.metadata,\
        Column("id", String(10), primary_key=True),
        Column("name", String(100)))

events_table = Table("events", dbconfig.metadata,\
        Column("id", String(10), primary_key=True),
        Column("description", String(100)))

rooms_table = Table("rooms", dbconfig.metadata,\
        Column("id", String(10), primary_key=True),
        Column("capacity", Integer))

features_table = Table("features", dbconfig.metadata,\
        Column("id", String(10), primary_key=True),
        Column("description", String(100)))

event_features = Table('event_features', dbconfig.metadata,\
        Column('event_id', String(10), ForeignKey('events.id')),\
        Column('feature_id', String(10), ForeignKey('features.id')))

room_features = Table('room_features', dbconfig.metadata,\
        Column('room_id', String(10), ForeignKey('rooms.id')),\
        Column('feature_id', String(10), ForeignKey('features.id')))

event_students = Table('event_students', dbconfig.metadata,\
        Column('event_id', String(10), ForeignKey('events.id')),\
        Column('student_id', String(10), ForeignKey('students.id')))