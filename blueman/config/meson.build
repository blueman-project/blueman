files = [
    '__init__.py',
    'AutoConnectConfig.py',
]

install_path = join_paths(pythondir, 'blueman', 'config')

foreach f: files
    configure_file(input: f, output: f, copy: true, install_dir: install_path)
endforeach
