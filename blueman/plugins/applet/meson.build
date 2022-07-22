files = [
    '__init__.py',
    'AuthAgent.py',
    'AutoConnect.py',
    'Battery.py',
    'ConnectionNotifier.py',
    'DBusService.py',
    'DhcpClient.py',
    'DisconnectItems.py',
    'DiscvManager.py',
    'ExitItem.py',
    'GameControllerWakelock.py',
    'KillSwitch.py',
    'Menu.py',
    'NetUsage.py',
    'Networking.py',
    'NMDUNSupport.py',
    'NMPANSupport.py',
    'PowerManager.py',
    'PPPSupport.py',
    'RecentConns.py',
    'SerialManager.py',
    'ShowConnected.py',
    'StandardItems.py',
    'StatusIcon.py',
    'StatusNotifierItem.py',
    'TransferService.py'
]

if get_option('pulseaudio')
  files += 'PulseAudioProfile.py'
endif

install_path = join_paths(pythondir, 'blueman', 'plugins', 'applet')

foreach f: files
    configure_file(input: f, output: f, copy: true, install_dir: install_path)
endforeach
