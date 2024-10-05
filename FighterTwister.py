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

fighter_twister = Devices.devices["fighter_twister"]
axefx           = Devices.devices["axefx"]


p_ft_callback = lambda message, data: None
def ft_push_settings():
    #  Datastore.push_all_data()
    for knob in Datastore.datastore:
        Datastore.save_knob_data(knob["id"], knob, force_push=True)
        # make sure to run logic to push to axefx
        p_ft_callback((mido.Message(
            "control_change",
            channel = fighter_twister["chan_value"],
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
    block_push = data["block_push"] if "block_push" in data else False

    chan_value = fighter_twister["chan_value"]
    chan_press = fighter_twister["chan_press"]
    #  chan_color = fighter_twister["chan_color"]
    #  chan_brit  = fighter_twister["chan_brit"]

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
                #  "brightness": BRIGHT if value > 0 else DIM,
            }) or force_push:
                Devices.send_midi("cc", "axefx", {
                    "channel": axefx["chan"],
                    "control": axefx["delay_1_chan"],
                    "value":   split_val,
                    "block_push": block_push,
                })

            # make sure axe is in sync with block bypass
            if force_push:
                knob = Datastore.get_knob(ctrl)
                Devices.send_midi("cc", "axefx", {
                    "channel":    axefx["chan"],
                    "control":    axefx["delay_1_byp"],
                    "value":      127 if knob["brightness"] == BRIGHT else 0,
                    "block_push": block_push,
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
                    "channel":    axefx["chan"],
                    "control":    axefx["reverb_1_chan"],
                    "value":      split_val,
                    "block_push": block_push,
                })

    elif ctrl == CTRL_REVERB_EXP:
        if chan == chan_value:
            if Datastore.save_knob_data(ctrl, {
                "value": value,
            }) or force_push:
                Devices.send_midi("cc", "axefx", {
                    "channel":    axefx["chan"],
                    "control":    axefx["reverb_exp"],
                    "value":      value,
                    "block_push": block_push,
                })

    elif ctrl == CTRL_VOLUME_EXP:
        if chan == chan_value:
            if Datastore.save_knob_data(ctrl, {
                "value": value,
            }) or force_push:
                Devices.send_midi("cc", "axefx", {
                    "channel":    axefx["chan"],
                    "control":    axefx["volume_exp"],
                    "value":      value,
                    "block_push": block_push,
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
                "channel":    fighter_twister["chan_color"],
                "control":    ctrl,
                "value":      value,
                "block_push": block_push,
            })
            Log.log(f"--> Color test: {value}")

p_ft_callback = ft_callback

def ft_setup_callback():
    fighter_twister["port_in"].set_callback(ft_callback, {})

def ft_manual_callback(type, chan, ctrl, value, force_push=False, block_push=False):
    knob = Datastore.get_knob(ctrl)

    ft_callback((mido.Message(
        type,
        channel = chan,
        control = ctrl,
        value   = value if value is not None else knob["value"]
    ).bytes(), 0), {
        "force_push": force_push,
        "block_push": block_push
    })
