
from __future__ import absolute_import, print_function, unicode_literals
from ableton.v2.base import EventObject, listens, liveobj_valid
from ableton.v2.control_surface.control import ButtonControl, ButtonControlBase, control_color

from .my_live_api_utils import toggle_or_cycle_parameter_value

import logging
logger = logging.getLogger(__name__)


class MySwitchControl(ButtonControl):

    class State(ButtonControl.State):
        color = control_color('DefaultButton.On')
        on_color = control_color(None)


        def __init__(self, *args, color=None, on_color=None, **kwargs):
            logger.info('in __init__()')
            (super(MySwitchControl.State, self).__init__)(*args, **kwargs)
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
            logger.debug('in _on_pressed()')
            super(MySwitchControl.State, self)._on_pressed()


        def _on_released(self):
            logger.debug('in _on_released()')
            super(MySwitchControl.State, self)._on_released()


    def __init__(self, *args, **kwargs):
        logger.info('in __init__()')
        (super(MySwitchControl, self).__init__)(*args, **kwargs)


class MyMappableSwitch(EventObject):

    def __init__(self, *a, **k):
        logger.info('in __init__()')
        (super().__init__)(*a, **k)
        self._parameter = None

    def disconnect(self):
        logger.info('in disconnect()')
        self._parameter = None
        super().disconnect()

    @property
    def mapped_parameter(self):
        logger.info('in mapped_parameter().property')
        return self._parameter

    @mapped_parameter.setter
    def mapped_parameter(self, parameter):
        logger.info('in mapped_parameter().setter')
        self._parameter = parameter if liveobj_valid(parameter) else None
        self.enabled = self._parameter is not None
        self._MyMappableSwitch__on_parameter_value_changed.subject = self._parameter
        self._MyMappableSwitch__on_parameter_value_changed()

    @listens('value')
    def __on_parameter_value_changed(self):
        logger.info('in __on_parameter_value_changed().listens.value')
        self.is_on = liveobj_valid(self._parameter) and self._parameter.value


class MyMappedSwitchControl(MySwitchControl):

    class State(MySwitchControl.State, MyMappableSwitch):

        def __init__(self, *a, **k):
            logger.info('in __init__()')
            (super().__init__)(*a, **k)
            self.enabled = False


        def _call_listener(self, listener_name, *_):
            logger.info('in _call_listener()')
            if listener_name == 'pressed':
                toggle_or_cycle_parameter_value(self.mapped_parameter)
