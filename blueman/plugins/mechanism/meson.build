files = [
    '__init__.py',
    'Network.py',
    'Ppp.py',
    'Rfcomm.py',
    'RfKill.py'
]

install_path = join_paths(pythondir, 'blueman', 'plugins', 'mechanism')

foreach f: files
    configure_file(input: f, output: f, copy: true, install_dir: install_path)
endforeach
