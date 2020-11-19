from lib import listener
from lib import transmit

destinations = {"lpi": listener.lp_init,
                "lpm": listener.lp_process_manifest,
                "lpo": listener.lp_initialized,
                "lprk": listener.lp_rekey,
                "gcmd": listener.lp_getcmd,
                "rcok": listener.lp_cmdack
                }


def determine_destination(frame, component):
    if frame['cmd'] in destinations.keys():
        component.logging.log(f"Routing '{frame['cmd']}' frame to {destinations[frame['cmd']]}", level="debug",
                              source="lib.frame_orchestrator")
        return destinations[frame['cmd']](frame, component)
    else:
        component.logging.log(f"Invalid frame received", level="warn", source="lib.frame_orchestrator")
        component.logging.log(f"Invalid frame: {frame}", level="debug", source="lib.frame_orchestrator")
        return None
