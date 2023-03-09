
from __future__ import absolute_import, print_function, unicode_literals
from future.moves.itertools import zip_longest
import Live
import logging
from ableton.v2.base import listens, liveobj_valid
from ableton.v2.control_surface import Component, device_to_appoint
from ableton.v2.control_surface.control import ButtonControl
from ableton.v2.control_surface.components import FlattenedDeviceChain

from .my_switch_control import MySwitchControl
from .my_live_api_utils import release_control, collect_devices

logger = logging.getLogger(__name__)
import pprint

DEVICE_SLOTS = 4
NavDirection = Live.Application.Application.View.NavDirection


class MySimpleDeviceNavigationComponent(Component):
    """A class for left/right navigation of the device chain"""

    next_button = MySwitchControl()
    prev_button = MySwitchControl()


    def __init__(self, *args, **keywords):
        logger.info('in __init()__')
        (super(MySimpleDeviceNavigationComponent, self).__init__)(*args, **keywords)
        self._MySimpleDeviceNavigationComponent__on_selected_track_changed.subject = self.song.view

    # @next_button.released
    # def next_button(self, button):
    #     logger.info('in next_button().released')
    #     pass

    # the released_immediately and released_delayed functions throw an error!
    # @next_button.released_immediately
    # def next_button(self, value):
    #     logger.info('in next_button().released_immediately')
    #     pass

    # @next_button.released_delayed
    # def next_button(self, value):
    #     logger.info('in next_button().released_delayed')
    #     pass

    @next_button.pressed
    def next_button(self, value):
        logger.info('in next_button().pressed')
        self._scroll_device_chain(NavDirection.right)

    # @next_button.pressed_delayed
    # def next_button(self, value):
    #     logger.info('in next_button().pressed_delayed')
    #     pass

    # @prev_button.released
    # def prev_button(self, button):
    #     logger.info('in prev_button().released')
    #     pass

    # @prev_button.released_immediately
    # def prev_button(self, value):
    #     logger.info('in prev_button().released_immediately')
    #     pass

    # @prev_button.released_delayed
    # def prev_button(self, value):
    #     logger.info('in prev_button().released_delayed')
    #     pass

    @prev_button.pressed
    def prev_button(self, value):
        logger.info('in prev_button().pressed')
        self._scroll_device_chain(NavDirection.left)

    # @prev_button.pressed_delayed
    # def prev_button(self, value):
    #     logger.info('in prev_button().pressed_delayed')
    #     pass



    def _scroll_device_chain(self, direction):
        logger.info('in _scroll_device_chain()')
        view = self.application.view
        if not (view.is_view_visible('Detail') and view.is_view_visible('Detail/DeviceChain')):
            view.show_view('Detail')
            view.show_view('Detail/DeviceChain')
        else:
            view.scroll_view(direction, 'Detail/DeviceChain', False)


    def _current_track(self):
        logger.info('in _current_track()')
        return self.song.view.selected_track


    def _update_selected_track(self):
        logger.info('in _update_selected_track()')
        self._selected_track = self.song.view.selected_track


    @listens('device')
    def __on_device_changed(self):
        logger.info('in __on_device_changed()')
        pass


    @listens('selected_track')
    def __on_selected_track_changed(self):
        logger.info('in __on_selected_track_changed().listens')
        self._update_selected_track()



    # @listens('selected_device')
    # def _device_selection_in_track_changed(self):
    #     logger.info('in _device_selection_in_track_changed()')
    #     new_selection = self.song.view.selected_track.view.selected_device
    #     self._update_item_provider(new_selection)


    # def _update_item_provider(self, selection):
    #     logger.info('in _device_selection_in_track_changed()')
    #     self._flattened_chain.selected_item = selection