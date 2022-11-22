project(
    'blueman', 'c',
    version: '2.3.5',
    license: 'GPL3',
    meson_version: '>=0.50.0',
    default_options: 'b_lundef=false'
)

package_name = meson.project_name()

# Import needed modules
python = import('python')
gnome = import('gnome')
i18n = import('i18n')

pyinstall = python.find_installation('python3', required: true)

if not pyinstall.language_version().version_compare('>=3.6')
    error('Python 3.6 or higher not found which is required.')
endif

# Setup all directories we install in
prefix = get_option('prefix')
datadir = join_paths([prefix, get_option('datadir')])
pkgdatadir = join_paths([prefix, get_option('datadir'), package_name])
bindir = join_paths([prefix, get_option('bindir')])
libexecdir = join_paths([prefix, get_option('libexecdir')])
schemadir = join_paths(['share', 'glib-2.0', 'schemas'])
pythondir = pyinstall.get_install_dir()

if get_option('policykit')
    have_polkit = 'True'
else
    have_polkit = 'False'
endif

# Setup congfiguration
conf_data = configuration_data()
conf_data.set('BINDIR', bindir)
conf_data.set('LIBEXECDIR', libexecdir)
conf_data.set('VERSION', meson.project_version())
conf_data.set('PACKAGE', package_name)
conf_data.set('prefix', prefix)
conf_data.set('pkgdatadir', pkgdatadir)
conf_data.set('LOCALEDIR', join_paths(prefix, get_option('localedir')))
conf_data.set('icondir', join_paths(datadir, 'icons'))
conf_data.set('dhconfig', get_option('dhcp-config-path'))
conf_data.set('POLKIT', have_polkit)
conf_data.set('GETTEXT_PACKAGE', package_name)
conf_data.set('PYTHON', pyinstall.path())

# Check for build dependencies
pythonlib = pyinstall.dependency()
pygobject = dependency('pygobject-3.0', required: true)
bluez = dependency('bluez', version: '>= 5.0', required: true)
gthread = dependency('gthread-2.0', version: '>= 2.32', required: true)

# Check for systemd to get unit file dirs
systemd = dependency('systemd', required: false)

# Check for runtime deps and when not found fail based on runtime_deps_check
do_runtime_checks = get_option('runtime_deps_check')

gtk = dependency('gtk+-3.0', version: '>= 3.10.', required: do_runtime_checks)

# Configure blueman apps
foreach libexecapp: ['blueman-mechanism', 'blueman-rfcomm-watcher']
    configure_file(
        input: join_paths('apps', libexecapp + '.in'),
        output: libexecapp,
        install_dir: libexecdir,
        install_mode: 'rwxr-xr-x',
        configuration: conf_data
    )
endforeach

binapps = ['blueman-adapters', 'blueman-applet', 'blueman-manager',
           'blueman-sendto', 'blueman-services', 'blueman-tray']

foreach binapp: binapps
    configure_file(
        input: join_paths('apps', binapp + '.in'),
        output: binapp,
        install_dir: bindir,
        install_mode: 'rwxr-xr-x',
        configuration: conf_data
    )
endforeach

# Install all the artwork and icons
# FIXME use strip_directory when meson 0.45.0 is mainstream
install_data(
    'data/icons/pixmaps/blueman-battery-10.png',
    'data/icons/pixmaps/blueman-battery-20.png',
    'data/icons/pixmaps/blueman-battery-30.png',
    'data/icons/pixmaps/blueman-battery-40.png',
    'data/icons/pixmaps/blueman-battery-50.png',
    'data/icons/pixmaps/blueman-battery-60.png',
    'data/icons/pixmaps/blueman-battery-70.png',
    'data/icons/pixmaps/blueman-battery-80.png',
    'data/icons/pixmaps/blueman-battery-90.png',
    'data/icons/pixmaps/blueman-battery-100.png',
    'data/icons/pixmaps/blueman-lq-10.png',
    'data/icons/pixmaps/blueman-lq-20.png',
    'data/icons/pixmaps/blueman-lq-30.png',
    'data/icons/pixmaps/blueman-lq-40.png',
    'data/icons/pixmaps/blueman-lq-50.png',
    'data/icons/pixmaps/blueman-lq-60.png',
    'data/icons/pixmaps/blueman-lq-70.png',
    'data/icons/pixmaps/blueman-lq-80.png',
    'data/icons/pixmaps/blueman-lq-90.png',
    'data/icons/pixmaps/blueman-lq-100.png',
    'data/icons/pixmaps/blueman-rssi-10.png',
    'data/icons/pixmaps/blueman-rssi-20.png',
    'data/icons/pixmaps/blueman-rssi-30.png',
    'data/icons/pixmaps/blueman-rssi-40.png',
    'data/icons/pixmaps/blueman-rssi-50.png',
    'data/icons/pixmaps/blueman-rssi-60.png',
    'data/icons/pixmaps/blueman-rssi-70.png',
    'data/icons/pixmaps/blueman-rssi-80.png',
    'data/icons/pixmaps/blueman-rssi-90.png',
    'data/icons/pixmaps/blueman-rssi-100.png',
    'data/icons/pixmaps/blueman-tpl-10.png',
    'data/icons/pixmaps/blueman-tpl-20.png',
    'data/icons/pixmaps/blueman-tpl-30.png',
    'data/icons/pixmaps/blueman-tpl-40.png',
    'data/icons/pixmaps/blueman-tpl-50.png',
    'data/icons/pixmaps/blueman-tpl-60.png',
    'data/icons/pixmaps/blueman-tpl-70.png',
    'data/icons/pixmaps/blueman-tpl-80.png',
    'data/icons/pixmaps/blueman-tpl-90.png',
    'data/icons/pixmaps/blueman-tpl-100.png',
    install_dir: join_paths([datadir, package_name, 'pixmaps'])
)

icon_makefiles = [
    'Makefile.am',
    '128x128/apps/Makefile.am',
    '128x128/status/Makefile.am',
    '128x128/Makefile.am',
    '16x16/actions/Makefile.am',
    '16x16/apps/Makefile.am',
    '16x16/devices/Makefile.am',
    '16x16/status/Makefile.am',
    '16x16/Makefile.am',
    '192x192/apps/Makefile.am',
    '192x192/status/Makefile.am',
    '192x192/Makefile.am',
    '22x22/apps/Makefile.am',
    '22x22/status/Makefile.am',
    '22x22/Makefile.am',
    '24x24/actions/Makefile.am',
    '24x24/apps/Makefile.am',
    '24x24/status/Makefile.am',
    '24x24/Makefile.am',
    '256x256/apps/Makefile.am',
    '256x256/status/Makefile.am',
    '256x256/Makefile.am',
    '32x32/actions/Makefile.am',
    '32x32/apps/Makefile.am',
    '32x32/status/Makefile.am',
    '32x32/Makefile.am',
    '48x48/actions/Makefile.am',
    '48x48/apps/Makefile.am',
    '48x48/status/Makefile.am',
    '48x48/Makefile.am',
    '64x64/apps/Makefile.am',
    '64x64/status/Makefile.am',
    '64x64/Makefile.am',
    '72x72/apps/Makefile.am',
    '72x72/status/Makefile.am',
    '72x72/Makefile.am',
    '96x96/apps/Makefile.am',
    '96x96/status/Makefile.am',
    '96x96/Makefile.am',
    'scalable/actions/Makefile.am',
    'scalable/apps/Makefile.am',
    'scalable/devices/Makefile.am',
    'scalable/status/Makefile.am',
    'scalable/Makefile.am'
]

install_subdir(
    'data/icons/hicolor',
    install_dir: join_paths([datadir, 'icons']),
    exclude_files: icon_makefiles
)


# GtkBuilder UI files
install_subdir(
    'data/ui',
    install_dir: pkgdatadir,
    exclude_files: ['Makefile.am']
)


# Gsettings and pin database
install_data('data/org.blueman.gschema.xml', install_dir: schemadir)

# Merge translation into policy file
i18n.merge_file(
    input: 'data/configs/org.blueman.policy.in',
    output: 'org.blueman.policy',
    type: 'xml',
    po_dir: 'po',
    data_dirs: 'data/configs',
    install: true,
    install_dir: join_paths(datadir, 'polkit-1', 'actions'),
)

# Merge translations into desktop files
i18n.merge_file(
    input: 'data/blueman.desktop.in',
    output: 'blueman.desktop',
    type: 'desktop',
    po_dir: 'po',
    install: true,
    install_dir: join_paths([get_option('sysconfdir'), 'xdg', 'autostart']),
)

i18n.merge_file(
    input: 'data/blueman-adapters.desktop.in',
    output: 'blueman-adapters.desktop',
    type: 'desktop',
    po_dir: 'po',
    install: true,
    install_dir: join_paths([datadir,'applications']),
)

i18n.merge_file(
    input: 'data/blueman-manager.desktop.in',
    output: 'blueman-manager.desktop',
    type: 'desktop',
    po_dir: 'po',
    install: true,
    install_dir: join_paths([datadir,'applications']),
)

i18n.merge_file(
    input: 'data/thunar-sendto-blueman.desktop.in',
    output: 'thunar-sendto-blueman.desktop',
    type: 'desktop',
    po_dir: 'po',
    install: get_option('thunar-sendto'),
    install_dir: join_paths([datadir,'Thunar', 'sendto']),
)


# install manpages
install_man(
    'data/man/blueman-adapters.1',
    'data/man/blueman-applet.1',
    'data/man/blueman-manager.1',
    'data/man/blueman-sendto.1',
    'data/man/blueman-services.1',
    'data/man/blueman-tray.1'
)


# Gather all configurable files
configurable_files = [
    ['blueman/Constants.py.in',
     'Constants.py',
     join_paths(pythondir, package_name)],
    ['data/configs/org.blueman.Applet.service.in',
     'org.blueman.Applet.service',
     join_paths(datadir, 'dbus-1', 'services')],
    ['data/configs/org.blueman.Manager.service.in',
     'org.blueman.Manager.service',
     join_paths(datadir, 'dbus-1', 'services')],
    ['data/configs/org.blueman.Mechanism.service.in',
     'org.blueman.Mechanism.service',
     join_paths(datadir, 'dbus-1', 'system-services')]
]

systemd_user_dir = get_option('systemduserunitdir')
if systemd_user_dir != ''
    systemd_user_path = join_paths(prefix, systemd_user_dir)
elif systemd.found()
    systemd_user_path = join_paths(prefix, systemd.get_pkgconfig_variable('systemduserunitdir'))
else
    systemd_user_path = ''
endif

if systemd_user_path != ''
    configurable_files += [['data/configs/blueman-applet.service.in',
                            'blueman-applet.service',
                            systemd_user_path],
                           ['data/configs/blueman-manager.service.in',
                            'blueman-manager.service',
                            systemd_user_path]]
endif

systemd_system_dir = get_option('systemdsystemunitdir')
if systemd_system_dir != ''
    systemd_system_path = join_paths(prefix, systemd_system_dir)
elif systemd.found()
    systemd_system_path = join_paths(prefix, systemd.get_pkgconfig_variable('systemdsystemunitdir'))
else
    systemd_system_path = ''
endif

if systemd_system_path != ''
    configurable_files += [['data/configs/blueman-mechanism.service.in',
                            'blueman-mechanism.service',
                            systemd_system_path]]
endif

# Generate all configurable files based on conf_data
foreach conf_file: configurable_files
    configure_file(
        input: conf_file[0],
        output: conf_file[1],
        install_dir: conf_file[2],
        configuration: conf_data
    )
endforeach

install_data(
    'data/configs/org.blueman.Mechanism.conf',
    install_dir: join_paths(get_option('datadir'), 'dbus-1', 'system.d')
)


# Install blueman subdir and exclude files based on configure options
blueman_makefiles = [
    'Makefile.am',
    'bluez/obex/Makefile.am',
    'bluez/Makefile.am',
    'config/Makefile.am',
    'gui/applet/Makefile.am',
    'gui/manager/Makefile.am',
    'gui/Makefile.am',
    'main/applet/Makefile.am',
    'main/indicators/Makefile.am',
    'main/Makefile.am',
    'plugins/applet/Makefile.am',
    'plugins/manager/Makefile.am',
    'plugins/mechanism/Makefile.am',
    'plugins/services/Makefile.am',
    'plugins/Makefile.am',
    'services/meta/Makefile.am',
    'services/Makefile.am'
]

blueman_exclude_files = ['Constants.py.in'] + blueman_makefiles
pulseaudio = get_option('pulseaudio')
if not pulseaudio
    blueman_exclude_files += 'plugins/manager/PulseAudioProfile.py'
endif

install_subdir(
    'blueman',
    install_dir: pythondir,
    exclude_files: blueman_exclude_files
)


# Install nautilus (plus clones) python plugins for blueman-sendto
foreach name: get_option('sendto-plugins')
    dep = dependency('@0@-python'.format(name.to_lower()), required: false)
    if not dep.found()
        warning('@0@-python not found which is required for @0@_blueman_sendto to work.'.format(name.to_lower()))
    endif

    sendto_conf = configuration_data()
    sendto_conf.set('FILEMANAGER', name)
    configure_file(
        input: 'sendto/blueman_sendto.py.in',
        output: '@0@_blueman_sendto.py'.format(name.to_lower()),
        configuration: sendto_conf,
        install_dir: join_paths(prefix, datadir, '@0@-python'.format(name.to_lower()), 'extensions')
    )
endforeach

# Add data as custom_target does not work in subdirectory
subdir('data')
subdir('po')
subdir('module')
