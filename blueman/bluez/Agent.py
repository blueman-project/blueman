# coding=utf-8
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.Functions import dprint
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
        node_info = Gio.DBusNodeInfo.new_for_xml(introspection_xml)

        regid = self.__bus.register_object(
            agent_path,
            node_info.interfaces[0],
            handle_method_call,
            None,
            None)

        if regid:
            self.__regid = regid
        else:
            raise GLib.Error('Failed to register object with path: %s', agent_path)

    def __del__(self):
        self._unregister_object()

    def _unregister_object(self):
        self.__bus.unregister_object(self.__regid)
