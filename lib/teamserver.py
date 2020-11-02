import base64
import asyncio
import flask

loop = asyncio.get_event_loop()
app = flask.Flask(__name__)


class Teamserver(object):
    def __init__(self, arg):
        self.info = {"name": "teamserver",
                     "author": "und3rf10w"
                     }
        super(Teamserver, self).__init__()

    @app.route("/")
    def teamserver_base():
        teamserver.logging.log("hit on /", source="teamserver")
        return "Попрешь на крутых, уроем как остальных"

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

        response = {"success": success, "error": error }
        if success and username:
            response['username'] = username
            auth_cookie = base64.b64encode(f"{username} `|` {authstring}".encode('utf-8'))

        res = flask.make_response(flask.jsonify(response))
        if success: res.set_cookie('Auth', auth_cookie)
        return res

    @app.route("/cmd", methods=["POST"])
    def teamserver_run_cmd():
        """
        Run a command on an implant

        :return:
        """

        error = False
        success = False

        response = {"success": False}

        # Get the cookie
        try:
            cookie = flask.request.cookies.get("Auth")
            username, recv_authstring = base64.b64decode(cookie).decode('utf-8').split(" `|` ")
            if base64.b64decode(recv_authstring).decode("utf-8") == teamserver.config['authstring']:
                # Process the command
                data = flask.request.get_json(force=True)
                teamserver.logging.log(f"Received {data['cmd']}, from {username}, for implant {data['id']}",
                                       level="debug", source=f"{teamserver.teamserver.info['name']}")
                teamserver.config()

            else:
                # Our auth string didn't match
                error = True
        except Exception:
            error = True

        return response

    def validate_cookie(self, cookie):
        print(cookie)


    def start_teamserver(self, *args):
        global teamserver

        teamserver = args[0]

        try:
            app.run(host=teamserver.addr, port=teamserver.port)
        except Exception as e:
            teamserver.logging.log(f"Critical error when starting teamserver api server", level="critical",
                             source=f"{teamserver.teamserver.info['name']}")
            exit()