from Base import Base
from gi.repository import GObject


class Session(Base):
    __gsignals__ = {
        'transfer-started': (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT, GObject.TYPE_PYOBJECT, GObject.TYPE_PYOBJECT,)),
        'transfer-progress': (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT,)),
        'transfer-completed': (GObject.SignalFlags.NO_HOOKS, None, ()),
        'error-occurred': (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT,))
    }

    def __init__(self, object_path):
        if self.__class__.get_interface_version()[0] < 5:
            bus_name = 'org.bluez.obex.client'
            interface_name = 'org.bluez.obex.ObjectPush'
        else:
            bus_name = 'org.bluez.obex'
            interface_name = 'org.bluez.obex.ObjectPush1'

        super(Session, self).__init__(object_path, bus_name)

        self.__object_path = object_path
        self.__interface = self._get_interface(interface_name)

    def send_file(self, file_path):
        def reply_handler(transfer_path, props):
            if self.__class__.get_interface_version()[0] < 5:
                handlers = {
                    'PropertyChanged': self.on_transfer_property_changed,
                    'Complete': self.on_transfer_completed,
                    'Error': self.on_transfer_error
                }

                for prop, func in handlers.items():
                    self._get_bus().add_signal_receiver(func, prop, 'org.bluez.obex.Transfer', 'org.bluez.obex.client',
                                                        transfer_path)
            else:
                self._get_bus().add_signal_receiver(self.on_transfer_properties_changed, 'PropertiesChanged',
                                                    'org.freedesktop.DBus.Properties', 'org.bluez.obex', transfer_path)

            self.emit('transfer-started', props['Filename'], file_path, props['Size'])

        self.__interface.SendFile(file_path, reply_handler=reply_handler, error_handler=self.on_transfer_error)

    def on_transfer_property_changed(self, name, value):
        if name == 'Progress':
            self.emit('transfer-progress', value)

    def on_transfer_properties_changed(self, interface_name, changed_properties, _invalidated_properties):
        if interface_name != 'org.bluez.obex.Transfer1':
            return

        for name, value in changed_properties.items():
            if name == 'Transferred':
                self.emit('transfer-progress', value)
            elif name == 'Status' and value == 'complete':
                self.on_transfer_completed()

    def on_transfer_completed(self):
        self.emit('transfer-completed')

    def on_transfer_error(self, *args):
        self.emit('error-occurred', *args)

    def get_object_path(self):
        return self.__object_path
