# coding=utf-8
from gi.repository import Gio, GLib

introspection_xml = \
    '''
    <node name='/'>
      <interface name='org.bluez.Agent1'>
        <method name='Release'/>
        <method name='RequestPinCode'>
          <arg type='o' name='device' direction='in'/>
          <arg type='s' name='pincode' direction='out'/>
        </method>
        <method name='RequestPasskey'>
          <arg type='o' name='device' direction='in'/>
          <arg type='u' name='passkey' direction='out'/>
        </method>
        <method name='DisplayPasskey'>
          <arg type='o' name='device' direction='in'/>
          <arg type='u' name='passkey' direction='in'/>
          <arg type='y' name='entered' direction='in'/>
        </method>
        <method name='DisplayPinCode'>
          <arg type='o' name='device' direction='in'/>
          <arg type='s' name='pincode' direction='in'/>
        </method>
        <method name='RequestConfirmation'>
          <arg type='o' name='device' direction='in'/>
          <arg type='u' name='passkey' direction='in'/>
        </method>
        <method name='RequestAuthorization'>
          <arg type='o' name='device' direction='in'/>
        </method>
        <method name='AuthorizeService'>
          <arg type='o' name='device' direction='in'/>
          <arg type='s' name='uuid' direction='in'/>
        </method>
        <method name='Cancel'/>
      </interface>
    </node>
    '''


class Agent(object):
    __bus = Gio.bus_get_sync(Gio.BusType.SYSTEM)

    def __init__(self, agent_path, handle_method_call):
        self.__agent_path = agent_path
        self.__handle_method_call = handle_method_call
        self.__node_info = Gio.DBusNodeInfo.new_for_xml(introspection_xml)
        self.__regid = None

    def _register_object(self):
        regid = self.__bus.register_object(
            self.__agent_path,
            self.__node_info.interfaces[0],
            self.__handle_method_call,
            None,
            None)

        if regid:
            self.__regid = regid
        else:
            raise GLib.Error('Failed to register object with path: %s', self.__agent_path)

    def _unregister_object(self):
        self.__bus.unregister_object(self.__regid)
        self.__regid = None
