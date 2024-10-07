import mido, time
from Log import Log
from Helpers import mm_convert, select_split
from Devices import Devices
from Datastore import Datastore
from FighterTwister import COLORS
from FighterTwister import DIM, BRIGHT, CTRL_DELAY_1, CTRL_REVERB_1
from FighterTwister import CTRL_REVERB_EXP, CTRL_VOLUME_EXP
from FighterTwister import ft_callback, ft_manual_callback

fighter_twister = Devices.devices["fighter_twister"]
axefx           = Devices.devices["axefx"]
mc6_pro         = Devices.devices["mc6_pro"]

def mc6_callback(message, data):
    msg        = mm_convert(message)
    type       = msg.type
    chan       = msg.channel
    force_push = data["force_push"] if "force_push" in data else False

    if type == "program_change":
        prog = msg.program
    else:
        prog = None

    if type == "control_change":
        ctrl = msg.control
        value = msg.value
    else:
        ctrl  = None
        value = None

    if chan == axefx["chan"]:
        if type == "control_change":
            Devices.send_midi("cc", "axefx", {
                "channel": chan,
                "control": ctrl,
                "value":   value,
            })

            if ctrl == axefx["scene"]:
                # delay_1
                Datastore.save_knob_data(CTRL_DELAY_1, {
                    "brightness": DIM,
                })
                ft_manual_callback(
                    type       = "control_change",
                    chan       = fighter_twister["chan_value"],
                    ctrl       = CTRL_DELAY_1,
                    value      = None, # send stored value
                    force_push = True  # force push to axefx
                )

                # reverb_1
                ft_manual_callback(
                    type       = "control_change",
                    chan       = fighter_twister["chan_value"],
                    ctrl       = CTRL_REVERB_1,
                    value      = 0,   # reset channel select
                    block_push = True # don't push to axefx
                )

            elif ctrl == axefx["delay_1_byp"]:
                Datastore.save_knob_data(CTRL_DELAY_1, {
                    "brightness": BRIGHT if value > 0 else DIM,
                })

            elif ctrl == axefx["reverb_exp"]:
                Datastore.save_knob_data(CTRL_REVERB_EXP, {
                    "value": value,
                })

            elif ctrl == axefx["volume_exp"]:
                Datastore.save_knob_data(CTRL_VOLUME_EXP, {
                    "value": value,
                })

        elif type == "program_change":
            Devices.send_midi("pc", "axefx", {
                "channel": chan,
                "program": prog,
            })
            if prog == 1:
                for i in range(16, 16+8):
                    Datastore.save_knob_data(i, {
                        "color":      COLORS["red"],
                        "is_pulsing": True,
                    })
                    time.sleep(0.05)
            else:
                for i in range(16, 16+8):
                    Datastore.save_knob_data(i, {
                        "color":      COLORS["green"],
                        "is_pulsing": False,
                        "brightness": 10,
                    })
                    time.sleep(0.05)

    # if fighter twister is NOT plugged into MC6, and we are sending the FT data
    #  from Reaper or MC6, then we need some way to relay to the FT USB port.
    elif chan == fighter_twister["chan_value"] or \
            chan == fighter_twister["chan_press"] or \
            chan == fighter_twister["chan_brit"] or \
            chan == fighter_twister["chan_color"]:
        if fighter_twister["name"] != mc6_pro["name"]:
            ft_callback(message, data)

def mc6_setup_callback():
    mc6_pro["port_in"].set_callback(mc6_callback, {})

