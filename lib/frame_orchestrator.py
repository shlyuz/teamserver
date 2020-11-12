from lib import listener
from lib import transmit


destinations = {"lpi": listener.lp_init,
                "lpm": listener.lp_process_manifest,
                "lpo": listener.lp_initalized,
                "lprk": listener.lp_rekey,
                "gcmd": listener.lp_getcmd
                }


def determine_destination(frame, teamserver):
    if frame['t'] in destinations.keys():
        return destinations[frame['t']](frame, teamserver)
    else:
        teamserver.logging.log(f"Invalid frame received", level="warn", source="lib.frame_orchestrator")
        teamserver.logging.log(f"Invalid frame: {frame}", level="debug", source="lib.frame_orchestrator")
        return None