# coding=utf-8
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from gi.repository import Gio, GLib

introspection_xml = \
'''
<node name='/org/blueman/obex_agent'>
  <interface name='org.bluez.obex.Agent1'>
    <method name='Release'/>
    <method name='Cancel'/>
    <method name ='AuthorizePush'>
      <arg type='o' name='transfer' direction='in'/>
      <arg type='s' name='path' direction='out'/>
    </method>
  </interface>
</node>
'''

class Agent(object):
    __bus = Gio.bus_get_sync(Gio.BusType.SESSION)

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
