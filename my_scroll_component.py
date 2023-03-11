
from __future__ import absolute_import, print_function, unicode_literals
from ableton.v2.control_surface import defaults
from ableton.v2.base import task
from ableton.v2.control_surface.component import Component
from ableton.v2.control_surface.components import ScrollComponent, Scrollable
from ableton.v2.control_surface.control import ButtonControl

from .my_switch_control import MySwitchControl

import logging
logger = logging.getLogger(__name__)

# from ..component import Component

# class Scrollable(object):

#     def can_scroll_up(self):
#         logger.info('Scrollable in can_scroll_up()')
#         return False

#     def can_scroll_down(self):
#         logger.info('Scrollable in can_scroll_down()')
#         return False

#     def scroll_up(self):
#         logger.info('Scrollable in scroll_up()')
#         pass

#     def scroll_down(self):
#         logger.info('Scrollable in scroll_down()')
#         pass


class MyScrollComponent(ScrollComponent, Scrollable):
    # is_private = True
    # scrolling_delay = defaults.MOMENTARY_DELAY
    # scrolling_step_delay = 0.1
    # default_scrollable = Scrollable()
    # default_pager = Scrollable()
    # _scrollable = default_scrollable
    scroll_up_button = MySwitchControl()
    scroll_down_button = MySwitchControl()

    def __init__(self, scrollable=None, *a, **k):
        logger.info('in __init__()')
        (super(MyScrollComponent, self).__init__)(*a, **k)
        self._scroll_task_up = self._make_scroll_task(self._do_scroll_up)
        self._scroll_task_down = self._make_scroll_task(self._do_scroll_down)
        if scrollable != None:
            self.scrollable = scrollable

    # def _make_scroll_task(self, scroll_step):
    #     logger.info('in _make_scroll_task()')
    #     t = self._tasks.add(task.sequence(task.wait(self.scrolling_delay), task.loop(task.wait(self.scrolling_step_delay), task.run(scroll_step))))
    #     t.kill()
    #     return t

    # @property
    # def scrollable(self):
    #     logger.info('in scrollable()')
    #     return self._scrollable

    # @scrollable.setter
    # def scrollable(self, scrollable):
    #     logger.info('in scrollable.setter()')
    #     self._scrollable = scrollable
    #     self._update_scroll_buttons()

    # def can_scroll_up(self):
    #     logger.info('in can_scroll_up()')
    #     return self._scrollable.can_scroll_up()

    # def can_scroll_down(self):
    #     logger.info('in can_scroll_down()')
    #     return self._scrollable.can_scroll_down()

    # def scroll_up(self):
    #     logger.info('in scroll_up()')
    #     return self._scrollable.scroll_up()

    # def scroll_down(self):
    #     logger.info('in scroll_down()')
    #     return self._scrollable.scroll_down()

    # def set_scroll_up_button(self, button):
    #     logger.info('in set_scroll_up_button()')
    #     self.scroll_up_button.set_control_element(button)
    #     self._update_scroll_buttons()

    # def set_scroll_down_button(self, button):
    #     logger.info('in set_scroll_down_button()')
    #     self.scroll_down_button.set_control_element(button)
    #     self._update_scroll_buttons()


    # def _update_scroll_buttons(self):
    #     logger.info('in _update_scroll_buttons()')
    #     self.scroll_up_button.enabled = self.can_scroll_up()
    #     self.scroll_down_button.enabled = self.can_scroll_down()

    @scroll_up_button.pressed
    def scroll_up_button(self, button):
        logger.info('in scroll_up_button().pressed')
        self._on_scroll_pressed(button, self._do_scroll_up, self._scroll_task_up)

    @scroll_up_button.released
    def scroll_up_button(self, button):
        logger.info('in scroll_up_button().released')
        self._on_scroll_released(self._scroll_task_up)

    @scroll_up_button.released_immediately
    def scroll_up_button(self, button):
        logger.info('in scroll_up_button().released_immediately')
        # self._on_scroll_released(self._scroll_task_up)


    @scroll_down_button.pressed
    def scroll_down_button(self, button):
        logger.info('in scroll_down_button().pressed')
        self._on_scroll_pressed(button, self._do_scroll_down, self._scroll_task_down)

    @scroll_down_button.released
    def scroll_down_button(self, button):
        logger.info('in scroll_down_button().released')
        self._on_scroll_released(self._scroll_task_down)

    # def _do_scroll_up(self):
    #     logger.info('in _do_scroll_up()')
    #     self.scroll_up()
    #     self._update_scroll_buttons()

    # def _do_scroll_down(self):
    #     logger.info('in _do_scroll_down()')
    #     self.scroll_down()
    #     self._update_scroll_buttons()


    # def update(self):
    #     logger.info('in update()')
    #     super(MyScrollComponent, self).update()
    #     self._update_scroll_buttons()


    # def _on_scroll_pressed(self, button, scroll_step, scroll_task):
    #     logger.info('in _on_scroll_pressed()')
    #     is_scrolling = not self._scroll_task_up.is_killed or not self._scroll_task_down.is_killed
    #     if not is_scrolling:
    #         scroll_step()
    #     if button.enabled:
    #         scroll_task.restart()
    #     self._ensure_scroll_one_direction()

    # def _on_scroll_released(self, scroll_task):
    #     logger.info('in _on_scroll_released()')
    #     scroll_task.kill()
    #     self._ensure_scroll_one_direction()

    # def _ensure_scroll_one_direction(self):
    #     logger.info('in _ensure_scroll_one_direction()')
    #     if self.scroll_up_button.is_pressed and self.scroll_down_button.is_pressed:
    #         self._scroll_task_up.pause()
    #         self._scroll_task_down.pause()
    #     else:
    #         self._scroll_task_up.resume()
    #         self._scroll_task_down.resume()