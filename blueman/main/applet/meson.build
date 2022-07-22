files = [
    '__init__.py',
    'BluezAgent.py'
]

install_path = join_paths(pythondir, 'blueman', 'main', 'applet')

foreach f: files
    configure_file(input: f, output: f, copy: true, install_dir: install_path)
endforeach
