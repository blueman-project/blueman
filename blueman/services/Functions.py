import inspect
import logging
from typing import Optional, List

from blueman.Service import Service
from blueman.Sdp import ServiceUUID
from blueman.bluez.Device import Device
from blueman.bluez.errors import BluezDBusException
import blueman.services


def get_service(device: Device, uuid: str) -> Optional[Service]:
    for name, cls in inspect.getmembers(blueman.services, inspect.isclass):
        if ServiceUUID(uuid).short_uuid == cls.__svclass_id__:
            svc: Service = cls(device, uuid)
            return svc
    return None


def get_services(device: Device) -> List[Service]:
    try:
        services = (get_service(device, uuid) for uuid in device['UUIDs'])
        return [service for service in services if service]
    except BluezDBusException as e:
        logging.exception(e)
        return []
