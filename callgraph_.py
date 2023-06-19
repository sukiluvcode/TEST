class BeingRevoked:
    def do_something(self):
        print("do something")

class Revoke:
    def __init__(self, cls):
        cls().do_something()

revoke = Revoke(BeingRevoked)