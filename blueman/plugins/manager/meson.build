files = [
    '__init__.py',
    'Info.py',
    'Notes.py',
    'Services.py'
]

if get_option('pulseaudio')
  files += 'PulseAudioProfile.py'
endif

install_path = join_paths(pythondir, 'blueman', 'plugins', 'manager')

foreach f: files
    configure_file(input: f, output: f, copy: true, install_dir: install_path)
endforeach
