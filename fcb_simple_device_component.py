
from __future__ import absolute_import, print_function, unicode_literals
from future.moves.itertools import zip_longest
from _Generic.Devices import best_of_parameter_bank, parameter_banks
from ableton.v2.base import EventObject, clamp, depends, listens, liveobj_valid, nop
from ableton.v2.control_surface import Component
from ableton.v2.control_surface.control import ToggleButtonControl
from .fixed_radio_button_group import FixedRadioButtonGroup
from .fcb_switch_control import FcbMappedSwitchControl
from .fcb_live_api_utils import release_control, collect_devices
import logging
logger = logging.getLogger(__name__)


class FcbSimpleDeviceParameterComponent(Component):
    bank_select_buttons = FixedRadioButtonGroup(control_count=2,
      unchecked_color='Mode.Device.Bank.Available',
      checked_color='Mode.Device.Bank.Selected')
    device_lock_button = ToggleButtonControl()
    # device_on_off_control = FcbMappedSwitchControl(color='Device.Off', on_color='Device.On')

    @depends(device_provider=None)
    def __init__(self, device_provider=None, device_bank_registry=None, toggle_lock=None, use_parameter_banks=False, *a, **k):
        super().__init__(*a, **k)
        self._toggle_lock = toggle_lock
        self._use_parameter_banks = use_parameter_banks
        self._device = None
        self._banks = []
        self._bank_index = 0
        self._parameter_controls = None
        self._on_off_control = None
        self._empty_control_slots = self.register_disconnectable(EventObject())
        self._device_bank_registry = device_bank_registry
        self._device_provider = device_provider
        self._FcbSimpleDeviceParameterComponent__on_provided_device_changed.subject = device_provider
        self._FcbSimpleDeviceParameterComponent__on_provided_device_changed()
        if toggle_lock:
            self._FcbSimpleDeviceParameterComponent__on_is_locked_to_device_changed.subject = self._device_provider
            self._FcbSimpleDeviceParameterComponent__on_is_locked_to_device_changed()

    @bank_select_buttons.checked
    def bank_select_buttons(self, button):
        logger.debug('bank_select_buttons().checked')
        self._on_bank_select_button_checked(button)

    def _on_bank_select_button_checked(self, button):
        logger.debug('_on_bank_select_button_checked()')
        self.bank_index = button.index

    @bank_select_buttons.value
    def bank_select_buttons(self, value, _):
        logger.debug('bank_select_buttons()')
        if not value:
            self._on_bank_select_button_released()

    def _on_bank_select_button_released(self):
        logger.debug('_on_bank_select_button_released()')
        pass

    @device_lock_button.toggled
    def device_lock_button(self, *_):
        logger.debug('device_lock_button().toggled')
        self._on_device_lock_button_toggled()

    def _on_device_lock_button_toggled(self):
        logger.debug('_on_device_lock_button_toggled()')
        self._toggle_lock()
        self._update_device_lock_button()

    @property
    def bank_index(self):
        logger.debug('bank_index.property()')
        if self._use_parameter_banks:
            return self._bank_index
        return 0

    @bank_index.setter
    def bank_index(self, value):
        logger.debug('bank_index.setter()')
        self._bank_index = self._clamp_to_bank_size(value)
        if self._device_bank_registry:
            self._device_bank_registry.set_device_bank(self._device, self._bank_index)
        self.update()

    def _clamp_to_bank_size(self, value):
        logger.debug('_clamp_to_bank_size()')
        return clamp(value, 0, self.num_banks - 1)

    @property
    def selected_bank(self):
        logger.debug('selected_bank().property')
        if self.num_banks:
            return self._banks[(self._bank_index or 0)]
        return []

    @property
    def num_banks(self):
        logger.debug('num_banks().property')
        return len(self._banks)


    def set_parameter_controls(self, controls):
        logger.debug('set_parameter_controls()')
        for control in self._parameter_controls or []:
            release_control(control)

        self._parameter_controls = controls
        self.update()

    def set_on_off_control(self, control):
        if control != self._on_off_control:
            release_control(self._on_off_control)
            self._on_off_control = control
            self.update()


    @listens('device')
    def __on_provided_device_changed(self):
        logger.info('__on_provided_device_changed().listens')

        for control in self._parameter_controls or []:
            release_control(control)

        self._device = self._device_provider.device
        self._FcbSimpleDeviceParameterComponent__on_bank_changed.subject = self._device_bank_registry
        if self._device_bank_registry:
            self._bank_index = self._device_bank_registry.get_device_bank(self._device)
            self.update()
        else:
            self.bank_index = 0


    @listens('device_bank')
    def __on_bank_changed(self, device, bank):
        logger.debug('__on_bank_changed().listens')
        if device == self._device:
            self.bank_index = bank


    @listens('is_locked_to_device')
    def __on_is_locked_to_device_changed(self):
        logger.debug('__on_is_locked_to_device_changed().listens')
        self._update_device_lock_button()


    def update(self):
        logger.info('update()')
        super(FcbSimpleDeviceParameterComponent, self).update()
        if self.is_enabled():
            self._update_parameter_banks()
            self._update_bank_select_buttons()
            self._empty_control_slots.disconnect()
            if liveobj_valid(self._device):
                self._connect_parameters()
            else:
                self._disconnect_parameters()
        else:
            self._disconnect_parameters()


    def _disconnect_parameters(self):
        logger.debug('_disconnect_parameters()')
        for control in self._parameter_controls or []:
            release_control(control)
            self._empty_control_slots.register_slot(control, nop, 'value')
        # self.device_on_off_button.mapped_parameter = None
        self._on_off_control = None



    def _connect_parameters(self):
        logger.debug('_connect_parameters()')
        for control, parameter in zip_longest(self._parameter_controls or [], self.selected_bank):
            if liveobj_valid(control):
                if liveobj_valid(parameter):
                    control.connect_to(parameter)
                else:
                    control.release_parameter()
                    self._empty_control_slots.register_slot(control, nop, 'value')
        # self.device_on_off_button.mapped_parameter = self._on_off_parameter()
        if liveobj_valid(self._on_off_control):
            parameter = self._on_off_parameter()
            if liveobj_valid(parameter):
                self._on_off_control.connect_to(parameter)



    def _on_off_parameter(self):
        if liveobj_valid(self._device):
            for p in self._device.parameters:
                if p.name.startswith('Device On'):
                    if liveobj_valid(p):
                        if p.is_enabled:
                            return p


    def _update_parameter_banks(self):
        logger.debug('_update_parameter_banks()')
        if liveobj_valid(self._device):
            if self._use_parameter_banks:
                self._banks = parameter_banks(self._device)
            else:
                self._banks = [
                 best_of_parameter_bank(self._device)]
        else:
            self._banks = []
        self._bank_index = self._clamp_to_bank_size(self._bank_index)


    def _update_bank_select_buttons(self):
        logger.debug('_update_bank_select_buttons()')
        self.bank_select_buttons.active_control_count = self.num_banks
        if self.bank_index < self.num_banks:
            self.bank_select_buttons[self.bank_index].is_checked = True


    def _update_device_lock_button(self):
        logger.debug('_update_device_lock_button()')
        self.device_lock_button.is_toggled = self._device_provider.is_locked_to_device