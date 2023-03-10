
from __future__ import absolute_import, print_function, unicode_literals
from future.moves.itertools import zip_longest
import Live
import logging
from ableton.v2.base import listens, liveobj_valid
from ableton.v2.control_surface import Component, device_to_appoint
from ableton.v2.control_surface.control import ButtonControl
from ableton.v2.control_surface.components import FlattenedDeviceChain

from .my_switch_control import MySwitchControl, MyMappedSwitchControl
from .my_live_api_utils import release_control, collect_devices

logger = logging.getLogger(__name__)
import pprint

DEVICE_SLOTS = 4
NavDirection = Live.Application.Application.View.NavDirection

def on_off_parameter(device):
        logger.info('in on_off_parameter()')
        if liveobj_valid(device):
            for p in device.parameters:
                if p.name.startswith('Device On'):
                    if liveobj_valid(p):
                        if p.is_enabled:
                            logger.info('in on_off_parameter() valid and enabled')
                            return p
                        
class MySimpleDeviceNavigationComponent(Component):
    """A class for left/right navigation of the device chain"""

    next_button = MySwitchControl()
    prev_button = MySwitchControl()
    on_off_control_1 = MyMappedSwitchControl(color='Device.Off', on_color='Device.On')
    on_off_control_2 = MyMappedSwitchControl(color='Device.Off', on_color='Device.On')
    on_off_control_3 = MyMappedSwitchControl(color='Device.Off', on_color='Device.On')
    on_off_control_4 = MyMappedSwitchControl(color='Device.Off', on_color='Device.On')

    def __init__(self, *args, **keywords):
        logger.info('in __init()__')
        (super(MySimpleDeviceNavigationComponent, self).__init__)(*args, **keywords)
        self._chain = []
        self._on_off_controls = [self.on_off_control_1, self.on_off_control_2, self.on_off_control_3, self.on_off_control_4]
        self._MySimpleDeviceNavigationComponent__on_selected_track_changed.subject = self.song.view


    @next_button.pressed
    def next_button(self, value):
        logger.info('in next_button().pressed')
        self._scroll_device_chain(NavDirection.right)

    @prev_button.pressed
    def prev_button(self, value):
        logger.info('in prev_button().pressed')
        self._scroll_device_chain(NavDirection.left)


    @on_off_control_1.pressed
    def on_off_control_1(self, value):
        logger.info('in on_off_control_1().pressed')
        pass

    @on_off_control_2.pressed
    def on_off_control_2(self, value):
        logger.info('in on_off_control_2().pressed')
        pass

    @on_off_control_3.pressed
    def on_off_control_3(self, value):
        logger.info('in on_off_control_3().pressed')
        pass

    @on_off_control_4.pressed
    def on_off_control_4(self, value):
        logger.info('in on_off_control_4().pressed')
        pass

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

    """#TODO: when a track is changed we need to attach the on/off button matrix to 
    the devices in the chain.
    1. discover chain
    2. release existing devices and buttons/controls
    3. connect the devices in the chain to the on/off buttons/controls"""
    def _update_selected_track(self):
        logger.info('in _update_selected_track()')
        self._selected_track = self.song.view.selected_track
        self._update_track_device_chain()

    """#TODO: Add some code to deal with a device change. This will unhook the device
    on/off buttons and re-attach the on-off buttons of the new device"""
    @listens('device')
    def __on_device_changed(self):
        logger.info('in __on_device_changed()')
        pass


    @listens('selected_track')
    def __on_selected_track_changed(self):
        logger.info('in __on_selected_track_changed().listens')
        self._update_selected_track()


    def _update_track_device_chain(self):
        logger.info('in _update_track_device_chain()')
        self._chain = collect_devices(self._selected_track)
        self._print_device_chain()
        for control in self._on_off_controls:
            control.mapped_parameter = None
        self.update()


    def _print_device_chain(self):
        for index, (device, nesting_level) in enumerate(self._chain):
            dev_class = getattr(device, 'class_name', "No class")
            dev_name = getattr(device, 'name', "No name")
            dev_type = getattr(device, 'type', "No name")
            logger.info('index: {} chain/device: \n\tname: {}, \n\ttype: {}, \n\tclass {}\n\tlevel: {}'.format(index, dev_name, dev_type, dev_class, nesting_level))
            parameter = on_off_parameter(device)


    def update(self):
        logger.info('update()')
        super(MySimpleDeviceNavigationComponent, self).update()
        self._connect_on_off_parameters()


    def _connect_on_off_parameters(self):
        logger.debug('_connect_on_off_parameters()')
        if len(self._chain) > 0:
            for (device, nesting_level), control in zip(self._chain, self._on_off_controls):
                if device:
                    if ((control is not None) and liveobj_valid(control) and liveobj_valid(device)):
                        parameter = on_off_parameter(device)
                        if liveobj_valid(parameter):
                                control.mapped_parameter = parameter

    # @listens('selected_device')
    # def _device_selection_in_track_changed(self):
    #     logger.info('in _device_selection_in_track_changed()')
    #     new_selection = self.song.view.selected_track.view.selected_device
    #     self._update_item_provider(new_selection)


    # def _update_item_provider(self, selection):
    #     logger.info('in _device_selection_in_track_changed()')
    #     self._flattened_chain.selected_item = selection