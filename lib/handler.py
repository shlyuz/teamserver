from threading import Thread
import pickle

class Handler(object):
    def __init__(self, shlyuz):
        super(Handler, self).__init__()
        self.shlyuz = shlyuz

    async def do (self, cmd, implant):
        # This is where we would do the actual command
        return "Sent message to LP"