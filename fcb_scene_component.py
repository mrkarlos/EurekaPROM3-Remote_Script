
from __future__ import absolute_import, print_function, unicode_literals
from builtins import zip
import Live
from ableton.v2.base import liveobj_valid
from ableton.v2.control_surface.components.scene import SceneComponent
from ableton.v2.control_surface.control import ButtonControl

from .fcb_clip_slot_component import FcbClipSlotComponent
from .fcb_switch_control import FcbSwitchControl

import logging
logger = logging.getLogger(__name__)

class FcbSceneComponent(SceneComponent):
    clip_slot_component_type = FcbClipSlotComponent
    # launch_button = ButtonControl()
    launch_button = FcbSwitchControl()

    def __init__(self, *args, **keywords):
        logger.info('in __init__()')
        super().__init__(*args, **keywords)


    def update(self):
        logger.info('in update()')
        (super(FcbSceneComponent, self).update)()


    @launch_button.pressed
    def launch_button(self, value):
        logger.info('in launch_button().pressed')
        self._on_launch_button_pressed()
        pass

    # @launch_button.pressed_delayed
    # def launch_button(self, value):
    #     logger.info('in launch_button().pressed_delayed')
    #     # self._on_launch_button_pressed()
    #     pass

    @launch_button.released
    def launch_button(self, value):
        logger.info('in launch_button().released')
        self._on_launch_button_released()
        pass

    # @launch_button.released_immediately
    # def launch_button(self, value):
    #     logger.info('in launch_button().released_immediately')
    #     # self._on_launch_button_pressed()
    #     pass

    # @launch_button.released_delayed
    # def launch_button(self, value):
    #     logger.info('in launch_button().released_delayed')
    #     # self._on_launch_button_released()
    #     pass