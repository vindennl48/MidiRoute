import mido
from Log import Log
from Helpers import mm_convert, select_split, ring
from Devices import Devices
from Datastore import Datastore

COLORS = {
    "blue":   1,
    "green":  50,
    "yellow": 70,
    "red":    83,
}

COLOR_WHEEL = [
    COLORS["blue"], COLORS["green"], COLORS["yellow"], COLORS["red"],
]

DIM    = 10
BRIGHT = 30

CTRL_RESET_1    = 5
CTRL_RESET_2    = 21
CTRL_DELAY_1    = 26
CTRL_REVERB_1   = 27
CTRL_COLOR_TEST = 29 # to test new colors
CTRL_REVERB_EXP = 30
CTRL_VOLUME_EXP = 31


p_ft_callback = lambda message, data: None
def ft_push_settings():
    #  Datastore.push_all_data()
    for knob in Datastore.datastore:
        Datastore.save_knob_data(knob["id"], knob, force_push=True)
        p_ft_callback((mido.Message(
            "control_change",
            channel = Devices.devices["fighter_twister"]["chan_value"],
            control = knob["id"],
            value   = knob["value"]
        ).bytes(), 0), {"force_push": True})

def ft_callback(message, data):
    msg        = mm_convert(message)
    type       = msg.type
    chan       = msg.channel
    ctrl       = msg.control
    value      = msg.value
    force_push = data["force_push"] if "force_push" in data else False

    chan_value = Devices.devices["fighter_twister"]["chan_value"]
    chan_press = Devices.devices["fighter_twister"]["chan_press"]
    #  chan_color = Devices.devices["fighter_twister"]["chan_color"]
    #  chan_brit  = Devices.devices["fighter_twister"]["chan_brit"]

    # ignore all other midi types except cc
    if type != "control_change": return

    # ignore all other channels
    elif chan not in [chan_value, chan_press]: return

    elif ctrl == CTRL_DELAY_1:
        if chan == chan_value:
            split_val = select_split(value, 4)
            color     = ring(COLOR_WHEEL, split_val)

            if Datastore.save_knob_data(ctrl, {
                "value":      value,
                "color":      color,
                "brightness": BRIGHT if value > 0 else DIM,
            }) or force_push:
                Devices.send_midi("cc", "axefx", {
                    "channel": Devices.devices["axefx"]["chan"],
                    "control": Devices.devices["axefx"]["delay_1_chan"],
                    "value":   split_val,
                })

            # make sure axe is in sync with block bypass
            if force_push:
                knob = Datastore.get_knob(ctrl)
                Devices.send_midi("cc", "axefx", {
                    "channel": Devices.devices["axefx"]["chan"],
                    "control": Devices.devices["axefx"]["delay_1_byp"],
                    "value":   127 if knob["brightness"] == BRIGHT else 0,
                })

    elif ctrl == CTRL_REVERB_1:
        if chan == chan_value:
            split_val = select_split(value, 4)
            color     = ring(COLOR_WHEEL, split_val)

            if Datastore.save_knob_data(ctrl, {
                "value":      value,
                "color":      color,
                "brightness": BRIGHT, # reverb is always on
            }) or force_push:
                Devices.send_midi("cc", "axefx", {
                    "channel": Devices.devices["axefx"]["chan"],
                    "control": Devices.devices["axefx"]["reverb_1_chan"],
                    "value":   split_val,
                })

    elif ctrl == CTRL_REVERB_EXP:
        if chan == chan_value:
            if Datastore.save_knob_data(ctrl, {
                "value": value,
            }) or force_push:
                Devices.send_midi("cc", "axefx", {
                    "channel": Devices.devices["axefx"]["chan"],
                    "control": Devices.devices["axefx"]["reverb_exp"],
                    "value":   value,
                })

    elif ctrl == CTRL_VOLUME_EXP:
        if chan == chan_value:
            if Datastore.save_knob_data(ctrl, {
                "value": value,
            }) or force_push:
                Devices.send_midi("cc", "axefx", {
                    "channel": Devices.devices["axefx"]["chan"],
                    "control": Devices.devices["axefx"]["volume_exp"],
                    "value":   value,
                })

    elif ctrl == CTRL_RESET_1:
        if chan == chan_press and value > 0:
            ft_push_settings()

    elif ctrl == CTRL_RESET_2:
        if chan == chan_press and value > 0:
            ft_push_settings()

    elif ctrl == CTRL_COLOR_TEST:
        if chan == chan_value:
            Devices.send_midi("cc", "fighter_twister", {
                "channel": Devices.devices["fighter_twister"]["chan_color"],
                "control": ctrl,
                "value":   value,
            })
            Log.log(f"--> Color test: {value}")

p_ft_callback = ft_callback
