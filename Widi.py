from Helpers import send_cc, mm_convert
from Axefx import axefx, axefx_send_raw
from FighterTwister import fighter_twister, ft_update_value
from FighterTwister import callback as ft_callback

widi = {
    "name":       "WIDI Bud Pro",
    "alias":      "widi",
    "virtual":    False,
    "chan":       13,
    "wait":       False,
    "port_id":    None,
    "port_in":    None,
    "port_out":   None,
}

def widi_setup_callbacks():
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
        elif fighter_twister["name"] != widi["name"]:
            if msg.channel == fighter_twister["chan_value"]:
                ft_callback(message, data)

    widi["port_in"].set_callback(callback, {})

################################################################################
## Callbacks ###################################################################
################################################################################
