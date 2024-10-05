from Devices import Devices
from Files import Settings

class Datastore:
    settings  = Settings("/Users/mitch/Documents/Code/Python/MidiRoute/settings.json", [])
    datastore = sorted(settings.json, key = lambda d: d['id'])

    @staticmethod
    def save():
        Datastore.settings.json = Datastore.datastore
        Datastore.settings.save()

    @staticmethod
    def get_knob(id):
        i = next((idx for (idx, d) in enumerate(Datastore.datastore) if d["id"] == id), None)
        if i is not None:
            return Datastore.datastore[i]
        return { "id": id, "value": None, "color": None, "brightness": None }

    @staticmethod
    def _set_knob(id, data):
        i = next((idx for (idx, d) in enumerate(Datastore.datastore) if d["id"] == id), None)
        if i is not None:
            Datastore.datastore[i] = data
        else:
            Datastore.datastore.append(data)

    #  @staticmethod
    #  def get_knob_data(id, type):
    #      knob = Datastore.get_knob(id)
    #      if type not in knob: return None
    #      return knob[type]

    @staticmethod
    # return true if change is detected
    def save_knob_data(id, data, push=True, force_push=False):
        knob = Datastore.get_knob(id)

        set_knob = False

        if "value" in data:
            if data["value"] is not None:
                is_different = True if knob["value"] != data["value"] else False
                set_knob     = True if is_different else set_knob

                knob["value"] = data["value"]
            else:
                is_different = False

            if (push and is_different) or force_push:
                Devices.send_midi("cc", "fighter_twister", {
                    "channel": Devices.devices["fighter_twister"]["chan_value"],
                    "control": id,
                    "value":   knob["value"],
                })

        if "color" in data:
            if data["color"] is not None:
                is_different = True if knob["color"] != data["color"] else False
                set_knob     = True if is_different else set_knob

                knob["color"] = data["color"]
            else:
                is_different = False

            if (push and is_different) or force_push:
                Devices.send_midi("cc", "fighter_twister", {
                    "channel": Devices.devices["fighter_twister"]["chan_color"],
                    "control": id,
                    "value":   knob["color"],
                })

        if "brightness" in data:
            if data["brightness"] is not None:
                is_different = True if knob["brightness"] != data["brightness"] else False
                set_knob     = True if is_different else set_knob

                knob["brightness"] = data["brightness"]
            else:
                is_different = False

            if (push and is_different) or force_push:
                Devices.send_midi("cc", "fighter_twister", {
                    "channel": Devices.devices["fighter_twister"]["chan_brit"],
                    "control": id,
                    "value":   knob["brightness"],
                })

        if set_knob:
            Datastore._set_knob(id, knob)
            return True

        return False

    @staticmethod
    def push_all_data():
        for knob in Datastore.datastore:
            Datastore.save_knob_data(knob["id"], knob, force_push=True)
