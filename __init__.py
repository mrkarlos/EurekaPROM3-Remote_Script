
from __future__ import absolute_import, print_function, unicode_literals
from ableton.v2.control_surface.capabilities import CONTROLLER_ID_KEY, NOTES_CC, PORTS_KEY, REMOTE, SCRIPT, controller_id, inport, outport
from .aaa import AAA

def get_capabilities():
    return {
        # CONTROLLER_ID_KEY: controller_id(vendor_id=1891,
        #         product_ids=[408],
        #         model_name='USB Axiom 25'),
        PORTS_KEY: [
                inport(props=[NOTES_CC, SCRIPT]),
                inport(props=[PLAIN_OLD_MIDI]),
                outport(props=[SCRIPT])]
    }

def create_instance(c_instance):
    return AAA(c_instance=c_instance)
