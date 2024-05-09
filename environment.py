class Value:
    def __init__(self, value, type, writeable=True):
        self.value = value
        self.type = type
        self.writeable = writeable

    def __str__(self):
        return 'value: ' + str(self.value) + ' type: ' + str(self.type) + ' writeable: ' + str(self.writeable)
    
    def __repr__(self):
        return str(self)

class Environment:
    def __init__(self, parent=None):
        self.parent = parent
        self.vars = {}

    def __contains__(self, name):
        if name in self.vars:
            return True
        elif self.parent:
            return name in self.parent
        else:
            return False

    def __getitem__(self, name):
        if name in self.vars:
            return self.vars[name]
        elif self.parent:
            return self.parent[name]
        else:
            return None
    
    def __setitem__(self, name, value):
        env = self
        while env.parent and name not in env.vars:
            env = env.parent
        
        env.vars[name] = value
    
    def define_local(self, name, value):
        self.vars[name] = value

    def push(self):
        return Environment(self)
    
    def pop(self):
        return self.parent

    def __str__(self):
        if self.parent:
            return str(self.parent) + str(self.vars)
        else:
            return str(self.vars)