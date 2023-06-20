
from __future__ import absolute_import, print_function, unicode_literals
from ableton.v2.base import liveobj_valid
from ableton.v2.control_surface.components import ChannelStripComponent
from ableton.v2.control_surface.control import ButtonControl

from .fcb_switch_control import FcbSwitchControl

import logging
logger = logging.getLogger(__name__)


class FcbChannelStripComponent(ChannelStripComponent):
    # clip_launch_button = ButtonControl()
    track_stop_button = FcbSwitchControl()
    # track_stop_button = ButtonControl()

    def __init__(self, *args, **keywords):
        logger.info('in __init__()')
        super().__init__(*args, **keywords)
        self._invert_mute_feedback = True


    # @clip_launch_button.pressed
    # def clip_launch_button(self, button):
    #     song_view = self.song.view
    #     slot_or_scene = song_view.selected_scene if self.song.view.selected_track == self.song.master_track else song_view.highlighted_clip_slot
    #     if liveobj_valid(slot_or_scene):
    #         slot_or_scene.fire()

    @track_stop_button.pressed
    def track_stop_button(self, button):
        logger.info('in track_stop_button().pressed')
        track = self.song.view.selected_track
        if track == self.song.master_track:
            self.song.stop_all_clips()
        elif track in self.song.tracks:
            track.stop_all_clips()


    # @track_stop_button.released_immediately
    # def track_stop_button(self, button):
    #     logger.info('in track_stop_button().released_immediately')
    #     track = self.song.view.selected_track
    #     if track == self.song.master_track:
    #         self.song.stop_all_clips()
    #     elif track in self.song.tracks:
    #         track.stop_all_clips()

    # @track_stop_button.released_delayed
    # def track_stop_button(self, button):
    #     logger.info('in track_stop_button().released_delayed')
    #     self.song.stop_all_clips()
