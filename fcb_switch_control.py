
from __future__ import absolute_import, print_function, unicode_literals
from ableton.v2.base import EventObject, listens, liveobj_valid, lazy_attribute, task
from ableton.v2.control_surface.control import ButtonControl, ButtonControlBase, control_event, control_color, InputControl

from .consts import DOUBLE_CLICK_DELAY, MOMENTARY_DELAY
from .fcb_live_api_utils import toggle_or_cycle_parameter_value

import logging
logger = logging.getLogger(__name__)

class DoubleClickContext(object):
    control_state = None
    click_count = 0

    def set_new_context(self, control_state):
        self.control_state = control_state
        self.click_count = 0

class FcbButtonControlBase(InputControl):
    DELAY_TIME = MOMENTARY_DELAY
    DOUBLE_CLICK_TIME = DOUBLE_CLICK_DELAY
    REPEAT_RATE = 0.1
    pressed = control_event('pressed')
    released = control_event('released')
    pressed_delayed = control_event('pressed_delayed')
    released_delayed = control_event('released_delayed')
    released_immediately = control_event('released_immediately')
    double_clicked = control_event('double_clicked')

    class State(InputControl.State):
        disabled_color = control_color('DefaultButton.Disabled')
        pressed_color = control_color(None)

        def __init__(self, pressed_color=None, disabled_color=None, repeat=False, enabled=True, double_click_context=None, delay_time=None, *a, **k):
            logger.info('in __init__()')
            (super(FcbButtonControlBase.State, self).__init__)(*a, **k)
            if disabled_color is not None:
                self.disabled_color = disabled_color
            self.pressed_color = pressed_color
            self._repeat = repeat
            self._is_pressed = False
            self._enabled = enabled
            self._double_click_context = double_click_context or DoubleClickContext()
            self._delay_time = delay_time if delay_time is not None else FcbButtonControlBase.DELAY_TIME

        @property
        def enabled(self):
            return self._enabled

        @enabled.setter
        def enabled(self, enabled):
            if self._enabled != enabled:
                if not enabled:
                    self._release_button()
                self._enabled = enabled
                self._send_current_color()

        @property
        def is_momentary(self):
            return self._control_element and self._control_element.is_momentary()

        @property
        def is_pressed(self):
            return self._is_pressed

        def _event_listener_required(self):
            logger.info('in _event_listener_required()')
            return True

        def set_control_element(self, control_element):
            if self._control_element != control_element:
                self._release_button()
                self._kill_all_tasks()
            super(FcbButtonControlBase.State, self).set_control_element(control_element)
            self._send_current_color()

        def _send_current_color(self):
            if self._control_element:
                if not self._enabled:
                    self._control_element.set_light(self.disabled_color)
                elif self.pressed_color is not None and self.is_pressed:
                    self._control_element.set_light(self.pressed_color)
                else:
                    self._send_button_color()

        def _send_button_color(self):
            raise NotImplementedError

        def _on_value(self, value, *a, **k):
            if self._notifications_enabled():
                if not self.is_momentary:
                    self._press_button()
                    self._release_button()
                elif value:
                    self._press_button()
                else:
                    self._release_button()
                (super(FcbButtonControlBase.State, self)._on_value)(value, *a, **k)
            self._send_current_color()

        def _press_button(self):
            is_pressed = self._is_pressed
            self._is_pressed = True
            if self._notifications_enabled():
                if not is_pressed:
                    self._on_pressed()

        def _on_pressed(self):
            if self._repeat:
                self._repeat_task.restart()
            self._call_listener('pressed')
            if self._has_delayed_event():
                self._delay_task.restart()
            self._check_double_click_press()

        def _release_button(self):
            is_pressed = self._is_pressed
            self._is_pressed = False
            if self._notifications_enabled():
                if is_pressed:
                    self._on_released()

        def _on_released(self):
            self._call_listener('released')
            if self._repeat:
                self._repeat_task.kill()
            if self._has_delayed_event():
                if self._delay_task.is_running:
                    self._call_listener('released_immediately')
                    self._delay_task.kill()
                else:
                    self._call_listener('released_delayed')
            self._check_double_click_release()

        def _check_double_click_press(self):
            if self._has_listener('double_clicked'):
                if not self._double_click_task.is_running:
                    self._double_click_task.restart()
                    self._double_click_context.click_count = 0
                if self._double_click_context.control_state != self:
                    self._double_click_context.set_new_context(self)

        def _check_double_click_release(self):
            if self._has_listener('double_clicked'):
                if self._double_click_task.is_running:
                    if self._double_click_context.control_state == self:
                        self._double_click_context.click_count += 1
                        if self._double_click_context.click_count == 2:
                            self._call_listener('double_clicked')
                            self._double_click_task.kill()

        def set_double_click_context(self, context):
            self._double_click_context = context

        @lazy_attribute
        def _delay_task(self):
            logger.info('in _delay_task()')
            return self.tasks.add(task.sequence(task.wait(self._delay_time), task.run(self._on_pressed_delayed)))

        @lazy_attribute
        def _repeat_task(self):
            logger.info('in _repeat_task()')
            notify_pressed = partial(self._call_listener, 'pressed')
            return self.tasks.add(task.sequence(task.wait(self._delay_time), task.loop(task.wait(ButtonControlBase.REPEAT_RATE), task.run(notify_pressed))))

        def _kill_all_tasks(self):
            logger.info('in _kill_all_tasks()')
            if self._repeat:
                self._repeat_task.kill()
            if self._has_delayed_event():
                self._delay_task.kill()

        @lazy_attribute
        def _double_click_task(self):
            logger.info('in _double_click_task()')
            return self.tasks.add(task.wait(ButtonControlBase.DOUBLE_CLICK_TIME))

        def _has_delayed_event(self):
            return self._has_listener('pressed_delayed') or self._has_listener('released_delayed') or self._has_listener('released_immediately')

        def _on_pressed_delayed(self):
            if self._is_pressed:
                self._call_listener('pressed_delayed')

        def update(self):
            self._send_current_color()

    def __init__(self, *a, **k):
        super(FcbButtonControlBase, self).__init__(extra_args=a, extra_kws=k)

class FcbSwitchControl(FcbButtonControlBase):

    class State(FcbButtonControlBase.State):
        color = control_color('DefaultButton.On')
        on_color = control_color(None)


        def __init__(self, *args, color=None, on_color=None, **kwargs):
            logger.info('in __init__()')
            super().__init__(*args, **kwargs)
            if color is not None:
                self.color = color
            if on_color is not None:
                self.on_color = on_color
            self._is_on = False


        @property
        def is_on(self):
            logger.info('in is_on().property')
            return self._is_on


        @is_on.setter
        def is_on(self, is_on):
            logger.info('in is_on().setter')
            self._is_on = is_on
            self._send_current_color()


        def _send_button_color(self):
            logger.debug('in _send_button_color()')
            if self.on_color is not None and self.is_on:
                self._control_element.set_light(self.on_color)
            else:
                self._control_element.set_light(self.color)
                
                
        def _on_pressed(self):
            logger.info('in _on_pressed()')
            super(FcbSwitchControl.State, self)._on_pressed()


        def _on_released(self):
            logger.info('in _on_released()')
            super(FcbSwitchControl.State, self)._on_released()


    def __init__(self, *args, **kwargs):
        logger.info('in __init__()')
        super(FcbSwitchControl, self).__init__(*args, **kwargs)


class FcbMappableSwitch(EventObject):

    def __init__(self, *a, **k):
        logger.info('in __init__()')
        super().__init__(*a, **k)
        self._parameter = None

    def disconnect(self):
        logger.info('in disconnect()')
        self._parameter = None
        super(FcbMappableSwitch, self).disconnect()

    @property
    def mapped_parameter(self):
        logger.info('in mapped_parameter().property')
        return self._parameter

    @mapped_parameter.setter
    def mapped_parameter(self, parameter):
        logger.info('in mapped_parameter().setter')
        self._parameter = parameter if liveobj_valid(parameter) else None
        self.enabled = self._parameter is not None
        self._FcbMappableSwitch__on_parameter_value_changed.subject = self._parameter
        self._FcbMappableSwitch__on_parameter_value_changed()

    @listens('value')
    def __on_parameter_value_changed(self):
        logger.info('in __on_parameter_value_changed().listens.value')
        self.is_on = liveobj_valid(self._parameter) and self._parameter.value


class FcbMappedSwitchControl(FcbSwitchControl):

    class State(FcbSwitchControl.State, FcbMappableSwitch):

        def __init__(self, *args, **kwargs):
            logger.info('FcbMappedSwitchControl.State in __init__()')
            super(FcbMappedSwitchControl.State, self).__init__(*args, **kwargs)
            self.enabled = False


        def _call_listener(self, listener_name, *args, **kwargs):
            logger.info('in _call_listener()')
            if listener_name == 'pressed':
                toggle_or_cycle_parameter_value(self.mapped_parameter)


    def __init__(self, *args, **kwargs):
        logger.info('FcbMappedSwitchControl in __init__()')
        super().__init__(*args, **kwargs)

