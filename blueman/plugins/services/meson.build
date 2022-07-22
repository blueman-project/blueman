files = [
    '__init__.py',
    'Network.py',
    'Transfer.py'
]

install_path = join_paths(pythondir, 'blueman', 'plugins', 'services')

foreach f: files
    configure_file(input: f, output: f, copy: true, install_dir: install_path)
endforeach
