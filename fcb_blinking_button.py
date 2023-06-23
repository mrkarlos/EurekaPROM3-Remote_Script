
from __future__ import absolute_import, print_function, unicode_literals
from functools import partial
from ableton.v2.base import lazy_attribute, task
import ableton.v2.control_surface.control as ButtonControlBase
from ableton.v2.control_surface.control import control_color
from ableton.v2.control_surface.control import ButtonControl, ToggleButtonControl

DEFAULT_BLINK_PERIOD = 0.4

class FcbBlinkingButtonControl(ButtonControl):

    class State(ButtonControl.State):
        blink_on_color = control_color('DefaultButton.On')
        blink_off_color = control_color('DefaultButton.Off')

        def __init__(self, blink_on_color='DefaultButton.On', blink_off_color='DefaultButton.Off', blink_period=DEFAULT_BLINK_PERIOD, *a, **k):
            (super(FcbBlinkingButtonControl.State, self).__init__)(*a, **k)
            self.blink_on_color = blink_on_color
            self.blink_off_color = blink_off_color
            self._untoggled_color = 'DefaultButton.Off'
            self._toggled_color = 'DefaultButton.On'
            self._blink_period = blink_period

        def start_blinking(self):
            self._blink_task.restart()

        def stop_blinking(self):
            self._blink_task.kill()

        @lazy_attribute
        def _blink_task(self):
            blink_on = partial(self._set_blinking_color, self.blink_on_color)
            blink_off = partial(self._set_blinking_color, self.blink_off_color)
            return self.tasks.add(task.sequence(task.run(blink_on), task.wait(self._blink_period), task.run(blink_off), task.wait(self._blink_period), task.run(blink_on), task.wait(self._blink_period), task.run(blink_off)))

        def _set_blinking_color(self, color):
            if self._control_element:
                self._control_element.set_light(color)

        def _kill_all_tasks(self):
            super(FcbBlinkingButtonControl.State, self)._kill_all_tasks()
            self._blink_task.kill()