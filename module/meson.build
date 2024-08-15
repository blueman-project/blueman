cython = find_program('cython', 'cython3' ,required: true)

blueman_c = custom_target(
    'blueman_c',
    output: '_blueman.c',
    input: '_blueman.pyx',
    command: [cython, '-w', meson.source_root(), '--output-file', join_paths(meson.build_root(), '@OUTPUT@'), join_paths(meson.build_root(), '@INPUT@')])

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
