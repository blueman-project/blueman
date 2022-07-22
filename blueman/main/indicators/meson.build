files = [
    '__init__.py',
    'GtkStatusIcon.py',
    'IndicatorInterface.py',
    'StatusNotifierItem.py'
]

install_path = join_paths(pythondir, 'blueman', 'main', 'indicators')

foreach f: files
    configure_file(input: f, output: f, copy: true, install_dir: install_path)
endforeach
