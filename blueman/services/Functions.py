# coding=utf-8

from blueman.Sdp import ServiceUUID
from blueman.bluez.errors import BluezDBusException
import blueman.services
import inspect
import logging


def get_service(device, uuid):
    for name, cls in inspect.getmembers(blueman.services, inspect.isclass):
        if ServiceUUID(uuid).short_uuid == cls.__svclass_id__:
            return cls(device, uuid)


def get_services(device):
    try:
        services = (get_service(device, uuid) for uuid in device['UUIDs'])
        return [service for service in services if service]
    except BluezDBusException as e:
        logging.exception(e)
        return []
