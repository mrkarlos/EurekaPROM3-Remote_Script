Actions
Refister buttons with midi info as None (This didn't work, gave errors)
Create a receive_midi method in the class. Deal with the two cc's and do a send value to the
None buttons. May need to pass to Super() when done with the overriden cc's (Did this)
do a register midi_map for the two button cc's.  (Not a good idea)

Check thr Axiom.py cs for example midi method

What buttons in what Component

MODES 
When creating modes create the main element e.g. _mixer and leave the controls to the modes/layer

ControlSurface

SessionModesComponent
''' This is the high level component that controls the session. It contains:

    name
    is_enabled
    Layer (This layer contains the buttons to control the mode)
    modes (This are instances of the ModesComponent)
    support_momentary_mode_cycling (Set to False)

SessionComponent
    name
    session_mode_button (Is this the button that puts the device into session mode?)
    session_ring (The session ring is used to move the window around the session view)
    layer
    is_enabled

    set_stop_all_clips_button
    set_stop_track_clip_buttons
    set_managed_select_button
    set_managed_delete_button
    set_managed_duplicate_button
    set_modifier_button
    set_clip_launch_buttons
    set_scene_launch_buttons

SessionNavigationComponent
    name
    session_ring
    layer

    set_up_button
    set_down_button
    set_left_button
    set_right_button
    set_page_up_button
    set_page_down_button
    set_page_left_button
    set_page_right_button

SessionRingComponent
    ''' This is thd ring around the clips in session view TBC '''
    Number of tracks (num_tracks)
    Number of scences (num_scenes)

ViewControlComponent
    set_next_track_button
    set_prev_track_button
    set_next_scene_button
    set_prev_scene_button
    set_next_scene_list_button
    set_prev_scene_list_button

BackgroundComponent
''' Is this a component that is always running in the background?'''

    name
    is_enabled
    add_nop_listeners (True or False)
    layer

SessionRecordingComponent
    set_scene_list_new_button
    set_new_button
    set_new_scene_button
    record buttton? (see TransportComponent)

TransportComponent
    play_button
    stop_button
    tap_tempo_button
    continue_playing_button

    set_seek_buttons (ffwd_button, rwd_button)
    set_seek_forward_button
    set_seek_backward_button
    set_nudge_buttons (up_button, down_button)
    set_nudge_up_button(self, up_button):
    set_nudge_down_button
    set_record_button
    set_loop_button
    set_punch_in_button
    set_punch_out_button
    set_metronome_button
    set_arrangement_overdub_button
    set_overdub_button
    set_tempo_control
    set_tempo_fine_control

MixerComponent
    name
    auto_name (Set to True)
    tracks_provider ( set to self._session_ring)
    track_assigner (set to SimpleTrackAssigner() )
    channel_strip_component_type
    channel_strip
    master_strip

    set_prehear_volume_control
    set_crossfader_control
    set_volume_controls
    set_pan_controls
    set_send_controls
    set_arm_buttons
    set_solo_buttons
    set_mute_buttons
    set_track_select_buttons
    set_shift_button

ChannelStripComponent
    set_send_controls
    set_pan_control
    set_volume_control
    set_select_button
    set_mute_button
    set_solo_button
    set_arm_button
    set_shift_button
    set_crossfade_toggle
    set_invert_mute_feedback

ClipSlotComponent
    set_launch_button
    set_delete_button
    set_select_button
    set_duplicate_button

ModesComponent
    cycle_mode_button

UndoRedoComponent
    undo_button
    redo_button

