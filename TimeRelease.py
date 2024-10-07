import time as Time

class TimeRelease:
    callbacks = []

    @staticmethod
    def add_callback(func, data, time):
        TimeRelease.callbacks.append({
            "function": func,
            "data":     data,
            "time":     Time.time() + time
        })

    @staticmethod
    def run_callbacks():
        for callback in TimeRelease.callbacks:
            if Time.time() >= callback["time"]:
                callback["function"](**callback["data"])
                TimeRelease.callbacks.remove(callback)
