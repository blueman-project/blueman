from dataclasses import dataclass


@dataclass
class BluemanSettings:
    version: str
    package: str
    website: str
    prefix: str
    bindir: str
    localedir: str
    dhcp_config_file: str
    polkit: bool
    gettext_package: str
    rfcomm_watcher_path: str
