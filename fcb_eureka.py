
from __future__ import absolute_import, print_function, unicode_literals
from builtins import object, range, str
import Live
import time
import logging
from ableton.v2.base import listens, inject, const, depends
from ableton.v2.control_surface import MIDI_CC_TYPE, MIDI_NOTE_TYPE, ControlSurface, Layer
from ableton.v2.control_surface.components import TransportComponent, MixerComponent, ViewControlComponent, SessionRingComponent, SimpleTrackAssigner
from ableton.v2.control_surface.elements import EncoderElement, ButtonMatrixElement
from ableton.v2.control_surface import midi
from ableton.v2.control_surface.control import ButtonControl
from ableton.v2.control_surface.mode import LayerMode, AddLayerMode, EnablingMode, SetAttributeMode, ModesComponent, ImmediateBehaviour, MomentaryBehaviour, LatchingBehaviour

from .fcb_button_element import FcbButtonElement
# from .blinking_button import BlinkingButtonControl
from .fcb_modes_component import FcbModesComponent
from .fcb_session_component import FcbSessionComponent
from .fcb_session_navigation_component import FcbSessionNavigationComponent
from .fcb_channel_strip_component import FcbChannelStripComponent
from .fcb_transport_component import FcbTransportComponent
from .consts import *
from .skin import skin
from .elements import SESSION_WIDTH, SESSION_HEIGHT, V_SESSION_WIDTH, V_SESSION_HEIGHT, NUM_SCENES, NUM_TRACKS, Elements
from .fcb_simple_device_component import FcbSimpleDeviceParameterComponent
from .fcb_simple_device_navigation_component import FcbSimpleDeviceNavigationComponent
from .simple_display import SimpleDisplayElement

logger = logging.getLogger(__name__)


""" Here we define some global variables """
CHANNEL = 0 # Channels are numbered 0 through 15, this script only makes use of one MIDI Channel (Channel 1)

@depends(skin=None)
def create_button(identifier, name, channel=CHANNEL, skin=None):
    return FcbButtonElement(True, MIDI_CC_TYPE, channel, identifier, name=name, skin=skin)

@depends(skin=None)
def create_toggle_button(identifier, name, channel=CHANNEL, skin=None):
    return FcbButtonElement(False, MIDI_CC_TYPE, channel, identifier, name=name, skin=skin)


class FCB_Eureka(ControlSurface):

    def __init__(self, *args, **kwargs):
        (super(FCB_Eureka, self).__init__)(*args, **kwargs)
        
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
            self._create_vertical_mixer()
            self._create_transport()
            self._create_device_parameters()
            self._create_device_navigation()
            self._create_bottom_row_modes() # Order is important, this should happen before the main _create_session_modes()
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
        self._pedal_pair_matrix = ButtonMatrixElement(rows=[pedal_pair_raw], name='Pedal_Pair_Matrix')

        self._device_parameter_controls_raw = [self._pedal_a, self._pedal_b]
        self._device_parameter_controls = ButtonMatrixElement(rows=[self._device_parameter_controls_raw], name='Device_Parameter_Controls')

        self._device_on_off_button_matrix_raw = [self._button_1, self._button_2, self._button_3, self._button_4]
        self._device_on_off_buttons = ButtonMatrixElement(rows=[self._device_on_off_button_matrix_raw], name='Device_On_off_Buttons')

        # Clip launch configs
        clip_buttons_horizontal_raw = [self._button_1, self._button_2, self._button_3, self._button_4]
        self._clip_launch_matrix = ButtonMatrixElement(rows=[clip_buttons_horizontal_raw], name='Clip_Launch_Matrix')

        clip_buttons_vertical_raw = [[self._button_1], [self._button_2 ], [self._button_3 ], [self._button_4 ]]
        self._clip_launch_vertical_matrix = ButtonMatrixElement(rows=clip_buttons_vertical_raw, name='Clip_Launch_Vertical_Matrix')


    def _create_transport(self):
        logger.info('in _create_transport()')
        self._transport = FcbTransportComponent(name='Transport')

        # self._session_recording = SessionRecordingComponent(name='Session_Recording')
        # self._session_recording.layer = Layer(record_button=(self._record_button),
        #     record_stop_button=(self._record_stop_button))


    def _create_session_modes(self):
        """Create the main session modes.

            There are 3 session modes: Launch (L), Device (D) and Channel Strip/Transport (T).
            The mode is indicated in the left LED

            The navigation for the session modes is defined in the respective _create_<mode>_navigation_layer()
            Typically the session mode is driven by the top row buttons and 'Up' 'Down' buttons.

            Each session mode has one or more bottom row modes. These use the bottom 5 buttons.
        
        Args: None
        
        Notes:"""

        logger.info('in _create_session_modes()')

        self._session_modes = FcbModesComponent(name='Session_Modes',
          is_enabled=False,
          support_momentary_mode_cycling=True,
          layer=Layer(cycle_mode_button=(self._button_0)))
        # self._session_modes.add_mode('launch_horz', ( 
        #       EnablingMode((self._session_ring)),
        #       LayerMode((self._session_navigation), layer=self._create_session_navigation_layer()),
        #       LayerMode((self._mixer.selected_strip), layer=self._create_channel_strip_encoders_layer()),
        #       SetAttributeMode(self._bottom_row_modes, 'selected_mode', 'br_lh_launch'),
        #     ),
        #     behaviour=(ImmediateBehaviour()) )

        self._session_modes.add_mode('launch_vertical', ( 
              EnablingMode((self._vertical_session_ring)),
              LayerMode((self._vertical_session_navigation), layer=self._create_session_navigation_layer()),
              AddLayerMode((self._vertical_mixer.selected_strip), layer=self._create_channel_strip_encoders_layer()),
              SetAttributeMode(self._bottom_row_modes, 'selected_mode', 'br_lv_clip_launch'),
            ),
            behaviour=(ImmediateBehaviour()) )

        self._session_modes.add_mode('dev', (
              AddLayerMode((self._device_parameters), layer=self._create_device_parameter_layer()),
              AddLayerMode((self._device_navigation), layer=self._create_device_navigation_layer()),
              SetAttributeMode(self._bottom_row_modes, 'selected_mode', 'br_d_dev_1_4'),
            ),
            behaviour=(ImmediateBehaviour()) )
        self._session_modes.add_mode('chan_strip', (
            #   LayerMode((self._device_parameters), layer=self._create_device_parameter_layer()),
            #   LayerMode((self._device_navigation), layer=self._create_device_navigation_layer()),
              AddLayerMode((self._vertical_mixer.selected_strip), layer=self._create_channel_strip_encoders_layer()),
              SetAttributeMode(self._bottom_row_modes, 'selected_mode', 'br_c_chan_strip'),
            ),
            behaviour=(ImmediateBehaviour()) )
        # self.fcb1010_display_modes()
        self._FCB_Eureka__on_session_mode_changed.subject = self._session_modes
        self._session_modes.set_enabled(True)
        self._session_modes.selected_mode = 'launch_vertical'

        # device_layer_mode = LayerMode(self._device, Layer(parameter_controls=(self._encoders)))
        # device_navigation_layer_mode = LayerMode(self._device_navigation, Layer(device_nav_right_button=(self._forward_button),
        #   device_nav_left_button=(self._backward_button)))
        # self._encoder_modes.add_mode('device_mode', [device_layer_mode, device_navigation_layer_mode])

    def _create_bottom_row_modes(self):
        logger.info('in _create_bottom_row_modes()')

        self._bottom_row_modes = FcbModesComponent(name='Bottom_Row_Modes',
          is_enabled=False,
          support_momentary_mode_cycling=False
          )
        self._bottom_row_modes.add_mode('custom', ( 
              LayerMode((self._bottom_row_modes), layer=Layer(br_lv_launch_button=self._button_5))
            ),
            behaviour=(ImmediateBehaviour()) )

        # self._bottom_row_modes.add_mode('br_lh_launch', (
        #       LayerMode((self._session), layer=self._create_session_layer()),
        #       LayerMode((self._bottom_row_modes), layer=Layer(br_lh_mute_button=self._button_5))
        #     ),
        #     behaviour=(ImmediateBehaviour()) )

        # self._bottom_row_modes.add_mode('br_lh_mute', ( 
        #       LayerMode((self._mixer), layer=self._create_mute_layer()), 
        #       LayerMode((self._bottom_row_modes), layer=Layer(br_lh_solo_button=self._button_5))
        #     ),
        #     behaviour=(ImmediateBehaviour())  )
        # self._bottom_row_modes.add_mode('br_lh_solo', ( 
        #       LayerMode((self._mixer), layer=self._create_solo_layer()),
        #       LayerMode((self._bottom_row_modes), layer=Layer(br_lh_arm_button=self._button_5))
        #     ),
        #     behaviour=(ImmediateBehaviour()) )
        # self._bottom_row_modes.add_mode('br_lh_arm', (
        #       LayerMode((self._mixer), layer=self._create_arm_layer()),
        #       LayerMode((self._bottom_row_modes), layer=Layer(br_lh_launch_button=self._button_5))
        #     ),
        #     behaviour=(ImmediateBehaviour()) )

        self._bottom_row_modes.add_mode('br_lv_clip_launch', (
              LayerMode((self._vertical_session), layer=self._create_vertical_session_clips_layer()),
              LayerMode((self._bottom_row_modes), layer=Layer(br_lv_scene_launch_button=self._button_5))
            ),
            behaviour=(ImmediateBehaviour()) )

        self._bottom_row_modes.add_mode('br_lv_scene_launch', (
              LayerMode((self._vertical_session), layer=self._create_vertical_session_scenes_layer()),
              LayerMode((self._bottom_row_modes), layer=Layer(br_lv_transport_button=self._button_5))
            ),
            behaviour=(ImmediateBehaviour()) )

        self._bottom_row_modes.add_mode('br_lv_transport', (
              LayerMode((self._transport), layer=self._create_transport_control_layer()),
              LayerMode((self._bottom_row_modes), layer=Layer(br_lv_chan_strip_button=self._button_5))
            ),
            behaviour=(ImmediateBehaviour()) )
        
        self._bottom_row_modes.add_mode('br_lv_chan_strip', (
              LayerMode((self._vertical_mixer.selected_strip), layer=self._create_channel_strip_buttons_layer()),
              LayerMode((self._bottom_row_modes), layer=Layer(br_lv_clip_launch_button=self._button_5))
            ),
            behaviour=(ImmediateBehaviour()) )

        self._bottom_row_modes.add_mode('br_c_chan_strip', (
              LayerMode((self._vertical_mixer.selected_strip), layer=self._create_channel_strip_buttons_layer()),
              LayerMode((self._bottom_row_modes), layer=Layer(br_c_transport_button=self._button_5))
            ),
            behaviour=(ImmediateBehaviour()) )
        self._bottom_row_modes.add_mode('br_c_transport', (
              LayerMode((self._transport), layer=self._create_transport_control_layer()),
              LayerMode((self._bottom_row_modes), layer=Layer(br_c_chan_strip_button=self._button_5))
            ),
            behaviour=(ImmediateBehaviour()) )
        self._bottom_row_modes.add_mode('br_d_dev_1_4', (
              LayerMode((self._device_navigation), layer=self._create_device_navigation_on_off_layer_1_to_4()),
              LayerMode((self._bottom_row_modes), layer=Layer(br_d_dev_5_8_button=self._button_5))
            ),
            behaviour=(ImmediateBehaviour()) )
        self._bottom_row_modes.add_mode('br_d_dev_5_8', (
              LayerMode((self._device_navigation), layer=self._create_device_navigation_on_off_layer_5_to_8()),
              LayerMode((self._bottom_row_modes), layer=Layer(br_d_dev_9_12_button=self._button_5))
            ),
            behaviour=(ImmediateBehaviour()) )
        self._bottom_row_modes.add_mode('br_d_dev_9_12', (
              LayerMode((self._device_navigation), layer=self._create_device_navigation_on_off_layer_9_to_12()),
              LayerMode((self._bottom_row_modes), layer=Layer(br_d_chan_strip_button=self._button_5))
            ),
            behaviour=(ImmediateBehaviour()) )
        self._bottom_row_modes.add_mode('br_d_chan_strip', (
              LayerMode((self._vertical_mixer.selected_strip), layer=self._create_channel_strip_buttons_layer()),
              LayerMode((self._bottom_row_modes), layer=Layer(br_d_dev_1_4_button=self._button_5))
            ),
            behaviour=(ImmediateBehaviour()) )       
        self._bottom_row_modes.add_mode('br_tbd_transport', (
              LayerMode((self._transport), layer=self._create_transport_control_layer()),
              LayerMode((self._bottom_row_modes), layer=Layer(br_c_chan_strip_button=self._button_5))
            ),
            behaviour=(ImmediateBehaviour()) )
        self._FCB_Eureka__on_bottom_row_modes_changed.subject = self._bottom_row_modes
        self._bottom_row_modes.set_enabled(True)
        self._bottom_row_modes.selected_mode = 'br_lv_clip_launch'
        # self.fcb1010_display_modes()


    def _create_mixer(self):
        logger.info('in _create_mixer()')
        self._mixer = MixerComponent(name='Mixer',
          auto_name=True,
          tracks_provider=(self._session_ring),
          track_assigner=(SimpleTrackAssigner()),
          invert_mute_feedback=True,
          channel_strip_component_type=FcbChannelStripComponent)
        

    def _create_vertical_mixer(self):
        logger.info('in _create_vertical_mixer()')
        self._vertical_mixer = MixerComponent(name='Vertical_Mixer',
          auto_name=True,
          tracks_provider=(self._vertical_session_ring),
          track_assigner=(SimpleTrackAssigner()),
          invert_mute_feedback=True,
          channel_strip_component_type=FcbChannelStripComponent)
        

    def _create_device_parameters(self):
        logger.info('in _create_device_parameters()')
        self._device_parameters = FcbSimpleDeviceParameterComponent(name='Device',
          is_enabled=False,
          layer=self._create_device_parameter_layer())
        self._device_parameters.set_enabled(True)


    def _create_device_navigation(self, device_component=None):
        logger.info('in _create_device_navigation()')
        self._device_navigation = FcbSimpleDeviceNavigationComponent(name='Device_Navigation',
          layer=self._create_device_navigation_layer())


    def _create_session(self):
        logger.info('in _create_session()')
        self._session_ring = SessionRingComponent(name='Session_Ring',
          is_enabled=False,
          num_tracks=SESSION_WIDTH,
          num_scenes=SESSION_HEIGHT)
        self._session = FcbSessionComponent(name='Session',
          is_enabled=False,
          session_ring=(self._session_ring))
        self._session_navigation = FcbSessionNavigationComponent(name='Session_Navigation',
          is_enabled=False,
        #   layer=(self._create_session_navigation_layer()),
          session_ring=(self._session_ring),
        )
        self._session.set_enabled(True)
        self._session_navigation.set_enabled(True)


    def _create_vertical_session(self):
        logger.info('in _create_vertical_session()')
        self._vertical_session_ring = SessionRingComponent(name='Vertical_Session_Ring',
          is_enabled=True,
          num_tracks=V_SESSION_WIDTH,
          num_scenes=V_SESSION_HEIGHT)
        self._vertical_session = FcbSessionComponent(name='Vertical_Session',
          is_enabled=False,
          session_ring=(self._vertical_session_ring))
        self._vertical_session_navigation = FcbSessionNavigationComponent(name='Vertical_Session_Navigation',
          is_enabled=False,
        #   layer=(self._create_vertical_session_navigation_layer()),
          session_ring=(self._vertical_session_ring),
        )
        self._vertical_session.set_enabled(True)
        self._vertical_session_navigation.set_enabled(True)

    def _create_session_layer(self):
        logger.info('in _create_session_layer()')
        return Layer(clip_launch_buttons=self._clip_launch_matrix)

    def _create_vertical_session_clips_layer(self):
        logger.info('in _create_vertical_session_clips_layer()')
        return Layer(clip_launch_buttons=self._clip_launch_vertical_matrix)
    
    def _create_vertical_session_scenes_layer(self):
        logger.info('in _create_vertical_session_scenes_layer()')
        return Layer(scene_launch_buttons=self._clip_launch_vertical_matrix)

    def _create_session_navigation_layer(self):
        logger.info('in _create_session_navigation_layer()')
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
        logger.info('in _create_session_navigation_up_down_layer()')
        return Layer(up_button=self._button_6,
                     down_button=self._button_7)

    def _create_session_navigation_left_right_layer(self):
        logger.info('in _create_session_navigation_left_right_layer()')
        return Layer(left_button=self._button_6,
                     right_button=self._button_7)
     

    def _create_track_navigation_layer(self):
        logger.info('in _create_track_navigation_layer()')
        return Layer(prev_track_button=self._button_up,
                     next_track_button=self._button_down)


    def _create_device_navigation_layer(self):
        logger.info('in _create_device_navigation_layer()') 
        return Layer(prev_button=self._button_8,
                     next_button=self._button_9)
    
    def _create_device_navigation_on_off_layer(self):
        logger.info('in _create_device_navigation_on_off_layer()')
        # return Layer(device_on_off_buttons=self._device_on_off_buttons)
        return Layer(on_off_control_1=self._button_1,
                     on_off_control_2=self._button_2,
                     on_off_control_3=self._button_3,
                     on_off_control_4=self._button_4,
                    )
    def _create_device_navigation_on_off_layer_1_to_4(self):
        logger.info('in _create_device_navigation_on_off_layer_1_to_4()')
        return Layer(on_off_control_1=self._button_1,
                     on_off_control_2=self._button_2,
                     on_off_control_3=self._button_3,
                     on_off_control_4=self._button_4,
                    )

    def _create_device_navigation_on_off_layer_5_to_8(self):
        logger.info('in _create_device_navigation_on_off_layer_5_to_9()')
        return Layer(on_off_control_5=self._button_1,
                     on_off_control_6=self._button_2,
                     on_off_control_7=self._button_3,
                     on_off_control_8=self._button_4,
                    )
    def _create_device_navigation_on_off_layer_9_to_12(self):
        logger.info('in _create_device_navigation_on_off_layer_9_to_12()')
        return Layer(on_off_control_9=self._button_1,
                     on_off_control_10=self._button_2,
                     on_off_control_11=self._button_3,
                     on_off_control_12=self._button_4,
                    )

    def _create_device_parameter_layer(self):
        logger.info('in _create_device_parameter_layer()')
        return Layer(parameter_controls=self._device_parameter_controls)


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
                     metronome_button=self._button_4,
                    )


    def _create_mute_layer(self):
        logger.info('in _create_mute_layer()')
        return Layer(mute_buttons=self._clip_launch_matrix)


    def _create_solo_layer(self):
        logger.info('in _create_solo_layer()')
        return Layer(solo_buttons=self._clip_launch_matrix)


    def _create_arm_layer(self):
        logger.info('in _create_arm_layer()')
        return Layer(arm_buttons=self._clip_launch_matrix)
    

    def _create_vertical_mute_layer(self):
        logger.info('in _create_vertical_mute_layer()')
        return Layer(mute_buttons=self._clip_launch_vertical_matrix)

    def _create_vertical_solo_layer(self):
        logger.info('in _create_vertical_solo_layer()')
        return Layer(solo_buttons=self._clip_launch_vertical_matrix)


    def _create_vertical_arm_layer(self):
        logger.info('in _create_vertical_arm_layer()')
        return Layer(arm_buttons=self._clip_launch_vertical_matrix)


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


    def fcb1010_display_modes(self, segment=None):
        logger.info('in fcb1010_display_modes(), segment: {}'.format(segment))

        ASCII_CC = 109
        NUM_CC = 113

        ASCII_LOOKUP = {'A':  0, 'B':  1, 'C':  2, 'D':  3, 'E':  4, 'F':  5, 
                        'G':  6, 'H':  7, 'I':  8, 'J':  9, 'K': 10, 'L': 11,
                        'M': 12, 'N': 13, 'O': 14, 'P': 15, 'Q': 16, 'R': 17,
                        'S': 18, 'T': 19, 'U': 20, 'V': 21, 'W': 22, 'X': 23,
                        'Y': 24, 'Z': 25, ' ': 27 }
        CHAR_LOOKUP = {'A': [ASCII_CC, 0], 'B': [ASCII_CC, 1], 'C': [ASCII_CC, 2], 'D': [ASCII_CC, 3], 'E': [ASCII_CC, 4], 'F': [ASCII_CC, 5], 
                        'G': [ASCII_CC, 6], 'H': [ASCII_CC, 7], 'I': [ASCII_CC, 8], 'J': [ASCII_CC, 9], 'K': [ASCII_CC, 10], 'L': [ASCII_CC, 11],
                        'M': [ASCII_CC, 12], 'N': [ASCII_CC, 13], 'O': [ASCII_CC, 14], 'P': [ASCII_CC, 15], 'Q': [ASCII_CC, 16], 'R': [ASCII_CC, 17],
                        'S': [ASCII_CC, 18], 'T': [ASCII_CC, 19], 'U': [ASCII_CC, 20], 'V': [ASCII_CC, 21], 'W': [ASCII_CC, 22], 'X': [ASCII_CC, 23],
                        'Y': [ASCII_CC, 24], 'Z': [ASCII_CC, 25], ' ': [ASCII_CC, 27],
                        '0': [NUM_CC, 0], '1': [NUM_CC, 1], '2': [NUM_CC, 2], '3': [NUM_CC, 3], '4': [NUM_CC, 4], '5': [NUM_CC, 5],
                        '6': [NUM_CC, 6], '7': [NUM_CC, 7], '8': [NUM_CC, 8], '9': [NUM_CC, 9]
                      }
        MODE_LOOKUP = {'launch_horz': 'H', 'launch_vertical': 'S', 'dev': 'D', 'chan_strip': 'T',
                       'br_lh_arm': 'A', 'br_lh_solo': 'S', 'br_lh_launch': 'L', 'br_lh_mute': 'M', 
                       'br_lv_clip_launch': 'L', 'br_lv_scene_launch': 'S', 'br_lv_transport': 'T', 'br_lv_chan_strip': 'C',
                       'br_c_chan_strip': 'C', 'br_c_transport': 'T',
                       'br_d_dev_1_4': '1', 'br_d_dev_5_8': '5', 'br_d_dev_9_12': '9', 'br_d_chan_strip': 'C', 
                       'br_tbd_transport': 'T', 
                      }

        main_mode_char = MODE_LOOKUP.get(self._session_mode, ' ')
        sub_mode_char = MODE_LOOKUP.get(self._bottom_row_mode, ' ')

        logger.info('midi message, chars: {} {}, value: '.format(main_mode_char, sub_mode_char))
        left_midi_cc, left_midi_value =  CHAR_LOOKUP.get(main_mode_char, 27)
        right_midi_cc, right_midi_value =  CHAR_LOOKUP.get(sub_mode_char, 27)
        right_midi_cc = right_midi_cc + 1
        logger.info('midi message left char, cc: {}, value: {}'.format(left_midi_cc, left_midi_value))
        logger.info('midi message right char, cc: {}, value: {}'.format(right_midi_cc, right_midi_value))

        # midi_msg_left = (CC_STATUS + CHANNEL, ASCII_CC, ASCII_LOOKUP.get(main_mode_char, 27))
        # midi_msg_right = (CC_STATUS + CHANNEL, ASCII_CC + 1, ASCII_LOOKUP.get(sub_mode_char, 27))
        midi_msg_left = (CC_STATUS + CHANNEL, left_midi_cc, left_midi_value)
        midi_msg_right = (CC_STATUS + CHANNEL, right_midi_cc, right_midi_value)
        midi_clear_left = (CC_STATUS + CHANNEL, ASCII_CC, 27)
        midi_clear_right = (CC_STATUS + CHANNEL, ASCII_CC + 1, 27)
        midi_pp_left = midi.pretty_print_bytes(midi_msg_left)
        logger.info('midi message, mode: {}, value: '.format(self._session_mode) + midi_pp_left)
        midi_pp_right = midi.pretty_print_bytes(midi_msg_right)
        logger.info('midi message, mode: {}, value: '.format(self._bottom_row_mode) + midi_pp_right)
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
        logger.info('midi message, chars: {} {}, value: '.format(display_chars[0], display_chars[1]))
        midi_msg_1 = (CC_STATUS + CHANNEL, DISPLAY_1_CC, ASCII_LOOKUP.get(display_chars[0], 27))
        midi_msg_2 = (CC_STATUS + CHANNEL, DISPLAY_2_CC, ASCII_LOOKUP.get(display_chars[1], 27))
        midi_clear_1 = (CC_STATUS + CHANNEL, DISPLAY_1_CC, 27)
        midi_clear_2 = (CC_STATUS + CHANNEL, DISPLAY_2_CC, 27)
        midi_pp_1 = midi.pretty_print_bytes(midi_msg_1)
        logger.info('midi message, mode: {}, value: '.format(mode) + midi_pp_1)
        midi_pp_2 = midi.pretty_print_bytes(midi_msg_2)
        logger.info('midi message, mode: {}, value: '.format(mode) + midi_pp_2)
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
                    super(FCB_Eureka, self).receive_midi_chunk(midi_chunk)
                elif cc_no == 103:
                    logger.debug('Received CC 103, value: {}'.format(cc_value))
                    super(FCB_Eureka, self).receive_midi_chunk(midi_chunk)
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
                super(FCB_Eureka, self).receive_midi_chunk(midi_chunk)
        

    def receive_midi(self, midi_bytes):
        logger.debug('Received midi')
        super(FCB_Eureka, self).receive_midi(midi_bytes)


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
                    super(FCB_Eureka, self)._do_send_midi(midi_event_bytes)
                else:
                    midi_pp = midi.pretty_print_bytes(midi_event_bytes)
                    logger.debug('_do_send_midi(): forward midi event ' + midi_pp)
                    time.sleep(0.02) # Add a delay for the old device
                    super(FCB_Eureka, self)._do_send_midi(midi_event_bytes)


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
        super(FCB_Eureka, self).update()
        logger.info('update()')

def disconnect(self):
        self._transport = None
        self._mixer = None
        self._vertical_mixer = None
        ControlSurface.disconnect(self)