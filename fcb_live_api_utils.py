
from __future__ import absolute_import, print_function, unicode_literals
import logging
from ableton.v2.base import liveobj_valid

logger = logging.getLogger(__name__)

def toggle_or_cycle_parameter_value(parameter):
    if liveobj_valid(parameter):
        if parameter.is_quantized:
            if parameter.value + 1 > parameter.max:
                parameter.value = parameter.min
            else:
                parameter.value = parameter.value + 1
        else:
            parameter.value = parameter.max if parameter.value == parameter.min else parameter.min
        

def release_control(control):
    if control != None:
        control.release_parameter()


def is_empty_rack(rack):
    return rack.can_have_chains and len(rack.chains) == 0


def is_rack_with_bank_2(device):
    return getattr(device, 'can_have_chains', False) and any(device.macros_mapped[8:])


def nested_device_parent(device):
    if device.can_have_chains:
        if device.view.is_showing_chain_devices:
            if not device.view.is_collapsed:
                return device.view.selected_chain


def collect_devices(track_or_chain, nesting_level=0):
    logger.info('in collect_devices()')

    chain_devices = track_or_chain.devices if liveobj_valid(track_or_chain) else []
    logger.info('in collect_devices() chain len: {}'.format(len(chain_devices)))

    devices = []
    for device in chain_devices:
        devices.append((device, nesting_level))
        devices.extend(collect_devices((nested_device_parent(device)), nesting_level=(nesting_level + 1)))

    logger.info('in collect_devices() devices len: {}'.format(len(devices)))

    return devices