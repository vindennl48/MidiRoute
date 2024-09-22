import time
import rtmidi
import mido

from FighterTwister import fighter_twister, ft_load_settings, ft_save_settings
from FighterTwister import ft_setup_callbacks, ft_push_settings
from Axefx import axefx

devices = [ fighter_twister, axefx ]

################################################################################
## Functions ###################################################################
################################################################################
def setup():
    global devices
    available_ports = rtmidi.MidiIn()

    # Print available ports to choose the specific port by name or index
    all_devices_exist = False
    while not all_devices_exist:
        midi_in_ports = available_ports.get_ports()

        # Print out available midi ports
        if midi_in_ports:
            print("--> Available MIDI Input Ports:")
            for i, port_name in enumerate(midi_in_ports):
                print(f"{i}: {port_name}")
        else:
            print("--> No available MIDI input ports.")
            time.sleep(2)
            continue

        # Check for each device in devices dictionary
        all_devices_exist = True
        for device in devices:
            if device["virtual"]: continue

            print(f"--> Selecting MIDI Input Port: {device['name']}..")

            if device["name"] in midi_in_ports:
                device["port_id"] = midi_in_ports.index(device["name"])
                print(f"    Success!")
            else:
                print(f"    Could Not Find MIDI Input Port: {device['name']}..")
                if "wait" in device and not device["wait"]:
                    print(f"    Device Ignored..")
                else:
                    all_devices_exist = False
                    break

        if not all_devices_exist:
            print("##> Trying again..")
            time.sleep(2)
        else:
            print("--> All Devices Found!")

    # Create virtual ports
    for device in devices:
        if device["virtual"]:
            print(f"--> Creating virtual port: {device['name']}")
            device["port_in"] = rtmidi.MidiIn()
            device["port_out"] = rtmidi.MidiOut()
            device["port_in"].open_virtual_port(device["name"])
            device["port_out"].open_virtual_port(device["name"])

    # Open up all ports
    for device in devices:
        if device["virtual"]: continue
        if device["port_id"] is None: continue

        device["port_in"] = rtmidi.MidiIn()
        device["port_out"] = rtmidi.MidiOut()
        device["port_in"].open_port(device["port_id"])
        device["port_out"].open_port(device["port_id"])

# for save timer
last_save_time = time.time()
save_interval  = 1
def loop():
    global last_save_time
    try:
        while True:
            # save timer
            current_time = time.time()
            if current_time - last_save_time >= save_interval:
                ft_save_settings()  # Call the save function
                last_save_time = current_time  # Reset the timer

            time.sleep(0.01)
    except KeyboardInterrupt:
        print("##> Exiting...")

def cleanup():
    # Close all ports in ports dictionary
    print("--> Closing all ports...")
    for device in devices:
        print(f"--> Closing port: {device['name']}")
        if device["port_in"] is not None and device["port_in"].is_port_open():
            print(f"    Closing 'in' port")
            device["port_in"].close_port()
        if device["port_out"] is not None and device["port_out"].is_port_open():
            print(f"    Closing 'out' port")
            device["port_out"].close_port()
        print(f"    Port closed!")

    print("--> All cleaned up; Goodbye!")
    exit()


################################################################################
## Main Loop ###################################################################
################################################################################
if __name__ == "__main__":
    setup()

    ft_load_settings()
    ft_setup_callbacks()
    ft_push_settings()

    loop()
    cleanup()
