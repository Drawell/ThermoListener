

def callback(func):
    def set(self, value):
        self.callback_functions[func.__name__] = value

    def get(self):
        return self.callback_functions[func.__name__] if func.__name__ in self.callback_functions else self._pass

    return property(get, set)


class RecordControllerCallback:
    def __init__(self):
        self.callback_functions = {}

    def _pass(self, *args, **kwargs):
        pass

    @callback
    def on_receive_message(self):
        pass

    @callback
    def on_error(self):
        pass

    @callback
    def on_receive_temperature(self):
        pass

    @callback
    def on_receive_action(self):
        pass

    @callback
    def on_receive_turn_on(self):
        pass

    @callback
    def on_receive_turn_off(self):
        pass
