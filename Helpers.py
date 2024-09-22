import mido

def send_cc(port, chan, ctrl, value):
    if port is None: return
    msg = mido.Message(
        "control_change",
        channel = int(chan),
        control = int(ctrl),
        value   = int(value),
        time    = 0
    )
    port.send_message(msg.bytes())

def mm_convert(message):
    midi_message, timestamp = message
    return mido.parse(midi_message)

def clamp(minimum, x, maximum):
    return max(minimum, min(x, maximum))

def select_split(value, divisor):
    return int(value // (128 / divisor))

def ring(ring_list, index):
    return ring_list[index % len(ring_list)]
