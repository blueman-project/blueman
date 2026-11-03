blueman 2.4.3

  User defined options
    runtime_deps_check: false

Found ninja-1.11.1 at /usr/bin/ninja
INFO: autodetecting backend as ninja                                                                                                                                                    
INFO: calculating backend command to run: /usr/bin/ninja -C /home/dorin/work/nirodg/blueman/build-local
ninja: Entering directory `/home/dorin/work/nirodg/blueman/build-local'
[75/75] Linking target module/_blueman.so
Traceback (most recent call last):
  File "/home/dorin/work/nirodg/blueman/blueman/main/Manager.py", line 190, in on_dbus_name_appeared
    action_status = self.PowerManager.get_bluetooth_status() if pm_available else False
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/dorin/work/nirodg/blueman/blueman/main/DBusProxies.py", line 76, in get_bluetooth_status
    result = self.call_sync("org.blueman.Applet.PowerManager.GetBluetoothStatus", None,
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
gi.repository.GLib.GError: g-dbus-error-quark: GDBus.Error:org.freedesktop.DBus.Error.UnknownMethod: No such interface “org.blueman.Applet.PowerManager” on object at path /org/blueman/Applet (19)
❯ ./blueman-next
INFO: autodetecting backend as ninja
INFO: calculating backend command to run: /usr/bin/ninja -C /home/dorin/work/nirodg/blueman/build-local
ninja: Entering directory `/home/dorin/work/nirodg/blueman/build-local'
ninja: no work to do.
Traceback (most recent call last):
  File "/home/dorin/work/nirodg/blueman/blueman/main/Manager.py", line 190, in on_dbus_name_appeared
    action_status = self.PowerManager.get_bluetooth_status() if pm_available else False
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/dorin/work/nirodg/blueman/blueman/main/DBusProxies.py", line 76, in get_bluetooth_status
    result = self.call_sync("org.blueman.Applet.PowerManager.GetBluetoothStatus", None,
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
gi.repository.GLib.GError: g-dbus-error-quark: GDBus.Error:org.freedesktop.DBus.Error.UnknownMethod: No such interface “org.blueman.Applet.PowerManager” on object at path /org/blueman/Applet (19)
Traceback (most recent call last):
  File "/home/dorin/work/nirodg/blueman/blueman/main/Manager.py", line 288, in simple_action
    self.adapter_properties()
  File "/home/dorin/work/nirodg/blueman/blueman/main/Manager.py", line 374, in adapter_properties
    launch("blueman-adapters", name=_("Adapter Preferences"))
  File "/home/dorin/work/nirodg/blueman/blueman/Functions.py", line 134, in launch
    launched: bool = appinfo.launch(files, context)
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
gi.repository.GLib.GError: g-exec-error-quark: Program ‘/home/dorin/work/nirodg/blueman/apps/blueman-adapters’ not found in $PATH (8)
Traceback (most recent call last):
  File "/home/dorin/work/nirodg/blueman/blueman/main/Manager.py", line 286, in simple_action
    launch("blueman-services", name=_("Service Preferences"))
  File "/home/dorin/work/nirodg/blueman/blueman/Functions.py", line 134, in launch
    launched: bool = appinfo.launch(files, context)
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
gi.repository.GLib.GError: g-exec-error-quark: Program ‘/home/dorin/work/nirodg/blueman/apps/blueman-services’ not found in $PATH (8)
Traceback (most recent call last):
  File "/home/dorin/work/nirodg/blueman/blueman/main/Manager.py", line 119, in do_shutdown
    AppletServiceApplication().stop()
  File "/home/dorin/work/nirodg/blueman/blueman/main/DBusProxies.py", line 145, in stop
    self.ActivateAction('(sava{sv})', "Quit", [], {})
  File "/usr/lib/python3/dist-packages/gi/overrides/Gio.py", line 349, in __call__
    result = self.dbus_proxy.call_sync(self.method_name, arg_variant,
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
gi.repository.GLib.GError: g-dbus-error-quark: GDBus.Error:org.freedesktop.DBus.Error.InvalidArgs: Unknown action ‘Quit’ (16)

