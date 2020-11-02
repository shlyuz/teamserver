import configparser

class ConfigParse(object):
    def __init__(self, config_file):
        self.info = {"name": "configparse",
                     "author": "und3rf10w"}
        super(ConfigParse, self).__init__()

        self.config = self.read_config(config_file)

    def read_config(self, config_file):
        config = configparser.ConfigParser()
        config.read(config_file)
        return config
