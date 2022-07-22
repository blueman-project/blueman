files = [
    '__init__.py',
    'DialupNetwork.py',
    'Functions.py',
    'GroupNetwork.py',
    'NetworkAccessPoint.py',
    'SerialPort.py'
]

install_path = join_paths(pythondir, 'blueman', 'services')

foreach f: files
    configure_file(input: f, output: f, copy: true, install_dir: install_path)
endforeach

subdir('meta')
