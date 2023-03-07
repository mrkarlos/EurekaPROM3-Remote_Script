
from __future__ import absolute_import, print_function, unicode_literals
from ableton.v2.control_surface.elements import ButtonElement
import logging
logger = logging.getLogger(__name__)


class MyButtonElement(ButtonElement):

    def __init__(self, *args, **kwargs):
        (super(MyButtonElement, self).__init__)(*args, **kwargs)


    def receive_midi_chunk(self, midi_bytes):
        logger.debug('MyButton - Received midi chunk')
        super(MyButtonElement, self).receive_midi_chunk(midi_bytes)


    def receive_midi(self, midi_bytes):
        logger.debug('Received midi bytes')
        super(MyButtonElement, self).receive_midi(midi_bytes)


    def set_light(self, value):
        logger.debug('name: {}, set_light() value: {}'.format(self.name, value))
        super(MyButtonElement, self).set_light(value)

