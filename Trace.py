class Trace:
    def __init__(self, name, name_short, axis, key, id, unit):
        self.name = name
        self.name_short = name_short
        self.unit = unit
        self.axis = axis
        self.key = key
        self.id = id
        self.values = []

    def setValues(self, values):
        self.values = values
