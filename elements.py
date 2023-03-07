# decompyle3 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.8.9 (default, Mar 30 2022, 13:51:17) 
# [Clang 13.1.6 (clang-1316.0.21.2.3)]
# Embedded file name: output/Live/mac_64_static/Release/python-bundle/MIDI Remote Scripts/FANTOM/elements.py
# Compiled at: 2022-01-27 16:28:16
# Size of source mod 2**32: 4870 bytes
from __future__ import absolute_import, print_function, unicode_literals
from ableton.v3.control_surface import MIDI_NOTE_TYPE, ElementsBase, MapMode, PrioritizedResource, create_matrix_identifiers
# from . import sysex
# from .ringed_encoder import RingedEncoderElement
# from .scene_name_display import SceneNameDisplayElement
# from .simple_display import SimpleDisplayElement
# from .track_info_display import TrackInfoDisplayElement
NUM_TRACKS = 4
NUM_SCENES = 1
SESSION_WIDTH = 4
SESSION_HEIGHT = 1


def create_display_element(header, name=None):
    return SimpleDisplayElement(header, (0, sysex.SYSEX_END_BYTE), name=name)


class Elements(ElementsBase):

    def __init__(self, *a, **k):
        (super().__init__)(*a, **k)
        self.add_button(1, 'up_button')
        self.add_button(2, 'down_button')
        self.add_button(3, 'left_button')
        self.add_button(4, 'right_button')
        self.add_button(64, 'stop_all_clips_button')
        self.add_button(80, 'play_button')
        self.add_button(81, 'stop_button')
        self.add_button(82, 'record_button')
        self.add_button(83, 'undo_Button')
        self.add_button(84, 'metronome_button')
        self.add_button(85, 'session_record_button')
        self.add_button(86, 'Capture_midi_button')
        self.add_button(87, 'automation_re-enable_button')
        self.add_button(88, 'automation_arm_button')
        self.add_button(89, 'arrangement_overdub_button')
        self.add_button(91, 'tap_tempo_button')

        # track_channels = [i + 1 for i in range(NUM_TRACKS)]
        # self.add_button_matrix([
        #  [
        #   67] * NUM_TRACKS],
        #   'Mute_Buttons', channels=[track_channels])

        self.add_encoder(34, 'Tempo_Coarse_Control', map_mode=(MapMode.LinearBinaryOffset))
        self.add_encoder(35, 'Tempo_Fine_Control', map_mode=(MapMode.LinearBinaryOffset))
        self.add_encoder(72, 'Master_Pan_Control')
        self.add_encoder(73, 'Master_Volume_Control')
        self.add_encoder(96, 'Track_Select_Control', resource_type=PrioritizedResource)

        # self.add_matrix([
        #  [i + 16 for i in range(8)]],
        #   'Device_Controls',
        #   element_factory=RingedEncoderElement)
        # self.add_encoder_matrix([
        #  [
        #   72] * NUM_TRACKS],
        #   'Pan_Controls',
        #   channels=[
        #  track_channels],
        #   needs_takeover=False)

        # self.add_submatrix((self.send_controls), 'Send_A_Controls', rows=(0, 1))
        # self.add_submatrix((self.send_controls), 'Send_B_Controls', rows=(1, 2))

        # self.add_element('Beat Time Display', create_display_element, sysex.BEAT_TIME_DISPLAY_HEADER)
        # self.add_element('Tempo Display', create_display_element, sysex.TEMPO_DISPLAY_HEADER)
        # self.add_element('Track_Info_Display', TrackInfoDisplayElement, sysex.TRACK_INFO_DISPLAY_HEADER, (
        #  sysex.SYSEX_END_BYTE,))
        # self.add_element('Scene_Name_Display', SceneNameDisplayElement, sysex.SCENE_NAME_DISPLAY_HEADER, (
        #  sysex.SYSEX_END_BYTE,))

    def add_encoder(self, *a, **k):
        (super().add_encoder)(*a, needs_takeover=False, **k)