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

        # TODO: This is dumb, make this part of the global config
        self.authstring = "5243654tgbrhebs-tgr5ehjntdhyu563whtaghw65hrtagr.g5h7e6w5hert63"

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

        if base64.b64decode(authstring).decode("utf-8") == teamserver.teamserver.authstring:
            teamserver.logging.log(f"Authenticated {data['username']} from {flask.request.remote_addr}",
                             source=f"{teamserver.teamserver.info['name']}")
            success = True
            return "login_ok"
        else:
            error = False
            return "login_failed"

    def start_teamserver(self, *args):
        global teamserver

        teamserver = args[0]

        try:
            app.run(host=teamserver.addr, port=teamserver.port)
        except Exception as e:
            teamserver.logging.log(f"Critical error when starting teamserver api server", level="critical",
                             source=f"{teamserver.teamserver.info['name']}")
            exit()