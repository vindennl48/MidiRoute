from Files import Settings
from Helpers import select_split, send_cc, clamp, select_split, ring, mm_convert
from Axefx import axefx_send
import mido

fighter_twister = {
    "name":       "Midi Fighter Twister",
    #  "name":       "WIDI Bud Pro",
    "alias":      "fighter_twister",
    "virtual":    False,
    "chan_value": 0,
    "chan_press": 1,
    "chan_color": 1,
    "chan_brit":  2,
    "wait":       True,
    "port_id":    None,
    "port_in":    None,
    "port_out":   None,
}

colors = {
    "blue":   1,
    "green":  50,
    "yellow": 70,
    "red":    83,
}

color_wheel = [
    colors["blue"], colors["green"], colors["yellow"], colors["red"],
]

ft_save_data = []
ft_settings  = None

ft_callbacks = []

def ft_get_knob(id):
    i = next((idx for (idx, d) in enumerate(ft_save_data) if d["id"] == id), None)
    if i is not None:
        return ft_save_data[i]
    return None

def ft_set_knob(id, data):
    global ft_save_data
    i = next((idx for (idx, d) in enumerate(ft_save_data) if d["id"] == id), None)
    if i is not None:
        ft_save_data[i] = data
    else:
        ft_save_data.append(data)

# return true if change is detected
def ft_save_knob_data(id, type, data):
    knob = ft_get_knob(id)
    if knob is None:
        knob = { "id": id, "value": None, "color": None, "brightness": None }
    if knob[type] != data:
        knob[type] = data
        ft_set_knob(id, knob)
        return True
    return False

# return true if change is detected
def ft_save_value(id, value):
    return ft_save_knob_data(id, "value", value)

def ft_push_value(id, value):
    if value is not None:
        send_cc(fighter_twister["port_out"], fighter_twister["chan_value"], id, value)

# return true if change is detected
def ft_update_value(id, value, force=False):
    if ft_save_value(id, value) or force:
        ft_push_value(id, value)
        return True
    return False

# return true if change is detected
def ft_save_color(id, color):
    return ft_save_knob_data(id, "color", color)

def ft_push_color(id, color):
    if color is not None:
        send_cc(fighter_twister["port_out"], fighter_twister["chan_color"], id, color)

# return true if change is detected
def ft_update_color(id, color, force=False):
    if ft_save_color(id, color) or force:
        ft_push_color(id, color)
        return True
    return False

# return true if change is detected
def ft_save_brit(id, brit):
    return ft_save_knob_data(id, "brightness", clamp(0, brit, 30))

def ft_push_brit(id, brit):
    if brit is not None:
        send_cc(fighter_twister["port_out"], fighter_twister["chan_brit"], id, clamp(0, brit, 30)+17)

# return true if change is detected
def ft_update_brit(id, brit, force=False):
    if ft_save_brit(id, brit) or force:
        ft_push_brit(id, brit)
        return True
    return False

def ft_load_settings():
    global ft_settings
    global ft_save_data
    ft_settings  = Settings("settings.json", [])
    ft_save_data = sorted(ft_settings.json, key=lambda d: d['id'])

def ft_save_settings():
    global ft_settings
    global ft_save_data
    ft_settings.json = ft_save_data
    ft_settings.save()

def callback(message, data):
    msg = mm_convert(message)
    #  print(f"--> Fighter Twister: {msg}")
    if msg.type != "control_change": return
    if "force" not in data: data["force"] = False

    for cb in ft_callbacks:
        type = None
        if msg.channel == fighter_twister["chan_value"]:
            type = "value"
        elif msg.channel == fighter_twister["chan_press"]:
            type = "press"

        if type is not None:
            cb(type, msg.control, msg.value, data["force"])

def ft_setup_callbacks():
    fighter_twister["port_in"].set_callback(callback, {})

def ft_push_settings():
    for knob in ft_save_data:
        ft_push_value(knob["id"], knob["value"])
        ft_push_color(knob["id"], knob["color"])
        ft_push_brit(knob["id"], knob["brightness"])

        callback((mido.Message(
            "control_change",
            channel = fighter_twister["chan_value"],
            control = knob["id"],
            value   = knob["value"]
        ).bytes(), 0), {"force": True})


################################################################################
## Callbacks ###################################################################
################################################################################
def ftc_amp_tone(type, ctrl, value, force=False):
    if type != "value": return

    cc = None
    if ctrl == 16:   cc = "clean_high_exp"
    elif ctrl == 17: cc = "dist_high_exp"
    elif ctrl == 18: cc = "dist_tone_exp"

    if cc is not None:
        if ft_update_value(ctrl, value, force): axefx_send(cc, value)
ft_callbacks.append(ftc_amp_tone)

def ftc_reset(type, ctrl, value, force=False):
    id = [5, 21]
    if ctrl not in id: return

    if type == "press" and value > 0:
        ft_push_settings()
ft_callbacks.append(ftc_reset)

def ftc_pitch_1(type, ctrl, value, force=False):
    id    = 24
    split = 4
    if ctrl != id: return

    if type == "value":
        split_val = select_split(value, split)
        if ft_update_value(id, value, force): axefx_send("pitch_1_chan", split_val)
        ft_update_color(id, ring(color_wheel, split_val), force)

        if value > 0:
            if ft_update_brit(id, 30, force): axefx_send("pitch_1_byp", 127)
        else:
            if ft_update_brit(id, 15, force): axefx_send("pitch_1_byp", 0)

    elif type == "press":
        pass
ft_callbacks.append(ftc_pitch_1)

def ftc_megatap_1(type, ctrl, value, force=False):
    id    = 25
    split = 2
    if ctrl != id: return

    if type == "value":
        split_val = select_split(value, split)
        if ft_update_value(id, value, force): axefx_send("megatap_1_chan", split_val)
        ft_update_color(id, ring(color_wheel, split_val), force)

        if value > 0:
            if ft_update_brit(id, 30, force): axefx_send("megatap_1_byp", 127)
        else:
            if ft_update_brit(id, 15, force): axefx_send("megatap_1_byp", 0)

    elif type == "press":
        pass
ft_callbacks.append(ftc_megatap_1)

def ftc_delay_1(type, ctrl, value, force=False):
    id    = 26
    split = 4
    if ctrl != id: return

    if type == "value":
        split_val = select_split(value, split)
        if ft_update_value(id, value, force): axefx_send("delay_1_chan", split_val)
        ft_update_color(id, ring(color_wheel, split_val), force)

        if value > 0:
            if ft_update_brit(id, 30, force): axefx_send("delay_1_byp", 127)
        else:
            if ft_update_brit(id, 15, force): axefx_send("delay_1_byp", 0)

    elif type == "press":
        pass
ft_callbacks.append(ftc_delay_1)

def ftc_reverb_1(type, ctrl, value, force=False):
    id    = 27
    split = 4
    if ctrl != id: return

    if type == "value":
        split_val = select_split(value, split)
        if ft_update_value(id, value, force): axefx_send("reverb_1_chan", split_val)
        ft_update_color(id, ring(color_wheel, split_val), force)
        ft_update_brit(id, 30, force)

    elif type == "press":
        pass
ft_callbacks.append(ftc_reverb_1)

def ftc_reverb_exp(type, ctrl, value, force=False):
    id = 30
    if ctrl != id: return

    if type == "value":
        if ft_update_value(id, value, force): axefx_send("reverb_exp", value)

    elif type == "press":
        pass
ft_callbacks.append(ftc_reverb_exp)

def ftc_volume_exp(type, ctrl, value, force=False):
    id = 31
    if ctrl != id: return

    if type == "value":
        if ft_update_value(id, value, force): axefx_send("volume_exp", value)

    elif type == "press":
        pass
ft_callbacks.append(ftc_volume_exp)
