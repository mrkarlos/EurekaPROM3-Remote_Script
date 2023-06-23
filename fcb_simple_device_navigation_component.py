
from __future__ import absolute_import, print_function, unicode_literals
from future.moves.itertools import zip_longest
import Live
import logging, re
from ableton.v2.base import listens, liveobj_valid, index_if
from ableton.v2.control_surface import Component, device_to_appoint
from ableton.v2.control_surface.control import ButtonControl, control_list
from ableton.v2.control_surface.components import FlattenedDeviceChain

from .fcb_switch_control import FcbSwitchControl, FcbMappedSwitchControl
# from .fcb_blinking_button import FcbBlinkingButtonControl
from .fcb_live_api_utils import release_control, collect_devices

logger = logging.getLogger(__name__)

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
                        
class FcbSimpleDeviceNavigationComponent(Component):
    """A class for left/right navigation of the device chain"""

    next_button = FcbSwitchControl()
    prev_button = FcbSwitchControl()
    on_off_control_1 = FcbMappedSwitchControl(color='Device.Off', on_color='Device.On')
    on_off_control_2 = FcbMappedSwitchControl(color='Device.Off', on_color='Device.On')
    on_off_control_3 = FcbMappedSwitchControl(color='Device.Off', on_color='Device.On')
    on_off_control_4 = FcbMappedSwitchControl(color='Device.Off', on_color='Device.On')
    on_off_control_5 = FcbMappedSwitchControl(color='Device.Off', on_color='Device.On')
    on_off_control_6 = FcbMappedSwitchControl(color='Device.Off', on_color='Device.On')
    on_off_control_7 = FcbMappedSwitchControl(color='Device.Off', on_color='Device.On')
    on_off_control_8 = FcbMappedSwitchControl(color='Device.Off', on_color='Device.On')
    on_off_control_9 = FcbMappedSwitchControl(color='Device.Off', on_color='Device.On')
    on_off_control_10 = FcbMappedSwitchControl(color='Device.Off', on_color='Device.On')
    on_off_control_11 = FcbMappedSwitchControl(color='Device.Off', on_color='Device.On')
    on_off_control_12 = FcbMappedSwitchControl(color='Device.Off', on_color='Device.On')

    def __init__(self, *args, **keywords):
        logger.info('in __init()__')
        super().__init__(*args, **keywords)
        self._chain = []
        self._labelled_chain = []
        self._devices = 0
        self._selected_device = None
        self._selected_device_index = None
        self._on_off_controls = [self.on_off_control_1, self.on_off_control_2, self.on_off_control_3, self.on_off_control_4,
                                 self.on_off_control_5, self.on_off_control_6, self.on_off_control_7, self.on_off_control_8,
                                 self.on_off_control_9, self.on_off_control_10, self.on_off_control_11, self.on_off_control_12
                                ]
        self._FcbSimpleDeviceNavigationComponent__on_selected_track_changed.subject = self.song.view
        self._FcbSimpleDeviceNavigationComponent__device_selection_in_track_changed.subject = self.song.view.selected_track.view


    @property
    def has_labelled_chain(self):
        return len(self._labelled_chain) > 0

    def set_device_on_off_buttons(self, buttons):
        logger.info('in set_device_on_off_buttons()')
        if buttons:
            for button, idx in zip(buttons, range(1, DEVICE_SLOTS)):
                control_name = 'on_off_control_{}'.format(idx)
                logger.info('in set_device_on_off_buttons(), setting control element for: {}'.format(control_name))
                control = getattr(self, control_name)
                control.set_control_element(button)


    @next_button.pressed
    def next_button(self, value):
        logger.info('in next_button().pressed')
        self._scroll_device_chain(NavDirection.right)

    @prev_button.pressed
    def prev_button(self, value):
        logger.info('in prev_button().pressed')
        self._scroll_device_chain(NavDirection.left)

    def _update_scroll_buttons(self):
        self.prev_button.enabled = self.can_scroll_down()
        self.next_button.enabled = self.can_scroll_up()

    def can_scroll_up(self):
        current_selected_device = self.song.view.selected_track.view.selected_device
        current_selected_device_index = index_if(lambda i: i[0] == current_selected_device, self._chain)
        logger.info('can_scroll_up - index: {} of {} devices'.format(current_selected_device_index, len(self._chain)))
        return current_selected_device_index < (len(self._chain) -1)

    def can_scroll_down(self):
        current_selected_device = self.song.view.selected_track.view.selected_device
        current_selected_device_index = index_if(lambda i: i[0] == current_selected_device, self._chain)
        logger.info('can_scroll_down - index: {} of {} devices'.format(current_selected_device_index, len(self._chain)))
        return current_selected_device_index > 0

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

        self._update_scroll_buttons()


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

    """#TODO: Add some code to deal with a device change. This should unhook the device
    on/off buttons and re-attach the on-off buttons of the new device"""
    # @listens('selected_device')
    # def __on_selected_device_changed(self):
    #     logger.info('in __on_device_changed().listens')
    #     pass


    @listens('selected_track')
    def __on_selected_track_changed(self):
        logger.info('in __on_selected_track_changed().listens')
        self._FcbSimpleDeviceNavigationComponent__device_selection_in_track_changed.subject = self.song.view.selected_track.view

        self._update_selected_track()


    def _update_track_device_chain(self):
        logger.info('in _update_track_device_chain()')
        self._chain = collect_devices(self._selected_track)
        self._update_track_device_labelled_chain()
        self._print_device_chain()
        self._print_device_labelled_chain()
        # unmap the parameters of the previous devices before an update
        for control in self._on_off_controls:
            control.mapped_parameter = None
        self.update()

    def _update_track_device_labelled_chain(self):
        logger.info('in _update_track_device_labelled_chain()')
        self._labelled_chain = []
        labelled_chain = []
        for index, (device, _) in enumerate(self._chain):
            dev_name = getattr(device, 'name', "No name")

            match = re.search(r"\[B(\d+)\]$", dev_name)
            if match:
                num_str = match.group(1)
                logger.info('  postfix: {}'.format(num_str))
                num = int(num_str)
                logger.info('    num: {}'.format(num))
                if 1 <= num <= 12:
                    labelled_chain.append((device, num))

        self._labelled_chain = sorted(labelled_chain, key=lambda x: x[1])  # Sort based on the second element of each tuple



    def _print_device_chain(self):
        logger.info('in _print_device_chain()')
        for index, (device, nesting_level) in enumerate(self._chain):
            dev_class = getattr(device, 'class_name', "No class")
            dev_name = getattr(device, 'name', "No name")
            dev_type = getattr(device, 'type', "No name")
            logger.info('index: {} chain/device: \n\tname: {}, \n\ttype: {}, \n\tclass {}\n\tlevel: {}'.format(index, dev_name, dev_type, dev_class, nesting_level))

    def _print_device_labelled_chain(self):
        logger.info('in _print_device_labelled_chain()')
        if self.has_labelled_chain:
            for index, (device, position) in enumerate(self._labelled_chain):
                dev_class = getattr(device, 'class_name', "No class")
                dev_name = getattr(device, 'name', "No name")
                dev_type = getattr(device, 'type', "No name")
                logger.info('index: {} chain/device: \n\tname: {}, \n\ttype: {}, \n\tclass {}\n\tpostion: {}'.format(index, dev_name, dev_type, dev_class, position))
        else:
            logger.info('No labelled chain info defined in the device names')


    def update(self):
        logger.info('update()')
        super(FcbSimpleDeviceNavigationComponent, self).update()
        self._connect_on_off_parameters()
        self._update_scroll_buttons()


    def _connect_on_off_parameters(self):
        logger.debug('_connect_on_off_parameters()')
        if len(self._chain) > 0:
            for (device, nesting_level), control in zip(self._chain, self._on_off_controls):
                if device:
                    if ((control is not None) and liveobj_valid(control) and liveobj_valid(device)):
                        parameter = on_off_parameter(device)
                        if liveobj_valid(parameter):
                                control.mapped_parameter = parameter

    @listens('selected_device')
    def __device_selection_in_track_changed(self):
        logger.info('in _device_selection_in_track_changed()')
        self._update_selected_track()
