# decompyle3 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.8.9 (default, Mar 30 2022, 13:51:17) 
# [Clang 13.1.6 (clang-1316.0.21.2.3)]
# Embedded file name: output/Live/mac_64_static/Release/python-bundle/MIDI Remote Scripts/FANTOM/skin.py
# Compiled at: 2022-01-27 16:28:16
# Size of source mod 2**32: 1167 bytes
from __future__ import absolute_import, print_function, unicode_literals
from ableton.v3.control_surface import Skin, default_skin, merge_skins
from ableton.v3.control_surface.elements import SimpleColor
from .colors import Basic, Rgb
STOPPED = SimpleColor(4)
TRIGGERED_PLAY = SimpleColor(7)
LED_ON = SimpleColor(127)
LED_OFF = SimpleColor(0)

class Colors:

    class DefaultButton:
        Disabled = LED_OFF
        On = LED_ON
        Off = LED_OFF

    class Session:
        ClipEmpty = LED_OFF
        ClipStopped = LED_ON
        ClipRecordButton = LED_ON
        SlotLacksStop = LED_OFF
        SlotTriggeredPlay = LED_OFF
        ClipTriggeredPlay = LED_OFF
        SlotTriggeredRecord = LED_OFF
        ClipTriggeredRecord = LED_OFF
        ClipStarted = LED_ON
        ClipRecording = LED_ON
        Scene = STOPPED
        SceneTriggered = TRIGGERED_PLAY

    class Mixer:
        MuteOff = LED_ON
        MuteOn = LED_OFF
        SoloOff = LED_OFF
        SoloOn = LED_ON
        ArmOff = LED_OFF
        ArmOn = LED_ON

    class Device:
        Off = LED_OFF
        On = LED_ON
        Navigation = LED_ON
        NavigationPressed = LED_ON


skin = merge_skins(default_skin, Skin(Colors))