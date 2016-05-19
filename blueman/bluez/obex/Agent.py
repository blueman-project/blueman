# coding=utf-8
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from gi.repository import Gio
from blueman.bluez.Agent import Agent as AgentBase

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


class Agent(AgentBase):
    __bus_type = Gio.BusType.SESSION
