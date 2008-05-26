class Student(object):
    
    def __init__(self, id, name):
        self.id = id
        self.name = name
    
    def __repr__(self):
        return "<Student('%s', '%s')>" % (self.id, self.name)


class Event(object):
    
    def __init__(self, id, description):
        self.id = id
        self.description = description
    
    def __repr__(self):
        return "<Event('%s', '%s')>" % (self.id, self.description)


class Room(object):
    
    def __init__(self, id, capacity):
        self.id = id
        self.capacity = capacity
    
    def __repr__(self):
        return "<Room('%s', '%i')>" % (self.id, self.capacity)


class Feature(object):
    
    def __init__(self, id, description):
        self.id = id
        self.description = description
    
    def __repr__(self):
        return "<Feature('%s', '%s')>" % (self.id, self.description)
