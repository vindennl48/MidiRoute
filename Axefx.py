from Helpers import send_cc, send_pc

axefx = {
    "name":       "Axe-Fx III",
    "alias":      "axefx",
    "virtual":    False,
    "chan":       14,
    "wait":       False,
    "port_id":    None,
    "port_in":    None,
    "port_out":   None,

    "delay_1_byp":    1,
    "delay_1_chan":   2,
    "megatap_1_byp":  9,
    "megatap_1_chan": 10,
    "pitch_1_byp":    21,
    "pitch_1_chan":   22,
    "reverb_1_byp":   29,
    "reverb_1_chan":  30,
    "scene":          110,
    "tuner":          111,

    "clean_high_exp": 112,
    "dist_high_exp":  113,
    "dist_tone_exp":  114,
    "reverb_exp":     126,
    "volume_exp":     127,
}

def axefx_send(type, value):
    send_cc(axefx["port_out"], axefx["chan"], axefx[type], value)

def axefx_send_raw(ctrl, value):
    send_cc(axefx["port_out"], axefx["chan"], ctrl, value)

def axefx_send_pc(program):
    send_pc(axefx["port_out"], axefx["chan"], program)
