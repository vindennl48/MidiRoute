import queue

class Log:
    string_queue = queue.Queue() # Thread status queue

    @staticmethod
    def log(*args):
        args = "".join([str(arg) for arg in args])
        Log.string_queue.put(args)
        print(args)
