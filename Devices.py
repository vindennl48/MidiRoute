import mido
from Log import Log

class Devices:
    devices = {
        "fighter_twister": {
            "name":       "Midi Fighter Twister",
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
        },

        "axefx": {
            #  "name":       "Axe-Fx III",
            "name":       "Scarlett 18i20 USB",
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
            "boost_exp":      125,
            "reverb_exp":     126,
            "volume_exp":     127,
        },

        "mc6_pro": {
            "name":       "WIDI Bud Pro",
            "alias":      "mc6_pro",
            "virtual":    False,
            "chan":       13,
            "wait":       True,
            "port_id":    None,
            "port_in":    None,
            "port_out":   None,
        },
    }

    @staticmethod
    def send_midi(type, device_name, data):
        if "block_push" in data and data["block_push"]: return

        msg = None
        if device_name not in Devices.devices:
            Log.log(f"##> Devices.send_midi: Device not found: {device_name}")
            Log.log(f"    Will not send message: {str(data)}")
            return False

        if type in ["cc", "note"]:
            if "channel" not in data or data["channel"] is None or \
                "control" not in data or data["control"] is None or \
                "value" not in data or data["value"] is None:
                return False

            #  Log.log(f"--> Devices.send_midi: Sending message: {str(data)}")
            msg = mido.Message(
                "control_change",
                channel = int(data["channel"]),
                control = int(data["control"]),
                value   = int(data["value"]),
                time    = 0
            )

        elif type == "pc":
            if "channel" not in data or \
                "program" not in data:
                return False

            msg = mido.Message(
                "program_change",
                channel = int(data["channel"]),
                program = int(data["program"]),
                time    = 0
            )

        if msg is None:
            Log.log(f"##> Devices.send_midi: Unknown message type: {type}")
            return False
        if Devices.devices[device_name]["port_out"] is None:
            #  Log.log(f"##> Devices.send_midi: Device not connected: {device_name}")
            return False
        if Devices.devices[device_name]["port_out"].is_port_open() is False:
            #  Log.log(f"##> Devices.send_midi: Device not connected: {device_name}")
            return False

        Devices.devices[device_name]["port_out"].send_message(msg.bytes())
