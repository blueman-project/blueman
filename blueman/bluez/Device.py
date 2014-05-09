from PropertiesBlueZInterface import PropertiesBlueZInterface
from ServiceInterface import ServiceInterface
from errors import raise_dbus_error
import dbus
import xml.dom.minidom


class Device(PropertiesBlueZInterface):
    @raise_dbus_error
    def __init__(self, obj_path=None):
        if self.__class__.get_interface_version()[0] < 5:
            interface = 'org.bluez.Device'
        else:
            interface = 'org.bluez.Device1'
        super(Device, self).__init__(interface, obj_path)

    @raise_dbus_error
    def list_services(self):
        interfaces = []
        dbus_object = dbus.SystemBus().get_object('org.bluez', self.get_object_path())
        dbus_introspect = dbus.Interface(dbus_object, 'org.freedesktop.DBus.Introspectable')
        introspect_xml = dbus_introspect.Introspect()
        root_node = xml.dom.minidom.parseString(introspect_xml)
        for interface in root_node.getElementsByTagName('interface'):
            interface_name = interface.getAttribute('name')
            if interface_name != self.get_interface_name():
                methods = []
                for method in interface.getElementsByTagName('method'):
                    methods.append(method.getAttribute('name'))
                interfaces.append(ServiceInterface(interface_name, self.get_object_path(), methods))
        return interfaces

    @raise_dbus_error
    def pair(self, reply_handler=None, error_handler=None):
        # BlueZ 5 only!
        def ok():
            if callable(reply_handler):
                reply_handler()

        def err(err):
            if callable(error_handler):
                error_handler(err)

        self.get_interface().Pair(reply_handler=ok, error_handler=err)
