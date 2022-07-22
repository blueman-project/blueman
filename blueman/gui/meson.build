files = [
    '__init__.py',
    'Animation.py',
    'CommonUi.py',
    'DeviceList.py',
    'DeviceSelectorDialog.py',
    'DeviceSelectorList.py',
    'DeviceSelectorWidget.py',
    'GenericList.py',
    'GsmSettings.py',
    'GtkAnimation.py',
    'Notification.py'
]

install_path = join_paths(pythondir, 'blueman', 'gui')

foreach f: files
    configure_file(input: f, output: f, copy: true, install_dir: install_path)
endforeach

subdir('applet')
subdir('manager')
