from __future__ import absolute_import, print_function, unicode_literals
from ableton.v2.control_surface.mode import MomentaryBehaviour, LatchingBehaviour
# from ableton.v2.control_surface.control import ButtonControl
from .my_mode import ModesComponent, MomentaryBehaviour, LatchingBehaviour
from .my_switch_control import MySwitchControl

import logging
logger = logging.getLogger(__name__)


class MyModesComponent(ModesComponent):
    cycle_up_mode_button = MySwitchControl()
    # cycle_down_mode_button = ButtonControl()
    cycle_mode_button = MySwitchControl()
    # default_behaviour = LatchingBehaviour()

    def __init__(self, *args, **keywords):
        logger.info('in __init__()')
        (super(MyModesComponent, self).__init__)(*args, **keywords)
        pass


    @cycle_mode_button.released_immediately
    def cycle_mode_button(self, button):
        logger.info('in cycle_mode_button().released_immediately')
        if len(self._mode_list):
            self.cycle_mode(1)


    @cycle_mode_button.released_delayed
    def cycle_mode_button(self, button):
        logger.info('in cycle_mode_button().released_delayed')
        if len(self._mode_list):
            self.cycle_mode(-1)


    @cycle_up_mode_button.released_delayed
    def cycle_up_mode_button(self, button):
        logger.info('in cycle_up_mode_button().released_delayed')
        if len(self._mode_list):
            self.cycle_mode(1)


    @cycle_up_mode_button.released_immediately
    def cycle_up_mode_button(self, button):
        logger.info('in cycle_up_mode_button().released_immediately')
        if len(self._mode_list):
            self.cycle_mode(-1)
