files = [
    '__init__.py',
    'Adapter.py',
    'AgentManager.py',
    'AnyBase.py',
    'Base.py',
    'Battery.py',
    'Device.py',
    'errors.py',
    'Manager.py',
    'Network.py',
    'NetworkServer.py'
]

install_path = join_paths(pythondir, 'blueman', 'bluez')

foreach f: files
    configure_file(input: f, output: f, copy: true, install_dir: install_path)
endforeach

subdir('obex')