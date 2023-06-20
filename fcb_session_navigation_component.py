from __future__ import absolute_import, print_function, unicode_literals
from ableton.v2.base import listens
from ableton.v2.control_surface.components import SessionNavigationComponent
from .fcb_scroll_component import FcbScrollComponent

import logging
logger = logging.getLogger(__name__)


class FcbSessionNavigationComponent(SessionNavigationComponent):

    def __init__(self, session_ring=None, *a, **k):
        super().__init__(*a, session_ring=session_ring, **k)
        self._session_ring = session_ring
        self._vertical_banking = FcbScrollComponent((self.scene_scroller_type(session_ring)),
          parent=self)
        self._horizontal_banking = FcbScrollComponent((self.track_scroller_type(session_ring)),
          parent=self)
        self._vertical_paginator = FcbScrollComponent((self.scene_pager_type(session_ring)),
          parent=self)
        self._horizontal_paginator = FcbScrollComponent((self.track_pager_type(session_ring)),
          parent=self)


    def set_up_down_button(self, button):
        self._vertical_banking.set_scroll_up_down_button(button)

    def set_left_right_button(self, button):
        self._horizontal_banking.set_scroll_left_right_button(button)
        self._horizontal_banking.update()

