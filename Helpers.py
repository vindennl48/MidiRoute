import mido

rtmidi_limit = 10240

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

def send_pc(port, chan, program):
    if port is None: return
    msg = mido.Message(
        "program_change",
        channel = int(chan),
        program = int(program),
        time    = 0
    )
    port.send_message(msg.bytes())

def send_note(port, chan, note, value):
    if port is None: return
    msg = mido.Message(
        "note_on",
        channel = int(chan),
        note    = int(note),
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
