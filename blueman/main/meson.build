files = [
    '__init__.py',
    'Adapter.py',
    'Applet.py',
    'Builder.py',
    'Config.py',
    'DBusProxies.py',
    'DbusService.py',
    'DhcpClient.py',
    'DNSServerProvider.py',
    'Manager.py',
    'MechanismApplication.py',
    'NetConf.py',
    'NetworkManager.py',
    'PluginManager.py',
    'PPPConnection.py',
    'Sendto.py',
    'Services.py',
    'SpeedCalc.py',
    'Tray.py'
]

if get_option('pulseaudio')
    files += 'PulseAudioUtils.py'
endif

install_path = join_paths(pythondir, 'blueman', 'main')

foreach f: files
    configure_file(input: f, output: f, copy: true, install_dir: install_path)
endforeach

subdir('applet')
subdir('indicators')
