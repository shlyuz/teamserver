#!/usr/bin/env python3
import asyncio
import argparse
from threading import Thread
import ast

from lib import teamserver
from lib import logging
from lib import banner
from lib import configparse
from lib import listener
from lib import common
from lib.crypto import asymmetric


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
        self.version = common.VERSION

        # Load our config
        self.logging.log(f"Loading Shlyuz config from {args['config']}", level='debug')
        self.config = configparse.ConfigParse(args['config'])
        self.logging.log(f"Loaded Shlyuz config", level='debug')

        # framework vars
        self.variables = {}

        # callback endpoint
        # self.callback = args['callback'] #TODO: Implement me if we're gonna use this... Likely not


class ShlyuzTeamserver(object):
    def __init__(self, args):
        super(ShlyuzTeamserver, self).__init__()

        self.logging = logging.Logging(args['debug'])
        self.logging.log("Starting Shlyuz Teamserver", source="teamserver_init")
        self.config = args['config']['teamserver']
        self.http_addr = self.config['http_addr']
        self.http_port = self.config['http_port']

        # Crypto values
        self.initial_private_key = asymmetric.private_key_from_bytes(args['config']['crypto']['private_key'])
        self.initial_public_key = self.initial_private_key.public_key
        self.xor_key = ast.literal_eval(args['config']['crypto']['xor_key'])

        # Teamserver Queues
        self.cmd_queue = []

        # Implant runtime vars
        self.implants = []
        self.implant_count = len(self.implants)

        # Listener runtime vars
        self.listeners = []
        self.listener_count = len(self.listeners)
        # DEBUG TODO: REmove me
        self.lp_pubkey = asymmetric.public_key_from_bytes(args['config']['listening_post_f35dead2cae04a6d975598153ae9a251']['pubkey'])

        # Starts the listener socket
        self.logging.log("Starting Shlyuz teamserver listener socket", level="debug", source="teamserver_init")
        self.listener_thread = listener.start_management_socket(self)
        self.logging.log("Started Shlyuz teamserver listener socket", level="debug", source="teamserver_init")

        self.logging.log("Starting Shlyuz teamserver flask thread", level="debug")
        self.teamserver = teamserver.Teamserver(self)
        self.teamserver_thread = None

    def add_instruction_to_cmd_queue(self, instruction_frame):
        """
        Takes an instruction frame and adds it to the cmd_queue. Assigns a state of 'processing' to
        the instruction_frame
        :param instruction_frame: a raw instruction frame
        :return:
        """
        instruction_frame['state'] = "processing"
        self.cmd_queue.append(instruction_frame)

    async def get_manifests(self):
        # TODO: Remove me
        # DEBUG
        self.listeners = []
        return self.listeners

    async def gather_manifests(self):
        await asyncio.gather(self.get_manifests())

    # TODO: Implement me
    # TODO: Start the listener interaction thread(s)
    # Gotta figure out how this is gonna work first
    # Plan is to start listener interactions, gather metadata from them (about the state of the implants), \
    # then start the console, which after the banner prints but before the console starts should print info about \
    # the current state of the entire shlyuz framework

    # TODO: listener socket interaction loop
    #  * Send out manifest requests to configured listening posts
    #  * As responses are returned, update self.listeners with the manifests
    #  * As listener manifests are returned, extract implant manifests, update self.listeners with the manifests
    #  * Now you have a map of implant -> listening_post which can be cross references against self.listeners and \
    #    self.implants
    #  * async loop to periodically update self.implant_count and self.listener_count
    #  * Let the listener interaction socket continue

    # TODO: Print stats from the listener manifests
    def print_stats(self):
        # TODO: Implement me
        print(self.listeners)
        print(self.implants)

    def start(self):
        """
        Start up for Shlyuz server, received manifests from listener, prints the banner, and start console_host listener thread

        :return:
        """

        # start banner
        banner.Banner()

        # Teamserver class init
        # Create our teamserver object  # TODO: Not used
        # self.shlyuz = Shlyuz(args)

        # Start our input handler
        # self.handler = handler.Handler(self.shlyuz) # TODO: Not used

        # Get the manifest(s) from the listening post(s)
        # asyncio.run(self.get_manifests())

        self.teamserver_thread = Thread(target=self.teamserver.start_teamserver, args=(self,))
        self.teamserver_thread.daemon = True
        self.teamserver_thread.start()
        self.logging.log("Started Shlyuz teamserver", level="debug", source="teamserver_start")
        self.teamserver.status = "STARTED"

        # TODO: logic here to retrieve listening post manifests
        self.logging.log("Retrieving listening post manifests")
        # self.get_manifests()  # TODO: Make me async, possibly assign my output as an attribute
        # asyncio.run(self.gather_manifests())

        # TODO: Logic here to output and update stats about environment from listener manifests
        # self.print_stats()

        # TODO: Logic here to start the async jobs to process stuff as it comes into the listener channel

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
    shlyuz_teamserver = ShlyuzTeamserver(args)
    shlyuz_teamserver.start()
