import configparser

class ConfigParse(object):
    def __init__(self, arg):
        self.info = {"name": "configparse",
                     "author": "und3rf10w"}
        super(ConfigParse, self).__init__()

        self.config_file = arg

    def init(self):
        config = configparser.ConfigParser()
        config.read(self.config_file)
