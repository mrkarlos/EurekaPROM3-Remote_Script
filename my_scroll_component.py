
from __future__ import absolute_import, print_function, unicode_literals
from ableton.v2.control_surface.components import ScrollComponent, Scrollable

from .my_switch_control import MySwitchControl

import logging
logger = logging.getLogger(__name__)


class MyScrollComponent(ScrollComponent, Scrollable):
    # scroll_up_button = MySwitchControl()
    # scroll_down_button = MySwitchControl()
    scroll_up_down_button = MySwitchControl()
    scroll_left_right_button = MySwitchControl()

    def __init__(self, scrollable=None, *a, **k):
        logger.info('in __init__()')
        (super(MyScrollComponent, self).__init__)(*a, **k)
        self._scroll_task_up = self._make_scroll_task(self._do_scroll_up)
        self._scroll_task_down = self._make_scroll_task(self._do_scroll_down)
        if scrollable != None:
            self.scrollable = scrollable

    def set_scroll_up_down_button(self, button):
        self.scroll_up_down_button.set_control_element(button)
        self._update_scroll_buttons()

    @scroll_up_down_button.pressed
    def scroll_up_down_button(self, button):
        logger.info('in scroll_up_button().pressed')
        # self._on_scroll_pressed(button, self._do_scroll_up, self._scroll_task_up)
        pass

    @scroll_up_down_button.released
    def scroll_up_down_button(self, button):
        logger.info('in scroll_up_down_button().released')
        pass

    @scroll_up_down_button.released_immediately
    def scroll_up_down_button(self, button):
        logger.info('in scroll_up_down_button().released_immediately')
        self.scroll_down()

    @scroll_up_down_button.released_delayed
    def scroll_up_down_button(self, button):
        logger.info('in scroll_up_down_button().released_delayed')
        self.scroll_up()


    def set_scroll_left_right_button(self, button):
        self.scroll_left_right_button.set_control_element(button)
        self._update_scroll_buttons()


    @scroll_left_right_button.pressed
    def scroll_left_right_button(self, button):
        logger.info('in scroll_left_right_button().pressed')
        pass

    @scroll_left_right_button.released
    def scroll_left_right_button(self, button):
        logger.info('in scroll_left_right_button().released')
        pass

    @scroll_left_right_button.released_immediately
    def scroll_left_right_button(self, button):
        logger.info('in scroll_left_right_button().released_immediately')
        self.scroll_down()

    @scroll_left_right_button.released_delayed
    def scroll_left_right_button(self, button):
        logger.info('in scroll_left_right_button().released_delayed')
        self.scroll_up()