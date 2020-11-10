#!/usr/bin/env python3

import asyncio
import ssl
import argparse
from threading import Thread

from lib import teamserver
from lib import logging
from lib import banner
from lib import configparse
from lib import handler
from lib import networking


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
        self.config = configparse.ConfigParse(args['config'])
        self.logging.log(f"Loaded Shlyuz config", level='debug')

        # framework vars
        self.variables = {}

        # callback endpoint
        # self.callback = args['callback'] #TODO: Implement me if we're gonna use this... Likely not


class Shlyuz_Teamserver(object):
    def __init__(self, args):
        super(Shlyuz_Teamserver, self).__init__()

        self.logging = logging.Logging(args['debug'])
        self.logging.log("Starting Shlyuz Teamserver", source="teamserver_init")
        self.config = args['config']['teamserver']
        self.http_addr = self.config['http_addr']
        self.http_port = self.config['http_port']

        # Implant runtime vars
        self.implants = {}
        self.implant_count = len(self.implants)
        self.current_implant = None  # used for operator console

        # Listener runtime vars
        self.listeners = {}
        self.listener_count = len(self.listeners)
        self.current_listener = None  # used for operator console

        # Starts the listener socket
        self.logging.log("Starting Shlyuz teamserver listener socket", level="debug", source="teamserver_init")
        self.listener_socket = networking.listen_on_listener_socket(self.config['l_addr'], self.config['l_port'])

        self.logging.log("Starting Shlyuz teamserver flask thread", level="debug")
        self.teamserver = teamserver.Teamserver(self)

    async def get_manifests(self):
        return 0  # TODO: Remove me
        # shlyuz = Shlyuz(args)
        # TODO: Start the listener interaction thread(s)
        # Gotta figure out how this is gonna work first
        # Plan is to start listener interactions, gather metadata from them (about the state of the implants), \
        # then start the console, which after the banner prints but before the console starts should print info about \
        # the current state of the entire shlyuz framework

        # TODO: Start listener interaction socket
        #  * Send out manifest requests to configured listening posts
        #  * As responses are returned, update self.listeners with the manifests
        #  * As listener manifests are returned, extract implant manifests, update self.listeners with the manifests
        #  * Now you have a map of implant -> listening_post which can be cross references against self.listeners and \
        #    self.implants
        #  * async loop to periodically update self.implant_count and self.listener_count
        #  * Let the listener interaction socket continue

    # TODO: Print stats from the listener manifests

    def start(self):
        """
        Start up for Shlyuz server, received manifests from listener, prints the banner, and start console_host listener thread

        :return:
        """

        # start banner
        banner.Banner()

        # Teamserver class init
        # Create our teamserver object
        self.shlyuz = Shlyuz(args)

        # Start our input handler
        self.handler = handler.Handler(self.shlyuz)

        # Get the manifest(s) from the listening post(s)
        # asyncio.run(self.get_manifests())

        teamserver_thread = Thread(target=self.teamserver.start_teamserver, args=(self,))
        teamserver_thread.daemon = True
        teamserver_thread.start()
        self.logging.log("Started Shlyuz teamserver")

        # Give shlyuz an instance of the teamserver
        self.shlyuz.teamserver = self

        # TODO: logic here to retrieve listening post manifests
        self.logging.log("Retrieving listening post manifests")

        # TODO: Logic here to output and update stats about environment from listener manifests

        while True:
            pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='shlyuz')
    parser.add_argument("-d", "--debug", required=False, default=False, action="store_true",
                        help="Enable debug logging")
    parser.add_argument("-c", "--config", required=False, default="config/shlyuz.conf",
                        help="Path to configuration file")

    # parse the args
    args = vars(parser.parse_args())

    global shlyuz
    shlyuz = Shlyuz(args)  # not currently used
    args['config'] = shlyuz.config.config
    shlyuz_teamserver = Shlyuz_Teamserver(args)
    shlyuz_teamserver.start()
