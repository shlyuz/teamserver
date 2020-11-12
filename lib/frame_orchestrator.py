from lib import listener
from lib import transmit

destinations = {"lpi": listener.lp_init,
                "lpm": listener.lp_process_manifest,
                "lpo": listener.lp_initialized,
                "lprk": listener.lp_rekey,
                "gcmd": listener.lp_getcmd
                }


def determine_destination(frame, teamserver):
    if frame['cmd'] in destinations.keys():
        teamserver.logging.log(f"Routing '{frame['cmd']}' frame to {destinations[frame['cmd']]}", level="debug",
                               source="lib.frame_orchestrator")
        return destinations[frame['cmd']](frame, teamserver)
    else:
        teamserver.logging.log(f"Invalid frame received", level="warn", source="lib.frame_orchestrator")
        teamserver.logging.log(f"Invalid frame: {frame}", level="debug", source="lib.frame_orchestrator")
        return None
