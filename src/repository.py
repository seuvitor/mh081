LIB_DIR = '../lib'

import sys
from os.path import abspath
sys.path.append(abspath(LIB_DIR))

import dbconfig
from core import *

def initialize_persistence():
    
    # Define object-relational mappings
    from sqlalchemy.orm import mapper, relation
    import dbmodel
    mapper(Student, dbmodel.students_table, properties={\
            'events':relation(Event, secondary=dbmodel.event_students)})
    mapper(Event, dbmodel.events_table, properties={\
            'students':relation(Student, secondary=dbmodel.event_students),
            'features':relation(Feature, secondary=dbmodel.event_features)})
    mapper(Room, dbmodel.rooms_table, properties={\
            'features':relation(Feature, secondary=dbmodel.room_features)})
    mapper(Feature, dbmodel.features_table)

    # Configure database connection
    global engine
    from sqlalchemy import create_engine
    engine = create_engine(dbconfig.DB_URI, echo=False)
    
    # Define Session class
    global Session
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=engine, autoflush=True, transactional=True)


def populate_database():
    
    from sqlalchemy.exceptions import IntegrityError
    try:
        session = Session()
        
        num_students = 3
        num_events = 8
        num_rooms = 2
        num_features = 1
        
        # Create objects
        students = [Student(str(id), 'John Nobody #' + str(id)) for id in range(num_students)]
        events = [Event(str(id), 'Event #' + str(id)) for id in range(num_events)]
        rooms = [Room(str(id), 3) for id in range(num_rooms)]
        features = [Feature(str(id), 'Feature #' + str(id)) for id in range(num_features)]
        
        # Save objects to the persistence
        for i in range(num_students): session.save(students[i])
        for i in range(num_events): session.save(events[i])
        for i in range(num_rooms): session.save(rooms[i])
        for i in range(num_features): session.save(features[i])
        
        # Set relationships
        students[0].events.append(events[0])
        students[0].events.append(events[1])
        students[0].events.append(events[2])
        students[1].events.append(events[3])
        students[1].events.append(events[4])
        students[1].events.append(events[5])
        students[2].events.append(events[5])
        students[2].events.append(events[6])
        students[2].events.append(events[7])
        
        rooms[0].features.append(features[0])
        
        events[0].features.append(features[0])
        events[4].features.append(features[0])
        events[7].features.append(features[0])
        
        session.commit()
    except IntegrityError:
        print "IntegrityError when populating. The database remains unchanged."


def get_students():
    from sqlalchemy.orm import eagerload
    session = Session()
    query = session.query(Student).options(eagerload('events'))
    return [student for student in query]


def get_events():
    from sqlalchemy.orm import eagerload
    session = Session()
    query = session.query(Event).options(eagerload('students'), eagerload('features'))
    return [event for event in query]


def get_event(event_id):
    from sqlalchemy.orm import eagerload
    session = Session()
    event = session.query(Event).get(event_id)
    return event


def get_rooms():
    from sqlalchemy.orm import eagerload
    session = Session()
    query = session.query(Room).options(eagerload('features'))
    return [room for room in query]


def get_features():
    session = Session()
    return [feature for feature in session.query(Feature)]


def add_student(id):
    session = Session()
    session.save(Student(id))
    session.commit()


def main():
    
    if (raw_input("create tables? ").strip() == "yes"):
        dbconfig.metadata.drop_all(engine)
        dbconfig.metadata.create_all(engine)

    if (raw_input("populate tables? ").strip() == "yes"):
        populate_database()

    for student in get_students():
        print student, 'events:', student.events
    for event in get_events():
        print event, 'students:', event.students, 'features:', event.features
    for room in get_rooms():
        print room, 'features:', room.features
    for feature in get_features():
        print feature


initialize_persistence()

if __name__ == "__main__":
    main()
