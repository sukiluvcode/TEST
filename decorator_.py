class Counts:
    def __init__(self, func):
        self.func = func
        self.count = 0

    def __call__(self, *args, **kargs):
        self.count += 1
        return self.func(*args, **kargs)
