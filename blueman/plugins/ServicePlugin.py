from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

class ServicePlugin(object):
    instances = []
    __plugin_info__ = None

    def __init__(self, services_inst):
        ServicePlugin.instances.append(self)
        self._options = []
        self._orig_state = {}
        self.__services_inst = services_inst

        self.__is_exposed = False
        self._is_loaded = False

    def _on_enter(self):
        if not self.__is_exposed:
            self.on_enter()
            self.__is_exposed = True

    def _on_leave(self):
        if self.__is_exposed:
            self.on_leave()
            self.__is_exposed = False


    # call when option has changed.
    def option_changed_notify(self, option_id, state=True):

        if not option_id in self._options:
            self._options.append(option_id)
        else:
            if state:
                self._options.remove(option_id)

        self.__services_inst.option_changed()

    def get_options(self):
        return self._options

    def clear_options(self):
        self._options = []


    #virtual functions
    #in: container hbox
    #out: (menu entry name, menu icon name)
    def on_load(self, container):
        pass

    def on_unload(self):
        pass

    #return true if apply button should be sensitive or false if not. -1 to force disabled
    def on_query_apply_state(self):
        pass

    def on_apply(self):
        pass

    #called when current plugin's page is selected. The plugin's widget should be shown
    def on_enter(self):
        pass

    #called when current plugin's page is changed to another. The plugin's widget should be hidden.
    def on_leave(self):
        pass
