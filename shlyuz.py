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
        self.addr = args['address']
        self.port = args['port']
        self.logging = logging.Logging(args['debug'])
        self.logging.log("Starting Shlyuz teamserver")

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

        # Console class init
        self.teamserver = teamserver.Teamserver(self.logging)

    def start(self):
        """
        Start up for Shlyuz server, received manifests from listener, prints the banner, and start console_host listener thread

        :return:
        """
        shlyuz = Shlyuz(args)

        # start banner
        banner.Banner()

        # TODO: Start the listener interaction thread(s)
        # Gotta figure out how this is gonna work first
        # Plan is to start listener interactions, gather metadata from them (about the state of the implants), \
        # then start the console, which after the banner prints but before the console starts should print info about \
        # the current state of the entire shlyuz framework

        # TODO: Print stats from the listener manifests

        # Start the teamserver
        # asyncio.run(self.teamserver.start(self.logging))
        self.logging.log("Starting Shlyuz teamserver flask thread", level="debug")
        teamserver_thread = Thread(target=self.teamserver.start_teamserver, args=(shlyuz,))
        teamserver_thread.daemon = True
        teamserver_thread.start()
        self.logging.log("Started Shlyuz teamserver")

        while True: pass




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

    shlyuz = Shlyuz(args)
    shlyuz.start()
