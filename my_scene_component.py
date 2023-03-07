
from __future__ import absolute_import, print_function, unicode_literals
from builtins import zip
import Live
from ableton.v2.control_surface.components.scene import SceneComponent
from .my_clip_slot_component import MyClipSlotComponent

import logging
logger = logging.getLogger(__name__)

class MySceneComponent(SceneComponent):
    clip_slot_component_type = MyClipSlotComponent

    def __init__(self, *args, **keywords):
        logger.info('in __init__()')
        (super(MySceneComponent, self).__init__)(*args, **keywords)
