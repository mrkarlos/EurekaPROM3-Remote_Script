
from __future__ import absolute_import, print_function, unicode_literals
from ableton.v2.control_surface.elements import ButtonElement
import logging
logger = logging.getLogger(__name__)


class FcbButtonElement(ButtonElement):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def receive_midi_chunk(self, midi_bytes):
        logger.debug('FcbButtonElement - Received midi chunk')
        super(FcbButtonElement, self).receive_midi_chunk(midi_bytes)


    def receive_midi(self, midi_bytes):
        logger.debug('Received midi bytes')
        super(FcbButtonElement, self).receive_midi(midi_bytes)


    def set_light(self, value):
        logger.debug('name: {}, set_light() value: {}'.format(self.name, value))
        super(FcbButtonElement, self).set_light(value)

