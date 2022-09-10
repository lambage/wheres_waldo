class Notification:
    def __init__(self):
        self._callbacks = {}

    def add_callback(self, func):
        """Register a new callback"""
        self._callbacks[func] = func

    def remove_callback(self, func):
        """Remove a callback if possible"""
        if func in self._callbacks:
            del self._callbacks[func]

    def _notify_callbacks(self, *args, **kwargs):
        for func in self._callbacks.values():
            func(*args, **kwargs)
