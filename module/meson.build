cython = find_program('cython', required: false)
if not cython.found()
    cython = find_program('cython3', required: true)
endif

blueman_c = custom_target(
    'blueman_c',
    output: '_blueman.c',
    input: '_blueman.pyx',
    command: [cython, '--output-file', '@OUTPUT@', '@INPUT@'])

sources = [
    blueman_c,
    'libblueman.c',
    'libblueman.h'
]

deps = [pygobject, pythonlib, gthread, bluez]

bluemanlib = shared_library(
    '_blueman', sources,
    name_prefix: '',
    dependencies : deps,
    c_args: ['-DSN_API_NOT_YET_FROZEN'],
    install: true,
    install_dir: pythondir,
)
