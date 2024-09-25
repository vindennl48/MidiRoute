from Helpers import send_cc, mm_convert
from Axefx import axefx, axefx_send_raw
from FighterTwister import fighter_twister, ft_update_value, ft_send_raw
from FighterTwister import callback as ft_callback

widi = {
    "name":       "WIDI Bud Pro",
    "alias":      "widi",
    "virtual":    False,
    "chan":       13,
    "wait":       True,
    "port_id":    None,
    "port_in":    None,
    "port_out":   None,
}

def widi_setup_callbacks():
    if widi["port_in"] is None: return
    def callback(message, data):
        msg = mm_convert(message)

        ## DESTINATION AXEFX ##
        if msg.channel == axefx["chan"]:
            axefx_send_raw(msg.control, msg.value)
            # send volume and reverb to fighter twister
            if msg.control == axefx["reverb_exp"]:
                ft_update_value(30, msg.value)
            elif msg.control == axefx["volume_exp"]:
                ft_update_value(31, msg.value)

        ## DESTINATION FIGHTER TWISTER ##
        ## BUT INCOMING FROM MORNINGSTAR ##
        elif msg.channel == fighter_twister["chan_value"] or \
                msg.channel == fighter_twister["chan_press"] or \
                msg.channel == fighter_twister["chan_color"] or \
                msg.channel == fighter_twister["chan_brit"]:
            if fighter_twister["name"] != widi["name"]:
                ft_callback(message, data)

    widi["port_in"].set_callback(callback, {})
