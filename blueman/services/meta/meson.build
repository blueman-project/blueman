files = [
    '__init__.py',
    'NetworkService.py',
    'SerialService.py'
]

install_path = join_paths(pythondir, 'blueman', 'services', 'meta')

foreach f: files
    configure_file(input: f, output: f, copy: true, install_dir: install_path)
endforeach
