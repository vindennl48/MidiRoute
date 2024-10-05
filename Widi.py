from Helpers import send_cc, mm_convert
from Axefx import axefx, axefx_send, axefx_send_raw, axefx_send_pc
from FighterTwister import fighter_twister, ft_update_value, ft_push_settings
from FighterTwister import ftc_delay_1, ftc_reverb_1
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
        print(f"{widi['name']}: {msg}")

        ## DESTINATION AXEFX ##
        if msg.channel == axefx["chan"]:
            if msg.type == "control_change":
                axefx_send_raw(msg.control, msg.value)

                # update knobs on fighter twister
                if msg.control == axefx["scene"]:
                    ftc_delay_1("value", 26, None, True, True) # keep delay setting set
                    ftc_delay_1("press", 26, 0, True, False) # turn off delay

                    ftc_reverb_1("value", 27, 0, True, False) # reset reverb knob

                elif msg.control == axefx["delay_1_byp"]:
                    # if we send delay byp from MC6, update knob
                    ftc_delay_1("press", 26, msg.value, True, False)

                # send volume and reverb to fighter twister
                elif msg.control == axefx["reverb_exp"]:
                    ft_update_value(30, msg.value)
                elif msg.control == axefx["volume_exp"]:
                    ft_update_value(31, msg.value)

            elif msg.type == "program_change":
                axefx_send_pc(msg.program)

        ## DESTINATION FIGHTER TWISTER ##
        ## BUT INCOMING FROM MORNINGSTAR ##
        elif msg.channel == fighter_twister["chan_value"] or \
                msg.channel == fighter_twister["chan_press"] or \
                msg.channel == fighter_twister["chan_color"] or \
                msg.channel == fighter_twister["chan_brit"]:
            if fighter_twister["name"] != widi["name"]:
                ft_callback(message, data)

    widi["port_in"].set_callback(callback, {})
