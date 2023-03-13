
from __future__ import absolute_import, print_function, unicode_literals
from builtins import object, range, str
import Live
import time
import logging
from ableton.v2.base import listens, inject, const, depends
from ableton.v2.control_surface import MIDI_CC_TYPE, MIDI_NOTE_TYPE, ControlSurface, Layer
from ableton.v2.control_surface.components import TransportComponent, MixerComponent, ViewControlComponent, SessionComponent, SessionRingComponent, SessionNavigationComponent, SimpleTrackAssigner, ChannelStripComponent, ClipSlotComponent, SceneComponent
from ableton.v2.control_surface.elements import ButtonElement, EncoderElement, ButtonMatrixElement
from ableton.v2.control_surface import midi
from ableton.v2.control_surface.control import ButtonControl
from ableton.v2.control_surface.mode import LayerMode, AddLayerMode, EnablingMode, SetAttributeMode, ModesComponent, MomentaryBehaviour, LatchingBehaviour

from .my_button_element import MyButtonElement
from .my_modes_component import MyModesComponent
from .my_session_component import MySessionComponent
from .my_session_navigation_component import MySessionNavigationComponent
from .my_channel_strip_component import MyChannelStripComponent
from .consts import *
from .skin import skin
from .elements import SESSION_WIDTH, SESSION_HEIGHT, NUM_SCENES, NUM_TRACKS, Elements
from .my_simple_device_component import MySimpleDeviceParameterComponent
from .my_simple_device_navigation_component import MySimpleDeviceNavigationComponent
from .simple_display import SimpleDisplayElement

logger = logging.getLogger(__name__)
import pprint


""" Here we define some global variables """
CHANNEL = 0 # Channels are numbered 0 through 15, this script only makes use of one MIDI Channel (Channel 1)
PEDAL_MODE_NAME = 'Pedal_Modes'
PEDAL_MODE_LAUNCH_MODE_NAME = 'pedal_launch'
PEDAL_MODE_TRACK_MODE_NAME = 'track_launch'

@depends(skin=None)
def create_button(identifier, name, channel=CHANNEL, skin=None):
    return MyButtonElement(True, MIDI_CC_TYPE, channel, identifier, name=name, skin=skin)

@depends(skin=None)
def create_toggle_button(identifier, name, channel=CHANNEL, skin=None):
    return MyButtonElement(False, MIDI_CC_TYPE, channel, identifier, name=name, skin=skin)


class AAA(ControlSurface):

    def __init__(self, *args, **kwargs):
        (super(AAA, self).__init__)(*args, **kwargs)
        self._current_pedal_mode = ''
        self._current_session_mode = ''
        self._current_track_mode = ''

        with self.component_guard():
            with inject(skin=(const(skin))).everywhere():
                self._create_controls()
        with self.component_guard():
            self._create_session()
            self._create_vertical_session()
            self._create_view_control()
            self._create_mixer()
            self._create_transport()
            self._create_device_parameters()
            self._create_device_navigation()
            # self._create_session_modes()
            self._create_track_modes()
            # self._create_pedal_modes()


        """ Here is some Live API stuff just for fun """
        app = Live.Application.get_application() # get a handle to the App
        maj = app.get_major_version() # get the major version from the App
        min = app.get_minor_version() # get the minor version from the App
        bug = app.get_bugfix_version() # get the bugfix version from the App
        self.show_message(str(maj) + "." + str(min) + "." + str(bug)) #put them together and use the ControlSurface show_message method to output version info to console

        self.fcb1010_display_modes()

        logger.info('Completed init')


    def _create_controls(self):
        logger.info('in _create_controls()')

        is_momentary = True # We'll only be using momentary buttons here

        # Main Buttons
        self._button_1 = create_button(104, name='Button_1')
        self._button_2 = create_button(105, name='Button_2')
        self._button_3 = create_button(101, name='Button_3')
        self._button_4 = create_button(100, name='Button_4')
        self._button_5 = create_button(99, name='Button_5')
        self._button_6 = create_button(98, name='Button_6')
        self._button_7 = create_button(97, name='Button_7')
        self._button_8 = create_button(96, name='Button_8')
        self._button_9 = create_button(95, name='Button_9')
        self._button_0 = create_button(94, name='Button_0')
        self._button_up = create_button(93, name='Button_Up')
        self._button_down = create_button(92, name='Button_Down')

        # Two Foot Pedals
        self._pedal_a = EncoderElement(MIDI_CC_TYPE, CHANNEL, 102, Live.MidiMap.MapMode.absolute, name="Pedal_A")
        self._pedal_b = EncoderElement(MIDI_CC_TYPE, CHANNEL, 103, Live.MidiMap.MapMode.absolute, name="Pedal_B")
        pedal_pair_raw = [self._pedal_a, self._pedal_b]
        self.pedal_pair_matrix = ButtonMatrixElement(rows=[pedal_pair_raw], name='Pedal_Pair_Matrix')

        device_parameter_controls_raw = [self._pedal_a, self._pedal_b]
        self.device_parameter_controls = ButtonMatrixElement(rows=[device_parameter_controls_raw], name='Device_Parameter_Controls')
        device_on_off_button_matrix_raw = [self._button_1, self._button_2, self._button_3, self._button_4]
        self.device_on_off_buttons = ButtonMatrixElement(rows=[device_on_off_button_matrix_raw], name='Device_On_off_Buttons')

        # Clip launch config
        horizontal_clip_buttons_raw = [self._button_1, self._button_2, self._button_3, self._button_4]
        self.horizontal_clip_launch_matrix = ButtonMatrixElement(rows=[horizontal_clip_buttons_raw], name='Horizontal_Clip_Launch_Matrix')
        vertical_clip_buttons_raw = [[self._button_1], [self._button_2], [self._button_3], [self._button_4]]
        self.vertical_clip_launch_matrix = ButtonMatrixElement(rows=vertical_clip_buttons_raw, name='Vertical_Clip_Launch_Matrix')


    def _create_transport(self):
        logger.info('in _create_transport()')
        self._transport = TransportComponent(name='Transport')

        # self._session_recording = SessionRecordingComponent(name='Session_Recording')
        # self._session_recording.layer = Layer(record_button=(self._record_button),
        #     record_stop_button=(self._record_stop_button))

    def _create_pedal_modes(self):
        logger.info('in _create_pedal_modes()')

        self._pedal_modes = MyModesComponent(name=PEDAL_MODE_NAME,
          is_enabled=False,
          support_momentary_mode_cycling=True,
          layer=Layer(cycle_mode_button=(self._button_0)))

        self._pedal_modes.add_mode(PEDAL_MODE_LAUNCH_MODE_NAME, (
            EnablingMode((self._horizontal_session_ring)),
            AddLayerMode((self._session_modes), layer=Layer(cycle_mode_button=(self._button_5))),
            # EnablingMode((self._session_modes)),
            # LayerMode((self._track_modes), None),
          ),
          behaviour=(MomentaryBehaviour())
        ),
        self._pedal_modes.add_mode(PEDAL_MODE_TRACK_MODE_NAME, (
            EnablingMode((self._vertical_session_ring)),
            AddLayerMode((self._track_modes), layer=Layer(cycle_mode_button=(self._button_5))),
            # EnablingMode((self._track_modes)),
            # LayerMode((self._session_modes), None),
          ),
          behaviour=(MomentaryBehaviour())
        )
        self._pedal_modes.selected_mode = PEDAL_MODE_LAUNCH_MODE_NAME
        self._current_pedal_mode = self._pedal_modes.selected_mode
        self._pedal_modes.set_enabled(True)
        self._AAA__on_pedal_mode_changed.subject = self._pedal_modes

    def _create_session_modes(self):
        logger.info('in _create_session_modes()')

        self._session_modes = MyModesComponent(name='Session_Modes',
          is_enabled=False,
          support_momentary_mode_cycling=True,
          layer=Layer(cycle_mode_button=(self._button_5)))
        self._session_modes.add_mode('launch', ( 
              EnablingMode((self._horizontal_session_ring)),
              AddLayerMode((self._session), layer=self._create_session_layer()),
              AddLayerMode((self._mixer.selected_strip), layer=self._create_channel_strip_encoders_layer()),
              AddLayerMode(( self._horizontal_session_navigation), layer=self._create_session_navigation_up_down_layer()),
              AddLayerMode(( self._horizontal_session_navigation), layer=self._create_session_navigation_left_right_layer()),
            ),
            behaviour=(MomentaryBehaviour()) )
        self._session_modes.add_mode('mute', ( 
              EnablingMode((self._horizontal_session_ring)),
              AddLayerMode((self._mixer), layer=self._create_mute_layer()), 
              AddLayerMode((self._mixer.selected_strip), layer=self._create_channel_strip_encoders_layer()),
              AddLayerMode(( self._horizontal_session_navigation), layer=self._create_session_navigation_up_down_layer()),
              AddLayerMode(( self._horizontal_session_navigation), layer=self._create_session_navigation_left_right_layer()),
            ),
            behaviour=(MomentaryBehaviour())  )
        self._session_modes.add_mode('solo', ( 
              EnablingMode((self._horizontal_session_ring)),
              AddLayerMode((self._mixer), layer=self._create_solo_layer()),
              AddLayerMode((self._mixer.selected_strip), layer=self._create_channel_strip_encoders_layer()),
              AddLayerMode(( self._horizontal_session_navigation), layer=self._create_session_navigation_up_down_layer()),
              AddLayerMode(( self._horizontal_session_navigation), layer=self._create_session_navigation_left_right_layer()),
            ),
            behaviour=(MomentaryBehaviour()) )
        self._session_modes.add_mode('arm', (
              EnablingMode((self._horizontal_session_ring)),
              AddLayerMode((self._mixer), layer=self._create_arm_layer()),
              AddLayerMode((self._mixer.selected_strip), layer=self._create_channel_strip_encoders_layer()),
              AddLayerMode(( self._horizontal_session_navigation), layer=self._create_session_navigation_up_down_layer()),
              AddLayerMode(( self._horizontal_session_navigation), layer=self._create_session_navigation_left_right_layer()),
            ),
            behaviour=(MomentaryBehaviour()) )
        self._session_modes.add_mode('transport', (
            #   EnablingMode((self._horizontal_session_ring)),
              AddLayerMode((self._transport), layer=self._create_transport_control_layer()),
              AddLayerMode(( self._horizontal_session_navigation), layer=self._create_session_navigation_up_down_layer()),
              AddLayerMode(( self._horizontal_session_navigation), layer=self._create_session_navigation_left_right_layer()),
            ),
            behaviour=(MomentaryBehaviour()) )
        self._session_modes.selected_mode = 'launch'
        self._current_session_mode = self._session_modes.selected_mode
        self._session_modes.set_enabled(True)
        self._AAA__on_session_mode_changed.subject = self._session_modes


    def _create_track_modes(self):
        logger.info('in _create_track_modes()')

        self._track_modes = MyModesComponent(name='Track_Modes',
          is_enabled=False,
          support_momentary_mode_cycling=True,
          layer=Layer(cycle_mode_button=(self._button_5)))
        self._track_modes.add_mode('launch', ( 
              EnablingMode((self._vertical_session_ring)),
              AddLayerMode((self._vertical_session), layer=self._create_vertical_session_layer()),
              AddLayerMode((self._mixer.selected_strip), layer=self._create_channel_strip_encoders_layer()),
              AddLayerMode(( self._vertical_session_navigation), layer=self._create_session_navigation_up_down_layer()),
              AddLayerMode(( self._vertical_session_navigation), layer=self._create_session_navigation_left_right_layer()),
            ),
            behaviour=(MomentaryBehaviour()) )
        self._track_modes.add_mode('dev', (
              EnablingMode((self._vertical_session_ring)),
              AddLayerMode((self._device_parameters), layer=self._create_device_parameter_layer()),
              AddLayerMode((self._device_navigation), layer=self._create_device_navigation_layer()),
              AddLayerMode((self._device_navigation), layer=self._create_device_navigation_on_off_layer()),
              AddLayerMode(( self._vertical_session_navigation), layer=self._create_session_navigation_up_down_layer()),
            #   AddLayerMode(( self._horizontal_session_navigation), layer=self._create_session_navigation_left_right_layer()),
            ),
            behaviour=(MomentaryBehaviour()) )
        self._track_modes.add_mode('chan_strip', (
              EnablingMode((self._vertical_session_ring)),
              AddLayerMode((self._mixer.selected_strip), layer=self._create_channel_strip_buttons_layer()),
              AddLayerMode((self._mixer.selected_strip), layer=self._create_channel_strip_encoders_layer()),
              AddLayerMode(( self._vertical_session_navigation), layer=self._create_session_navigation_up_down_layer()),
              AddLayerMode(( self._vertical_session_navigation), layer=self._create_session_navigation_left_right_layer()),
            ),
            behaviour=(MomentaryBehaviour()) )
        self._track_modes.selected_mode = 'launch'
        self._current_track_mode = self._track_modes.selected_mode
        self._track_modes.set_enabled(True)
        self._AAA__on_track_mode_changed.subject = self._track_modes


    def _create_mixer(self):
        logger.info('in _create_mixer()')
        self._mixer = MixerComponent(name='Mixer',
          auto_name=True,
          tracks_provider=(self._horizontal_session_ring),
          track_assigner=(SimpleTrackAssigner()),
          invert_mute_feedback=True,
          channel_strip_component_type=MyChannelStripComponent)


    def _create_device_parameters(self):
        logger.info('in _create_device_parameters()')
        self._device_parameters = MySimpleDeviceParameterComponent(name='Device',
          is_enabled=False,
          layer=self._create_device_parameter_layer())
        self._device_parameters.set_enabled(True)


    def _create_device_navigation(self, device_component=None):
        logger.info('in _create_device_navigation()')
        self._device_navigation = MySimpleDeviceNavigationComponent(name='Device_Navigation',
        #   device_component=self._device_parameters,
          layer=self._create_device_navigation_layer())


    def _create_session(self):
        logger.info('in _create_session()')
        self._horizontal_session_ring = SessionRingComponent(name='Horizontal_Session_Ring',
          is_enabled=False,
          num_tracks=SESSION_WIDTH,
          num_scenes=SESSION_HEIGHT)
        self._session = MySessionComponent(name='Session',
          is_enabled=False,
          session_ring=(self._horizontal_session_ring))
        self._session.set_enabled(True)
        self._horizontal_session_navigation = MySessionNavigationComponent(name='Horizontal_Session_Navigation',
          is_enabled=False,
          session_ring=(self._horizontal_session_ring))
        self._horizontal_session_navigation.set_enabled(True)
        self._horizontal_session_ring.set_enabled(False)


    def _create_vertical_session(self):
        logger.info('in _create_vertical_session()')
        self._vertical_session_ring = SessionRingComponent(name='Vertical_Session_Ring',
          is_enabled=False,
          num_tracks=SESSION_HEIGHT,
          num_scenes=SESSION_WIDTH)
        self._vertical_session = MySessionComponent(name='Vertical_Session',
          is_enabled=False,
          session_ring=(self._vertical_session_ring))
        self._vertical_session.set_enabled(True)
        self._vertical_session_navigation = MySessionNavigationComponent(name='Vertical_Session_Navigation',
          is_enabled=False,
          session_ring=(self._vertical_session_ring))

        self._vertical_session_navigation.set_enabled(True)
        self._vertical_session_ring.set_enabled(True)


    def _create_horizontal_session_ring(self):
        self._horizontal_session_ring = SessionRingComponent(name='Horizontal_Session_Ring',
          is_enabled=False,
          num_tracks=SESSION_WIDTH,
          num_scenes=SESSION_HEIGHT)
    
    def _create_vertical_session_ring(self):
        self._vertical_session_ring = SessionRingComponent(name='Vertical_Session_Ring',
          is_enabled=False,
          num_tracks=SESSION_HEIGHT,
          num_scenes=SESSION_WIDTH)

    def get_horizontal_ring_offsets(self):
        return (self._horizontal_session_ring.track_offset, self._horizontal_session_ring.scene_offset)

    def get_vertical_ring_offsets(self):
        return (self._vertical_session_ring.track_offset, self._vertical_session_ring.scene_offset)


    def _create_session_layer(self):
        logger.info('in _create_session_layer()')
        return Layer(clip_launch_buttons=self.horizontal_clip_launch_matrix)


    def _create_vertical_session_layer(self):
        logger.info('in _create_vertical_session_layer()')
        return Layer(clip_launch_buttons=self.vertical_clip_launch_matrix)


    def _create_session_navigation_layer(self):
        logger.info('in _create_session_navigation_layer()')
        return Layer(
          up_button=self._button_up,
          down_button=self._button_down,
        #   up_down_button=self._button_0,
          left_button=self._button_8,
          right_button=self._button_9,
        #   left_right_button=self._button_9,
          )

    def _create_session_navigation_up_down_layer(self):
        logger.info('in _create_session_navigation_up_down_layer()')
        return Layer(up_button=self._button_up,
                     down_button=self._button_down)


    def _create_session_navigation_left_right_layer(self):
        logger.info('in _create_session_navigation_left_right_layer()')
        return Layer(left_button=self._button_8,
                     right_button=self._button_9)
     

    def _create_track_navigation_layer(self):
        logger.info('in _create_track_navigation_layer()')
        return Layer(prev_track_button=self._button_6,
                     next_track_button=self._button_7)


    def _create_device_navigation_layer(self):
        logger.info('in _create_device_navigation_layer()')
        return Layer(prev_button=self._button_8,
                     next_button=self._button_9)


    def _create_device_navigation_on_off_layer(self):
        logger.info('in _create_device_navigation_on_off_layer()')
        return Layer(on_off_control_1=self._button_1,
                     on_off_control_2=self._button_2,
                     on_off_control_3=self._button_3,
                     on_off_control_4=self._button_4,
                    )


    def _create_device_parameter_layer(self):
        logger.info('in _create_device_parameter_layer()')
        return Layer(parameter_controls=self.device_parameter_controls)


    def _create_channel_strip_buttons_layer(self):
        logger.info('in _create_channel_strip_buttons_layer()')
        return Layer(mute_button=self._button_1,
                     solo_button=self._button_2,
                     arm_button=self._button_3,
                     track_stop_button=self._button_4,
                    )


    def _create_channel_strip_encoders_layer(self):
        logger.info('in _create_channel_strip_encoders_layer()')
        return Layer(volume_control=self._pedal_a,
                     pan_control=self._pedal_b)
    

    def _create_transport_control_layer(self):
        logger.info('in _create_transport_control_layer()')
        return Layer(play_button=self._button_1,
                     stop_button=self._button_2,
                    record_button=self._button_3,
                    overdub_button=self._button_4,
                    )


    def _create_mute_layer(self):
        logger.info('in _create_mute_layer()')
        return Layer(mute_buttons=self.horizontal_clip_launch_matrix)


    def _create_solo_layer(self):
        logger.info('in _create_solo_layer()')
        return Layer(solo_buttons=self.horizontal_clip_launch_matrix)


    def _create_arm_layer(self):
        logger.info('in _create_arm_layer()')
        return Layer(arm_buttons=self.horizontal_clip_launch_matrix)


    def _create_view_control(self):
        logger.info('in _create_view_control()')
        self._view_control = ViewControlComponent(is_enabled=False,
          layer=self._create_track_navigation_layer(),
          name='View_Control')
        self._view_control.set_enabled(True)
      

    def _create_display_element(self, command_bytes, name):
        return SimpleDisplayElement((midi.DISPLAY_HEADER + command_bytes),
        (sysex.SYSEX_END_BYTE,), name=name)


    def _create_parameter_display_matrix(self, command_byte, start_index, name):
        return ButtonMatrixElement(rows=[
        [self._create_display_element((command_byte, start_index + index), '_Display_{}'.format(name, index)) for index in range(8)]],
        name=('{}_Displays'.format(name)))


    def fcb1010_display_modes(self):
        logger.info('in fcb1010_display_modes()')
        DISPLAY_1_CC = 109
        DISPLAY_2_CC = 110
        ASCII_LOOKUP = {'A':  0, 'B':  1, 'C':  2, 'D':  3, 'E':  4, 'F':  5, 
                        'G':  6, 'H':  7, 'I':  8, 'J':  9, 'K': 10, 'L': 11,
                        'M': 12, 'N': 13, 'O': 14, 'P': 15, 'Q': 16, 'R': 17,
                        'S': 18, 'T': 19, 'U': 20, 'V': 21, 'W': 22, 'X': 23,
                        'Y': 24, 'Z': 25, ' ': 27 }
        MODE_LOOKUP = {'arm': 'A', 'solo': 'S', 'launch': 'L',
                       'mute': 'M', 'chan_strip': 'C', 'transport': 'T',
                       'dev': 'D', PEDAL_MODE_LAUNCH_MODE_NAME: 'L', PEDAL_MODE_TRACK_MODE_NAME: 'T'}

        left_led_char = MODE_LOOKUP.get(self._current_pedal_mode, ' ')
        if self._current_pedal_mode == PEDAL_MODE_LAUNCH_MODE_NAME:
            right_led_char = MODE_LOOKUP.get(self._current_session_mode, ' ')
        else:
            right_led_char = MODE_LOOKUP.get(self._current_track_mode, ' ')

        logger.info('midi message, chars: {} {}, value: '.format(left_led_char, right_led_char))
        midi_msg_1 = (CC_STATUS + CHANNEL, DISPLAY_1_CC, ASCII_LOOKUP.get(left_led_char, 27))
        midi_msg_2 = (CC_STATUS + CHANNEL, DISPLAY_2_CC, ASCII_LOOKUP.get(right_led_char, 27))
        midi_clear_1 = (CC_STATUS + CHANNEL, DISPLAY_1_CC, 27)
        midi_clear_2 = (CC_STATUS + CHANNEL, DISPLAY_2_CC, 27)
        midi_pp_1 = midi.pretty_print_bytes(midi_msg_1)
        logger.info('midi message, mode: {}, value: '.format(self._current_pedal_mode) + midi_pp_1)
        midi_pp_2 = midi.pretty_print_bytes(midi_msg_2)
        logger.info('midi message, mode: {}, value: '.format(self._current_session_mode) + midi_pp_2)
        logger.info('midi message, mode: {}, value: '.format(self._current_track_mode) + midi_pp_2)
        self._do_send_midi(midi_clear_1)
        time.sleep(0.05)
        self._do_send_midi(midi_clear_2)
        time.sleep(0.05)
        self._do_send_midi(midi_msg_1)
        time.sleep(0.05)
        self._do_send_midi(midi_msg_2)


    def fcb1010_display_mode(self, mode):
        logger.info('in fcb1010_display_mode()')
        DISPLAY_1_CC = 109
        DISPLAY_2_CC = 110
        ASCII_LOOKUP = {'A':  0, 'B':  1, 'C':  2, 'D':  3, 'E':  4, 'F':  5, 
                        'G':  6, 'H':  7, 'I':  8, 'J':  9, 'K': 10, 'L': 11,
                        'M': 12, 'N': 13, 'O': 14, 'P': 15, 'Q': 16, 'R': 17,
                        'S': 18, 'T': 19, 'U': 20, 'V': 21, 'W': 22, 'X': 23,
                        'Y': 24, 'Z': 25, ' ': 27 }
        MODE_LOOKUP = {'arm': ['A', 'R'], 'solo': ['S', 'L'], 'launch': ['L', 'C'],
                       'mute': ['M', 'T'], 'chan_strip': ['C', 'H'], 'transport': ['T', 'R'],
                       'dev': ['D', 'V']}

        display_chars = MODE_LOOKUP.get(mode, [' ', ' '])
        logger.debug('midi message, chars: {} {}, value: '.format(display_chars[0], display_chars[1]))
        midi_msg_1 = (CC_STATUS + CHANNEL, DISPLAY_1_CC, ASCII_LOOKUP.get(display_chars[0], 27))
        midi_msg_2 = (CC_STATUS + CHANNEL, DISPLAY_2_CC, ASCII_LOOKUP.get(display_chars[1], 27))
        midi_clear_1 = (CC_STATUS + CHANNEL, DISPLAY_1_CC, 27)
        midi_clear_2 = (CC_STATUS + CHANNEL, DISPLAY_2_CC, 27)
        midi_pp_1 = midi.pretty_print_bytes(midi_msg_1)
        logger.debug('midi message, mode: {}, value: '.format(mode) + midi_pp_1)
        midi_pp_2 = midi.pretty_print_bytes(midi_msg_2)
        logger.debug('midi message, mode: {}, value: '.format(mode) + midi_pp_2)
        self._do_send_midi(midi_clear_1)
        time.sleep(0.05)
        self._do_send_midi(midi_clear_2)
        time.sleep(0.05)
        self._do_send_midi(midi_msg_1)
        time.sleep(0.05)
        self._do_send_midi(midi_msg_2)


    def receive_midi_chunk(self, midi_chunk):
        logger.debug('Received midi chunk')
        for midi_bytes in midi_chunk:
            midi_pp = midi.pretty_print_bytes(midi_bytes)
            logger.debug('receive_midi_chunk, value: ' + midi_pp)
            # self.show_message('receive_midi_chunk, value: ' + midi_pp)

            if midi_bytes[0] & 240 == CC_STATUS:
                channel = midi_bytes[0] & 15
                cc_no = midi_bytes[1]
                cc_value = midi_bytes[2]
                if cc_no == 102:
                    logger.debug('Received CC 102, value: {}'.format(cc_value))
                    super(AAA, self).receive_midi_chunk(midi_chunk)
                elif cc_no == 103:
                    logger.debug('Received CC 103, value: {}'.format(cc_value))
                    super(AAA, self).receive_midi_chunk(midi_chunk)
                elif cc_no == 104:
                    logger.debug('Received CC 104, value: {}'.format(cc_value))
                    if cc_value == 1:
                        self._button_1.receive_value(127)
                    elif cc_value == 2:
                        self._button_2.receive_value(127)
                    elif cc_value == 3:
                        self._button_3.receive_value(127)
                    elif cc_value == 4:
                        self._button_4.receive_value(127)
                    elif cc_value == 5:
                        self._button_5.receive_value(127)
                    elif cc_value == 6:
                        self._button_6.receive_value(127)
                    elif cc_value == 7:
                        self._button_7.receive_value(127)
                    elif cc_value == 8:
                        self._button_8.receive_value(127)
                    elif cc_value == 9:
                        self._button_9.receive_value(127)
                    elif cc_value == 0:
                        self._button_0.receive_value(127)
                    elif cc_value == 10:
                        self._button_up.receive_value(127)
                    elif cc_value == 11:
                        self._button_down.receive_value(127)
                if cc_no == 105:
                    logger.debug('Received CC 105, value: {}'.format(cc_value))
                    if cc_value == 1:
                        self._button_1.receive_value(0)
                    elif cc_value == 2:
                        self._button_2.receive_value(0)
                    elif cc_value == 3:
                        self._button_3.receive_value(0)
                    elif cc_value == 4:
                        self._button_4.receive_value(0)
                    elif cc_value == 5:
                        self._button_5.receive_value(0)
                    elif cc_value == 6:
                        self._button_6.receive_value(0)
                    elif cc_value == 7:
                        self._button_7.receive_value(0)
                    elif cc_value == 8:
                        self._button_8.receive_value(0)
                    elif cc_value == 9:
                        self._button_9.receive_value(0)
                    elif cc_value == 0:
                        self._button_0.receive_value(0)
                    elif cc_value == 10:
                        self._button_up.receive_value(0)
                    elif cc_value == 11:
                        self._button_down.receive_value(0)
            elif midi_bytes[0] == 240:
                pass
            else:
                logger.debug('receive_midi_chunk(): forward midi chunk')
                super(AAA, self).receive_midi_chunk(midi_chunk)
        

    def receive_midi(self, midi_bytes):
        logger.debug('Received midi')
        super(AAA, self).receive_midi(midi_bytes)


    def _do_send_midi(self, midi_event_bytes):
        button_ccs = (94, 104, 105, 101, 100, 99, 98, 97, 96, 95, 93, 92)
        if midi_event_bytes[0] & 240 == CC_STATUS:
                channel = midi_event_bytes[0] & 15
                cc_no = midi_event_bytes[1]
                cc_value = midi_event_bytes[2]
                logger.debug('_do_send_midi(): incomming midi event, channel: {} cc: {} val: {}'.format(channel, cc_no, cc_value))
                if (channel == CHANNEL) and (cc_no in(button_ccs)):
                    button_index = button_ccs.index(cc_no)
                    if cc_value > 0:
                        midi_event_bytes = (midi_event_bytes[0], 106, button_index)
                        logger.debug('_do_send_midi(): rewrite cc {} to 106, value: {}, button: {}'.format(cc_no, cc_value, button_index))
                    else:
                        midi_event_bytes = (midi_event_bytes[0], 107, button_index)
                        logger.debug('_do_send_midi(): rewrite cc {} to 107, value: {}, button: {}'.format(cc_no, cc_value, button_index))
                    time.sleep(0.02) # Add a delay for the old device
                    super(AAA, self)._do_send_midi(midi_event_bytes)
                else:
                    midi_pp = midi.pretty_print_bytes(midi_event_bytes)
                    logger.debug('_do_send_midi(): forward midi event ' + midi_pp)
                    time.sleep(0.02) # Add a delay for the old device
                    super(AAA, self)._do_send_midi(midi_event_bytes)


    @listens('selected_mode')
    def __on_pedal_mode_changed(self, selected_mode):
        logger.info('__on_pedal_mode_changed(): mode = {}'.format(selected_mode))
        if selected_mode != None:
            self._current_pedal_mode = selected_mode
            self.fcb1010_display_modes()

    @listens('selected_mode')
    def __on_session_mode_changed(self, selected_mode):
        logger.info('__on_session_mode_changed(): mode = {}'.format(selected_mode))
        if selected_mode != None:
            self._current_session_mode = selected_mode
            self.fcb1010_display_modes()

    @listens('selected_mode')
    def __on_track_mode_changed(self, selected_mode):
        logger.info('__on_track_mode_changed(): mode = {}'.format(selected_mode))
        if selected_mode != None:
            self._current_track_mode = selected_mode
            self.fcb1010_display_modes()


    def update(self):
        super(AAA, self).update()
        logger.info('update()')

def disconnect(self):
        self._transport = None
        self._mixer = None
        ControlSurface.disconnect(self)