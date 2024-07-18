cython = find_program('cython', 'cython3' ,required: true)

blueman_c = pyinstall.extension_module(
    'blueman_c',
    '_blueman.pyx')

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
