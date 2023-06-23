
from __future__ import absolute_import, print_function, unicode_literals
from past.utils import old_div

TIMER_DELAY = 0.1
MOMENTARY_DELAY = 0.4
MOMENTARY_DELAY_TICKS = int(old_div(MOMENTARY_DELAY, TIMER_DELAY))
DOUBLE_CLICK_DELAY = 0.7

NOTE_OFF_STATUS = 128
NOTE_ON_STATUS = 144
CC_STATUS = 176
NUM_NOTES = 128
NUM_CC_NO = 128
NUM_CHANNELS = 16
EXP_PEDAL_CC = 11
