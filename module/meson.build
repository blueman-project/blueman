cython = find_program('cython', 'cython3' ,required: true)

cython_outfile = join_paths(meson.project_build_root(), '@OUTPUT@')
cython_infile = join_paths(meson.project_build_root(), '@INPUT@')
blueman_c = custom_target(
    'blueman_c',
    output: '_blueman.c',
    input: '_blueman.pyx',
    command: [cython, '-w', meson.project_source_root(), '--output-file', cython_outfile, cython_infile])

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
