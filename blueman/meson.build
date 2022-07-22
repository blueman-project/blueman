files = [
    'bluemantyping.py',
    'DeviceClass.py',
    'Functions.py',
    'gobject.py',
    '__init__.py',
    'Sdp.py',
    'Service.py'
]

install_path = join_paths(pythondir, 'blueman')

foreach f: files
    configure_file(input: f, output: f, copy: true, install_dir: install_path)
endforeach

configure_file(
    input: 'Constants.py.in',
    output: 'Constants.py',
    install_dir: install_path,
    configuration: conf_data
)

subdir('bluez')
subdir('config')
subdir('gui')
subdir('main')
subdir('plugins')
subdir('services')
