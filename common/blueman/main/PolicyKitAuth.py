#
#
# polkit_auth.py
# (c) 2007 Valmantas Paliksa <walmis at balticum-tv dot lt>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
# 
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#

import os
import time
import dbus


'''
PolicyKit related services.
'''

class PolicyKitAuth(object):
    '''
    Obtains sudo/root access,
    asking the user for authentication if necessary,
    using PolicyKit
    '''

    def is_authorized(self, action_id):
        '''
        Ask PolicyKit whether we are already authorized.
        '''

        # Check whether the process is authorized:
        pid = dbus.UInt32(os.getpid())
        authorized = self.policy_kit.IsProcessAuthorized(action_id, pid, False)

        return ('yes' == authorized)

    def obtain_authorization(self, widget, action_id):
        '''
        Try to obtain authoriztation for the specified action.
        '''

        xid = (widget and widget.get_toplevel().window.xid or 0)
        xid, pid = dbus.UInt32(xid), dbus.UInt32(os.getpid())

        granted = self.auth_agent.ObtainAuthorization(action_id, xid, pid)

        return bool(granted)
    
    def obtain_authorization_async(self, widget, action_id, reply, err):
        '''
        Try to obtain authoriztation for the specified action.
        '''

        xid = (widget and widget.get_toplevel().window.xid or 0)
        xid, pid = dbus.UInt32(xid), dbus.UInt32(os.getpid())

        self.auth_agent.ObtainAuthorization(action_id, xid, pid, reply_handler=reply, error_handler=err)


    def __get_policy_kit(self):
        '''Retreive the D-Bus interface of PolicyKit.'''

        # retreiving the interface raises DBusException on error:
        service = dbus.SystemBus().get_object('org.freedesktop.PolicyKit', '/')
        return dbus.Interface(service, 'org.freedesktop.PolicyKit')

    def __get_auth_agent(self):
        '''Retreive the D-Bus interface of the PolicyKit authentication agent.'''

        # retreiving the interface raises DBusException on error:
        return dbus.SessionBus().get_object(
            'org.freedesktop.PolicyKit.AuthenticationAgent', '/',
            'org.gnome.PolicyKit.AuthorizationManager.SingleInstance')

    auth_agent = property(__get_auth_agent)
    policy_kit = property(__get_policy_kit)

