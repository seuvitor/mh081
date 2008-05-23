class Student(object):
    
    def __init__(self, id):
        self.id = id
    
    def __repr__(self):
        return "<Student('%i')>" % (self.id)


class Event(object):
    
    def __init__(self, id):
        self.id = id
    
    def __repr__(self):
        return "<Event('%i')>" % (self.id)


class Room(object):
    
    def __init__(self, id, capacity):
        self.id = id
        self.capacity = capacity
    
    def __repr__(self):
        return "<Room('%i', '%i')>" % (self.id, self.capacity)


class Feature(object):
    
    def __init__(self, id):
        self.id = id
    
    def __repr__(self):
        return "<Feature('%i')>" % (self.id)
