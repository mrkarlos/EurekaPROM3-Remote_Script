
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
from ableton.v2.control_surface.mode import LayerMode, AddLayerMode, EnablingMode, SetAttributeMode, ModesComponent, ImmediateBehaviour, MomentaryBehaviour, LatchingBehaviour

from .my_button_element import MyButtonElement
# from .blinking_button import BlinkingButtonControl
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


""" Here we define some global variables """
CHANNEL = 0 # Channels are numbered 0 through 15, this script only makes use of one MIDI Channel (Channel 1)

@depends(skin=None)
def create_button(identifier, name, channel=CHANNEL, skin=None):
    return MyButtonElement(True, MIDI_CC_TYPE, channel, identifier, name=name, skin=skin)

@depends(skin=None)
def create_toggle_button(identifier, name, channel=CHANNEL, skin=None):
    return MyButtonElement(False, MIDI_CC_TYPE, channel, identifier, name=name, skin=skin)


class AAA(ControlSurface):

    def __init__(self, *args, **kwargs):
        (super(AAA, self).__init__)(*args, **kwargs)
        
        self._bottom_row_mode = None
        self._session_mode = None

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
            self._create_bottom_row_modes()
            self._create_session_modes()

        """ Here is some Live API stuff just for fun """
        app = Live.Application.get_application() # get a handle to the App
        maj = app.get_major_version() # get the major version from the App
        min = app.get_minor_version() # get the minor version from the App
        bug = app.get_bugfix_version() # get the bugfix version from the App
        self.show_message(str(maj) + "." + str(min) + "." + str(bug)) #put them together and use the ControlSurface show_message method to output version info to console

        self.fcb1010_display_modes()

        logger.info('Completed init')


    def _create_controls(self):
        logger.debug('in _create_controls()')

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

        device_parameter_controls_raw = [[self._pedal_a, self._pedal_b]]
        self.device_parameter_controls = ButtonMatrixElement(rows=device_parameter_controls_raw, name='Device_Parameter_Controls')

        device_on_off_button_matrix_raw = [[self._button_1, self._button_2, self._button_3, self._button_4]]
        self.device_on_off_buttons = ButtonMatrixElement(rows=device_on_off_button_matrix_raw, name='Device_On_off_Buttons')

        # Clip launch configs
        clip_buttons_horizontal_raw = [[self._button_1, self._button_2, self._button_3, self._button_4]]
        self.clip_launch_matrix = ButtonMatrixElement(rows=clip_buttons_horizontal_raw, name='Clip_Launch_Matrix')

        clip_buttons_vertical_raw = [[self._button_1], [self._button_2], [self._button_3], [self._button_4]]
        self.clip_launch_vertical_matrix = ButtonMatrixElement(rows=clip_buttons_vertical_raw, name='Clip_Launch_Vertical_Matrix')


    def _create_transport(self):
        logger.debug('in _create_transport()')
        self._transport = TransportComponent(name='Transport')

        # self._session_recording = SessionRecordingComponent(name='Session_Recording')
        # self._session_recording.layer = Layer(record_button=(self._record_button),
        #     record_stop_button=(self._record_stop_button))


    def _create_session_modes(self):
        logger.debug('in _create_session_modes()')

        self._session_modes = MyModesComponent(name='Session_Modes',
          is_enabled=False,
          support_momentary_mode_cycling=True,
          layer=Layer(cycle_mode_button=(self._button_0)))
        self._session_modes.add_mode('launch', ( 
              EnablingMode((self._session_ring)),
              LayerMode((self._session_navigation), layer=self._create_session_navigation_layer()),
              LayerMode((self._mixer.selected_strip), layer=self._create_channel_strip_encoders_layer()),
              SetAttributeMode(self._bottom_row_modes, 'selected_mode', 'br_l_launch'),
            ),
            behaviour=(ImmediateBehaviour()) )
        self._session_modes.add_mode('dev', (
              LayerMode((self._device_parameters), layer=self._create_device_parameter_layer()),
              LayerMode((self._device_navigation), layer=self._create_device_navigation_layer()),
              SetAttributeMode(self._bottom_row_modes, 'selected_mode', 'br_d_dev'),
            ),
            behaviour=(ImmediateBehaviour()) )
        self._session_modes.add_mode('chan_strip', (
              LayerMode((self._device_parameters), layer=self._create_device_parameter_layer()),
              LayerMode((self._device_navigation), layer=self._create_device_navigation_layer()),
              LayerMode((self._mixer.selected_strip), layer=self._create_channel_strip_encoders_layer()),
              SetAttributeMode(self._bottom_row_modes, 'selected_mode', 'br_c_chan_strip'),
            ),
            behaviour=(ImmediateBehaviour()) )
        # self.fcb1010_display_modes()
        self._AAA__on_session_mode_changed.subject = self._session_modes
        self._session_modes.set_enabled(True)
        self._session_modes.selected_mode = 'launch'

        # device_layer_mode = LayerMode(self._device, Layer(parameter_controls=(self._encoders)))
        # device_navigation_layer_mode = LayerMode(self._device_navigation, Layer(device_nav_right_button=(self._forward_button),
        #   device_nav_left_button=(self._backward_button)))
        # self._encoder_modes.add_mode('device_mode', [device_layer_mode, device_navigation_layer_mode])

    def _create_bottom_row_modes(self):
        logger.info('in _create_bottom_row_modes()')

        self._bottom_row_modes = MyModesComponent(name='Bottom_Row_Modes',
          is_enabled=False,
          support_momentary_mode_cycling=False,
        #   layer=Layer(cycle_mode_button=(self._button_5))
          )
        self._bottom_row_modes.add_mode('custom', ( 
              LayerMode((self._bottom_row_modes), layer=Layer(br_l_launch_button=self._button_5))
            ),
            behaviour=(ImmediateBehaviour()) )
        self._bottom_row_modes.add_mode('br_l_launch', ( 
              LayerMode((self._session), layer=self._create_session_layer()),
              LayerMode((self._bottom_row_modes), layer=Layer(br_l_mute_button=self._button_5))
            ),
            behaviour=(ImmediateBehaviour()) )
        self._bottom_row_modes.add_mode('br_l_mute', ( 
              LayerMode((self._mixer), layer=self._create_mute_layer()), 
              LayerMode((self._bottom_row_modes), layer=Layer(br_l_solo_button=self._button_5))
            ),
            behaviour=(ImmediateBehaviour())  )
        self._bottom_row_modes.add_mode('br_l_solo', ( 
              LayerMode((self._mixer), layer=self._create_solo_layer()),
              LayerMode((self._bottom_row_modes), layer=Layer(br_l_arm_button=self._button_5))
            ),
            behaviour=(ImmediateBehaviour()) )
        self._bottom_row_modes.add_mode('br_l_arm', (
              LayerMode((self._mixer), layer=self._create_arm_layer()),
              LayerMode((self._bottom_row_modes), layer=Layer(br_l_launch_button=self._button_5))
            ),
            behaviour=(ImmediateBehaviour()) )
        self._bottom_row_modes.add_mode('br_c_chan_strip', (
              AddLayerMode((self._mixer.selected_strip), layer=self._create_channel_strip_buttons_layer()),
              LayerMode((self._bottom_row_modes), layer=Layer(br_c_transport_button=self._button_5))
            ),
            behaviour=(ImmediateBehaviour()) )
        # self._bottom_row_modes.add_mode('br_c_launch', ( 
        #       LayerMode((self._vertical_session), layer=self._create_vertical_session_layer()),
        #       LayerMode((self._bottom_row_modes), layer=Layer(br_c_transport_button=self._button_5))
        #     ),
        #     behaviour=(ImmediateBehaviour()) )
        self._bottom_row_modes.add_mode('br_c_transport', (
              LayerMode((self._transport), layer=self._create_transport_control_layer()),
              LayerMode((self._bottom_row_modes), layer=Layer(br_c_chan_strip_button=self._button_5))
            ),
            behaviour=(ImmediateBehaviour()) )
        self._bottom_row_modes.add_mode('br_d_dev', (
              AddLayerMode((self._device_navigation), layer=self._create_device_navigation_on_off_layer()),
              LayerMode((self._bottom_row_modes), layer=Layer(br_d_chan_strip_button=self._button_5))
            ),
            behaviour=(ImmediateBehaviour()) )
        self._bottom_row_modes.add_mode('br_d_chan_strip', (
              AddLayerMode((self._mixer.selected_strip), layer=self._create_channel_strip_buttons_layer()),
              LayerMode((self._bottom_row_modes), layer=Layer(br_d_dev_button=self._button_5))
            ),
            behaviour=(ImmediateBehaviour()) )
        self._bottom_row_modes.add_mode('br_tbd_transport', (
              LayerMode((self._transport), layer=self._create_transport_control_layer()),
              LayerMode((self._bottom_row_modes), layer=Layer(br_c_chan_strip_button=self._button_5))
            ),
            behaviour=(ImmediateBehaviour()) )
        self._AAA__on_bottom_row_modes_changed.subject = self._bottom_row_modes
        self._bottom_row_modes.set_enabled(True)
        self._bottom_row_modes.selected_mode = 'br_l_launch'
        # self.fcb1010_display_modes()



    def _create_mixer(self):
        logger.debug('in _create_mixer()')
        self._mixer = MixerComponent(name='Mixer',
          auto_name=True,
          tracks_provider=(self._session_ring),
          track_assigner=(SimpleTrackAssigner()),
          invert_mute_feedback=True,
          channel_strip_component_type=MyChannelStripComponent)


    def _create_device_parameters(self):
        logger.debug('in _create_device_parameters()')
        self._device_parameters = MySimpleDeviceParameterComponent(name='Device',
          is_enabled=False,
          layer=self._create_device_parameter_layer())
        self._device_parameters.set_enabled(True)


    def _create_device_navigation(self, device_component=None):
        logger.debug('in _create_device_navigation()')
        self._device_navigation = MySimpleDeviceNavigationComponent(name='Device_Navigation',
          layer=self._create_device_navigation_layer())


    def _create_session(self):
        logger.debug('in _create_session()')
        self._session_ring = SessionRingComponent(name='Session_Ring',
          is_enabled=True,
          num_tracks=SESSION_WIDTH,
          num_scenes=SESSION_HEIGHT)
        self._session = MySessionComponent(name='Session',
          is_enabled=False,
          session_ring=(self._session_ring))
        self._session_navigation = MySessionNavigationComponent(name='Session_Navigation',
          is_enabled=False,
        #   layer=(self._create_session_navigation_layer()),
          session_ring=(self._session_ring),
        )
        self._session.set_enabled(True)
        self._session_navigation.set_enabled(True)

    def _create_vertical_session(self):
        logger.info('in _create_vertical_session()')
        self._vertical_session_ring = SessionRingComponent(name='Vertical_Session_Ring',
          is_enabled=False,
          num_tracks=SESSION_HEIGHT,
          num_scenes=SESSION_WIDTH)
        self._vertical_session = MySessionComponent(name='Vertical_Session',
          is_enabled=False,
        #   layer=self._create_vertical_session_layer(),
          session_ring=(self._vertical_session_ring))
        self._vertical_session_navigation = MySessionNavigationComponent(name='Vertical_Session_Navigation',
          is_enabled=False,
          session_ring=(self._vertical_session_ring))
        self._vertical_session_navigation.set_enabled(True)
        self._vertical_session.set_enabled(True)

    def _create_session_layer(self):
        logger.debug('in _create_session_layer()')
        return Layer(clip_launch_buttons=self.clip_launch_matrix)

    def _create_vertical_session_layer(self):
        logger.debug('in _create_vertical_session_layer()')
        return Layer(clip_launch_buttons=self.clip_launch_vertical_matrix)

    def _create_session_navigation_layer(self):
        logger.debug('in _create_session_navigation_layer()')
        return Layer(
          up_button=self._button_6,
          down_button=self._button_7,
        #   up_down_button=self._button_6,
          left_button=self._button_8,
          right_button=self._button_9,
        #   left_right_button=self._button_7,
          )

# TODO: change buttons
    def _create_session_navigation_up_down_layer(self):
        logger.debug('in _create_session_navigation_up_down_layer()')
        return Layer(up_button=self._button_6,
                     down_button=self._button_7)

    def _create_session_navigation_left_right_layer(self):
        logger.debug('in _create_session_navigation_left_right_layer()')
        return Layer(left_button=self._button_6,
                     right_button=self._button_7)
     

    def _create_track_navigation_layer(self):
        logger.debug('in _create_track_navigation_layer()')
        return Layer(prev_track_button=self._button_up,
                     next_track_button=self._button_down)


    def _create_device_navigation_layer(self):
        logger.debug('in _create_device_navigation_layer()') 
        return Layer(prev_button=self._button_8,
                     next_button=self._button_9)
    
    def _create_device_navigation_on_off_layer(self):
        logger.info('in _create_device_navigation_on_off_layer()')
        # return Layer(device_on_off_buttons=self.device_on_off_buttons)
        return Layer(on_off_control_1=self._button_1,
                     on_off_control_2=self._button_2,
                     on_off_control_3=self._button_3,
                     on_off_control_4=self._button_4,
                    )

    def _create_device_parameter_layer(self):
        logger.debug('in _create_device_parameter_layer()')
        return Layer(parameter_controls=self.device_parameter_controls)


    def _create_channel_strip_buttons_layer(self):
        logger.debug('in _create_channel_strip_buttons_layer()')
        return Layer(mute_button=self._button_1,
                     solo_button=self._button_2,
                     arm_button=self._button_3,
                     track_stop_button=self._button_4,
                    )


    def _create_channel_strip_encoders_layer(self):
        logger.debug('in _create_channel_strip_encoders_layer()')
        return Layer(volume_control=self._pedal_a,
                     pan_control=self._pedal_b)
    

    def _create_transport_control_layer(self):
        logger.debug('in _create_transport_control_layer()')
        return Layer(play_button=self._button_1,
                     stop_button=self._button_2,
                    record_button=self._button_3,
                    overdub_button=self._button_4,
                    )


    def _create_mute_layer(self):
        logger.debug('in _create_mute_layer()')
        return Layer(mute_buttons=self.clip_launch_matrix)


    def _create_solo_layer(self):
        logger.debug('in _create_solo_layer()')
        return Layer(solo_buttons=self.clip_launch_matrix)


    def _create_arm_layer(self):
        logger.debug('in _create_arm_layer()')
        return Layer(arm_buttons=self.clip_launch_matrix)


    def _create_view_control(self):
        logger.debug('in _create_view_control()')
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


    def fcb1010_display_modes(self, segment=None):
        logger.info('in fcb1010_display_modes(), segment: {}'.format(segment))

        DISPLAY_1_CC = 109
        DISPLAY_2_CC = 110
        ASCII_LOOKUP = {'A':  0, 'B':  1, 'C':  2, 'D':  3, 'E':  4, 'F':  5, 
                        'G':  6, 'H':  7, 'I':  8, 'J':  9, 'K': 10, 'L': 11,
                        'M': 12, 'N': 13, 'O': 14, 'P': 15, 'Q': 16, 'R': 17,
                        'S': 18, 'T': 19, 'U': 20, 'V': 21, 'W': 22, 'X': 23,
                        'Y': 24, 'Z': 25, ' ': 27 }
        MODE_LOOKUP = {'launch': 'S', 'dev': 'D', 'chan_strip': 'C',
                       'br_l_arm': 'A', 'br_l_solo': 'S', 'br_l_launch': 'L', 'br_l_mute': 'M', 
                       'br_c_chan_strip': 'C', 'br_c_transport': 'T',
                       'br_d_dev': 'D', 'br_d_chan_strip': 'C', 
                       'br_tbd_transport': 'T', 
                      }

        main_mode_char = MODE_LOOKUP.get(self._session_mode, ' ')
        sub_mode_char = MODE_LOOKUP.get(self._bottom_row_mode, ' ')

        logger.info('midi message, chars: {} {}, value: '.format(main_mode_char, sub_mode_char))
        midi_msg_left = (CC_STATUS + CHANNEL, DISPLAY_1_CC, ASCII_LOOKUP.get(main_mode_char, 27))
        midi_msg_right = (CC_STATUS + CHANNEL, DISPLAY_2_CC, ASCII_LOOKUP.get(sub_mode_char, 27))
        midi_clear_left = (CC_STATUS + CHANNEL, DISPLAY_1_CC, 27)
        midi_clear_right = (CC_STATUS + CHANNEL, DISPLAY_2_CC, 27)
        midi_pp_left = midi.pretty_print_bytes(midi_msg_left)
        logger.debug('midi message, mode: {}, value: '.format(self._session_mode) + midi_pp_left)
        midi_pp_right = midi.pretty_print_bytes(midi_msg_right)
        logger.debug('midi message, mode: {}, value: '.format(self._bottom_row_mode) + midi_pp_right)
        if segment == 'left':
            logger.info('in fcb1010_display_modes(), update LEFT segment')
            # self._do_send_midi(midi_clear_left)
            # time.sleep(0.05)
            self._do_send_midi(midi_msg_left)
            time.sleep(0.05)
        elif segment == 'right':
            logger.info('in fcb1010_display_modes(), update RIGHT segment')
            # self._do_send_midi(midi_clear_right)
            # time.sleep(0.05)
            self._do_send_midi(midi_msg_right)
            time.sleep(0.05)
        else:
            logger.info('in fcb1010_display_modes(), update BOTH segments')
            # self._do_send_midi(midi_clear_left)
            # time.sleep(0.05)
            # self._do_send_midi(midi_clear_right)
            # time.sleep(0.05)
            self._do_send_midi(midi_msg_left)
            time.sleep(0.05)
            self._do_send_midi(midi_msg_right)
            time.sleep(0.05)




    def fcb1010_display_mode(self, mode):
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
    def __on_session_mode_changed(self, selected_mode):
        logger.info('__on_session_mode_changed(): mode = {}'.format(selected_mode))
        self._session_mode = selected_mode
        self.fcb1010_display_modes(segment='left')

    @listens('selected_mode')
    def __on_bottom_row_modes_changed(self, selected_mode):
        logger.info('__on_bottom_row_modes_changed(): mode = {}'.format(selected_mode))
        self._bottom_row_mode = selected_mode
        self.fcb1010_display_modes(segment='right')

    def update(self):
        super(AAA, self).update()
        logger.info('update()')

def disconnect(self):
        self._transport = None
        self._mixer = None
        ControlSurface.disconnect(self)