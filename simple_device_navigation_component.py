
from __future__ import absolute_import, print_function, unicode_literals
import Live
import logging
from ableton.v2.base import listens
from ableton.v2.control_surface import Component, device_to_appoint
from ableton.v2.control_surface.control import ButtonControl
from ableton.v2.control_surface.components import FlattenedDeviceChain
from ableton.v2.control_surface.components.item_lister import ItemListerComponent, ItemProvider

logger = logging.getLogger(__name__)
import pprint

NavDirection = Live.Application.Application.View.NavDirection


class SimpleDeviceNavigationComponent(ItemListerComponent):
    next_button = ButtonControl(color='Device.Navigation',
      pressed_color='Device.NavigationPressed')
    prev_button = ButtonControl(color='Device.Navigation',
      pressed_color='Device.NavigationPressed')

    def __init__(self, *args, device_component=None, item_provider=None, **keywords):
        logger.info('in __init()__')
        self._device_component = device_component


    @next_button.pressed
    def next_button(self, value):
        self._scroll_device_chain(NavDirection.right)

    @prev_button.pressed
    def prev_button(self, value):
        self._scroll_device_chain(NavDirection.left)

    def _scroll_device_chain(self, direction):
        logger.info('in _scroll_device_chain()')
        view = self.application.view
        if not (view.is_view_visible('Detail') and view.is_view_visible('Detail/DeviceChain')):
            view.show_view('Detail')
            view.show_view('Detail/DeviceChain')
        else:
            view.scroll_view(direction, 'Detail/DeviceChain', False)


    @listens('device')
    def __on_device_changed(self):
        logger.info('in __on_device_changed()')
        # self._update_device()


    def _update_device(self):
        logger.info('in _update_device()')
        self._update_item_provider(self._device_component.device())


    @listens('selected_device')
    def _device_selection_in_track_changed(self):
        logger.info('in _device_selection_in_track_changed()')
        new_selection = self.song.view.selected_track.view.selected_device
        self._update_item_provider(new_selection)


    def _update_item_provider(self, selection):
        logger.info('in _device_selection_in_track_changed()')
        self._flattened_chain.selected_item = selection