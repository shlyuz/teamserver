#!/usr/bin/env python3

import asyncio
import ssl
import argparse
from threading import Thread

from lib import teamserver
from lib import logging
from lib import banner
from lib import configparse


class Shlyuz(object):
    def __init__(self, args):
        """
        Initializes Shlyuz

        :param args: arguments received via main argument parser
        """
        super(Shlyuz, self).__init__()

        # Declare our variables to run
        self.logging = logging.Logging(args['debug'])
        self.logging.log("Starting Shlyuz")

        # Load our config
        self.logging.log(f"Loading Shlyuz config from {args['config']}", level='debug')
        # self.config = configparse.ConfigParse(args['config']) #TODO: Reenable me
        self.logging.log(f"Loaded Shlyuz config", level='debug')

        # framework vars
        self.variables = {}

        # callback endpoint
        # self.callback = args['callback'] #TODO: Implement me

        # Implant runtime vars
        self.implants = {}
        self.implant_count = len(self.implants)
        self.current_implant = None

        # Listener runtime vars
        self.listeners = {}
        self.listener_count = len(self.listeners)
        self.current_listener = None

    # Not currently used
    # def start(self):
    # shlyuz = Shlyuz(args)
    # TODO: Start the listener interaction thread(s)
    # Gotta figure out how this is gonna work first
    # Plan is to start listener interactions, gather metadata from them (about the state of the implants), \
    # then start the console, which after the banner prints but before the console starts should print info about \
    # the current state of the entire shlyuz framework

    # TODO: Print stats from the listener manifests


class Shlyuz_Teamserver(object):
    def __init__(self, args):
        super(Shlyuz_Teamserver, self).__init__()

        self.config = args['config']
        self.logging = logging.Logging(args['debug'])
        self.logging.log("Starting Shlyuz Teamserver", source="teamserver_init")
        self.addr = args['address']
        self.port = args['port']

        self.logging.log("Starting Shlyuz teamserver flask thread", level="debug")
        self.teamserver = teamserver.Teamserver(self)

    def start(self):
        """
        Start up for Shlyuz server, received manifests from listener, prints the banner, and start console_host listener thread

        :return:
        """

        # start banner
        banner.Banner()

        # Teamserver class init

        # Start the teamserver
        # asyncio.run(self.teamserver.start(self.logging))

        teamserver_thread = Thread(target=self.teamserver.start_teamserver, args=(self,))
        teamserver_thread.daemon = True
        teamserver_thread.start()
        self.logging.log("Started Shlyuz teamserver")

        # Create our teamserver object
        self.shlyuz = Shlyuz(args)

        # Give shlyuz and instance of the teamserver
        self.shlyuz.teamserver = self

        while True:
            pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='shlyuz')
    parser.add_argument("-a", "--address", required=False, default="0.0.0.0", help="Address to listen on")
    parser.add_argument("-p", "--port", required=False, default=8080, help="Port to bind to")
    parser.add_argument("-d", "--debug", required=False, default=False, action="store_true",
                        help="Enable debug logging")
    parser.add_argument("-c", "--config", required=False, default="config/shlyuz.conf",
                        help="Path to configuration file")

    # parse the args
    args = vars(parser.parse_args())

    shlyuz_teamserver = Shlyuz_Teamserver(args)
    # shlyuz.start() # not currently used
    shlyuz_teamserver.start()
