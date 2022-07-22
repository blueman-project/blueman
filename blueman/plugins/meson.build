files = [
    '__init__.py',
    'AppletPlugin.py',
    'BasePlugin.py',
    'errors.py',
    'ManagerPlugin.py',
    'MechanismPlugin.py',
    'ServicePlugin.py'
]

install_path = join_paths(pythondir, 'blueman', 'plugins')

foreach f: files
    configure_file(input: f, output: f, copy: true, install_dir: install_path)
endforeach

subdir('applet')
subdir('manager')
subdir('mechanism')
subdir('services')
