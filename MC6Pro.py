import mido
from Helpers import mm_convert, select_split
from Devices import Devices
from Datastore import Datastore
from FighterTwister2 import DIM, BRIGHT, CTRL_DELAY_1, CTRL_REVERB_1
from FighterTwister2 import CTRL_REVERB_EXP, CTRL_VOLUME_EXP
from FighterTwister2 import ft_callback

def mc6_callback(message, data):
    msg        = mm_convert(message)
    type       = msg.type
    chan       = msg.channel
    program    = msg.program
    ctrl       = msg.control
    value      = msg.value
    force_push = data["force_push"] if "force_push" in data else False

    if chan == Devices.devices["axefx"]["chan"]:
        if type == "control_change":
            Devices.send_midi("cc", "axefx", {
                "channel": chan,
                "control": ctrl,
                "value":   value,
            })

            if ctrl == Devices.devices["axefx"]["scene"]:
                # delay_1
                knob = Datastore.get_knob(CTRL_DELAY_1)
                Datastore.save_knob_data(CTRL_DELAY_1, {
                    "brightness": DIM,
                })
                Devices.send_midi("cc", "axefx", {
                    "channel": Devices.devices["axefx"]["chan"],
                    "control": Devices.devices["axefx"]["delay_1_chan"],
                    "value":   select_split(knob["value"], 4),
                })

                # reverb_1
                Datastore.save_knob_data(CTRL_REVERB_1, {
                    "value": 0,
                })

            elif ctrl == Devices.devices["axefx"]["delay_1_byp"]:
                Datastore.save_knob_data(CTRL_DELAY_1, {
                    "brightness": BRIGHT if value > 0 else DIM,
                })

            elif ctrl == Devices.devices["axefx"]["reverb_exp"]:
                Datastore.save_knob_data(CTRL_REVERB_EXP, {
                    "value": value,
                })

            elif ctrl == Devices.devices["axefx"]["volume_exp"]:
                Datastore.save_knob_data(CTRL_VOLUME_EXP, {
                    "value": value,
                })

        elif type == "program_change":
            Devices.send_midi("pc", "axefx", {
                "channel": chan,
                "program": program,
            })

    # if fighter twister is NOT plugged into MC6, and we are sending the FT data
    #  from Reaper or MC6, then we need some way to relay to the FT USB port.
    elif chan == Devices.devices["fighter_twister"]["chan_value"] or \
            chan == Devices.devices["fighter_twister"]["chan_press"] or \
            chan == Devices.devices["fighter_twister"]["chan_brit"] or \
            chan == Devices.devices["fighter_twister"]["chan_color"]:
        if Devices.devices["fighter_twister"]["name"] != Devices.devices["mc6_pro"]["name"]:
            ft_callback(message, data)
