import base64
import asyncio
import flask

loop = asyncio.get_event_loop()
app = flask.Flask(__name__)


class Teamserver(object):
    def __init__(self, logger):
        self.info = {"name": "teamserver",
                     "author": "und3rf10w"
                     }
        super(Teamserver, self).__init__()

        self.logging = logger
        # TODO: This is dumb, make this part of the global config
        self.authstring = "5243654tgbrhebs-tgr5ehjntdhyu563whtaghw65hrtagr.g5h7e6w5hert63"

    @app.route("/")
    def teamserver_base():
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

        logging.log(logging.INFO, f"Authentication attempt from {flask.request.remote_addr} for user {data['username']}")

        if base64.b64decode(authstring) == authstring:
            logging.log(f"Authenticated {data['username']} from {flask.request.remote_addr}",
                             source=f"teamserver")
            success = True
        else:
            error = False

        return "login_ok"

    def start_teamserver(self, *args):
        global teamserver

        teamserver = args[0]

        try:
            app.run(host=teamserver.addr, port=teamserver.port)
        except Exception as e:
            self.logging.log(f"Critical error when starting teamserver api server", level="critical",
                             source=f"{self.info['name']}")
            exit()