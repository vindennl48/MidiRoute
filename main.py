import time
import queue
import rtmidi
import argparse
import threading
import tkinter as tk

from Log import Log
from Devices import Devices
from Datastore import Datastore
from Helpers import rtmidi_limit
from FighterTwister import ft_setup_callback, ft_push_settings
from MC6Pro import mc6_setup_callback

#  from FighterTwister import fighter_twister, ft_load_settings, ft_save_settings
#  from FighterTwister import ft_setup_callbacks, ft_push_settings
#  from Axefx import axefx
#  from Widi import widi, widi_setup_callbacks

################################################################################
## Setup #######################################################################
################################################################################
fighter_twister = Devices.devices["fighter_twister"]
axefx           = Devices.devices["axefx"]
mc6_pro         = Devices.devices["mc6_pro"]
devices         = [ fighter_twister, axefx, mc6_pro ]

midi_names = {
    "widi":            "WIDI Bud Pro",
    "fighter_twister": "Midi Fighter Twister",
    "mc6_pro":         "Morningstar MC6 Pro Port 1",
    "axefx":           "Axe-Fx III",
}

exit_event    = threading.Event() # Thread exit event
restart_event = threading.Event() # Thread restart event

################################################################################
## Functions ###################################################################
################################################################################
def setup():
    global devices
    available_ports = rtmidi.MidiIn(queue_size_limit=rtmidi_limit)

    # Print available ports to choose the specific port by name or index
    all_devices_exist = False
    while not all_devices_exist:
        midi_in_ports = available_ports.get_ports()

        # Print out available midi ports
        if midi_in_ports:
            Log.log("--> Available MIDI Input Ports:")
            for i, port_name in enumerate(midi_in_ports):
                Log.log(f"{i}: {port_name}")
        else:
            if restart_event.is_set() or exit_event.is_set():
                Log.log("##> Exiting..")
                return False
            Log.log("--> No available MIDI input ports.")
            time.sleep(2)
            continue

        # Check for each device in devices dictionary
        all_devices_exist = True
        for device in devices:
            if device["virtual"]: continue

            Log.log(f"--> Selecting MIDI Port '{device['name']}' for '{device['alias']}' ..")

            if device["name"] in midi_in_ports:
                device["port_id"] = midi_in_ports.index(device["name"])
                Log.log(f"    Success!")
            else:
                Log.log(f"    Could Not Find MIDI Input Port: {device['name']}..")
                if "wait" in device and not device["wait"]:
                    Log.log(f"    Device Ignored..")
                else:
                    all_devices_exist = False
                    break

        if not all_devices_exist:
            if restart_event.is_set() or exit_event.is_set():
                Log.log("##> Exiting..")
                return False
            Log.log("##> Trying again..\n")
            time.sleep(2)
        else:
            Log.log("--> All Devices Found!")

    # Create virtual ports
    for device in devices:
        if device["virtual"]:
            Log.log(f"--> Creating virtual port: {device['name']}")
            device["port_in"] = rtmidi.MidiIn(queue_size_limit=rtmidi_limit)
            device["port_out"] = rtmidi.MidiOut()
            device["port_in"].open_virtual_port(device["name"])
            device["port_out"].open_virtual_port(device["name"])
            if device["port_in"].is_port_open():
                Log.log(f"    Success!")
            else:
                Log.log(f"    Failed!")

    # Open up all ports
    for device in devices:
        if device["virtual"]: continue
        if device["port_id"] is None: continue

        device["port_in"] = rtmidi.MidiIn(queue_size_limit=rtmidi_limit)
        device["port_out"] = rtmidi.MidiOut()
        device["port_in"].open_port(device["port_id"])
        device["port_out"].open_port(device["port_id"])

    return True

# for save timer
last_save_time = time.time()
save_interval  = 1
def loop():
    global last_save_time
    try:
        while not restart_event.is_set() and not exit_event.is_set():
            # save timer
            current_time = time.time()
            if current_time - last_save_time >= save_interval:
                Datastore.save() # call the save function
                last_save_time = current_time  # Reset the timer

            time.sleep(0.01)
    except KeyboardInterrupt:
        Log.log("##> Exiting Backend...")

def cleanup():
    # Close all ports in ports dictionary
    Log.log("--> Closing all ports...")
    for device in devices:
        Log.log(f"--> Closing port: {device['name']}")
        if device["port_in"] is not None and device["port_in"].is_port_open():
            Log.log(f"    Closing 'in' port")
            device["port_in"].close_port()
        if device["port_out"] is not None and device["port_out"].is_port_open():
            Log.log(f"    Closing 'out' port")
            device["port_out"].close_port()
        Log.log(f"    Port closed!")

    Log.log("--> All cleaned up; Goodbye!")

def start_midi():
    while not exit_event.is_set():
        restart_event.clear()
        if setup():
            ft_setup_callback()
            ft_push_settings()

            mc6_setup_callback()

            loop()
            cleanup()

def mode_wireless():
    Log.log("--> Wireless mode selected.")
    fighter_twister["name"] = midi_names["widi"]
    mc6_pro["name"]         = midi_names["widi"]

def mode_computer():
    Log.log("--> Computer mode selected.")
    fighter_twister["name"] = midi_names["mc6_pro"]
    mc6_pro["name"]         = midi_names["mc6_pro"]

def mode_alt():
    Log.log("--> Alternative mode selected.")
    fighter_twister["name"] = midi_names["fighter_twister"]
    mc6_pro["name"]         = midi_names["mc6_pro"]

def start_gui():
    def restart_backend():
        restart_event.set()

    def on_restart_wireless():
        Log.log("--> Restarting with Wireless")
        mode_wireless()
        restart_backend()

    def on_restart_computer():
        Log.log("--> Restarting with Computer")
        mode_computer()
        restart_backend()

    def on_restart_alt():
        Log.log("--> Restarting with Alt")
        mode_alt()
        restart_backend()

    def on_exit():
        exit_event.set()  # Signal the main loop to exit
        root.quit()       # Close the GUI

    # Function to update the label with the latest status from the queue
    def update_label():
        try:
            log_message = Log.string_queue.get_nowait()
            log_textbox.insert(tk.END, log_message + "\n")
            log_textbox.see(tk.END)  # Scroll to the end to always show the latest log
        except queue.Empty:
            pass
        root.after(22, update_label)  # Update every 100 ms

    root = tk.Tk()
    root.title("MIDI Translator Control")
    root.geometry("600x600")

    #  restart_button = tk.Button(root, text="Restart", command=on_restart)
    #  restart_button.pack(pady=20)

    # Label above the buttons
    restart_label = tk.Label(root, text="Restart", font=("Helvetica", 14))
    restart_label.pack(pady=10)

    # Frame for the three buttons (Wireless, Computer, Alt)
    button_frame = tk.Frame(root)
    button_frame.pack(pady=5)

    wireless_button = tk.Button(button_frame, text="Wireless", command=on_restart_wireless)
    wireless_button.pack(side=tk.LEFT, padx=10)

    computer_button = tk.Button(button_frame, text="Computer", command=on_restart_computer)
    computer_button.pack(side=tk.LEFT, padx=10)

    alt_button = tk.Button(button_frame, text="Alt", command=on_restart_alt)
    alt_button.pack(side=tk.LEFT, padx=10)

    exit_button = tk.Button(root, text="Exit", command=on_exit)
    exit_button.pack(pady=20)

    # Add a text box with a scrollbar for the log
    log_frame = tk.Frame(root)
    log_frame.pack(pady=10, fill="both", expand=True)

    scrollbar = tk.Scrollbar(log_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    log_textbox = tk.Text(log_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set)
    log_textbox.pack(side=tk.LEFT, fill="both", expand=True)

    scrollbar.config(command=log_textbox.yview)

    update_label()

    root.mainloop()


################################################################################
## Main Loop ###################################################################
################################################################################
if __name__ == "__main__":
    # setup midi devices based on argument input
    parser = argparse.ArgumentParser(description="MIDI Translator Control")
    
    # Adding mutually exclusive group
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--computer', '-c', action='store_true', help='When MC6Pro is connected to computer')
    group.add_argument('--alt',      '-a', action='store_true', help='When Fighter Twister AND MC6Pro is connected to computer separately')
    group.add_argument('--wireless', '-w', action='store_true', default=True, help='When using Widi wireless (default)')
    
    args = parser.parse_args()

    # Handle the arguments
    if args.computer:
        mode_computer()
        #  Log.log("--> Computer mode selected.")
        #  fighter_twister["name"] = midi_names["mc6_pro"]
        #  mc6_pro["name"]         = midi_names["mc6_pro"]
    elif args.alt:
        mode_alt()
        #  fighter_twister["name"] = midi_names["fighter_twister"]
        #  mc6_pro["name"]         = midi_names["mc6_pro"]
    else:
        mode_wireless()
        #  Log.log("--> Wireless mode selected.")
        #  fighter_twister["name"] = midi_names["widi"]
        #  mc6_pro["name"]         = midi_names["widi"]


    # Start the midi routing in a separate thread
    midi_thread = threading.Thread(target=start_midi)
    midi_thread.start()

    start_gui()

    midi_thread.join()
