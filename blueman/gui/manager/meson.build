files = [
    '__init__.py',
    'ManagerDeviceList.py',
    'ManagerDeviceMenu.py',
    'ManagerMenu.py',
    'ManagerProgressbar.py',
    'ManagerStats.py',
    'ManagerToolbar.py'
]

install_path = join_paths(pythondir, 'blueman', 'gui', 'manager')

foreach f: files
    configure_file(input: f, output: f, copy: true, install_dir: install_path)
endforeach
