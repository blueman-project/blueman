files = [
    '__init__.py',
    'AgentManager.py',
    'Base.py',
    'Client.py',
    'Manager.py',
    'ObjectPush.py',
    'Session.py',
    'Transfer.py'
]

install_path = join_paths(pythondir, 'blueman', 'bluez', 'obex')

foreach f: files
    configure_file(input: f, output: f, copy: true, install_dir: install_path)
endforeach