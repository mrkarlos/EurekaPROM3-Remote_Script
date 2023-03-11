from __future__ import absolute_import, print_function, unicode_literals
# from ...base import listens
# from ..component import Component
# from .scroll import Scrollable, ScrollComponent
from ableton.v2.base import listens
# from ableton.v2.control_surface.components import SessionNavigationComponent, Scrollable, SessionRingScroller, SessionRingTrackScroller, SessionRingSceneScroller, SessionRingTrackPager, SessionRingScenePager
from ableton.v2.control_surface.components import SessionNavigationComponent, Scrollable, SessionRingScroller,SessionRingTrackScroller, SessionRingSceneScroller, SessionRingTrackPager, SessionRingScenePager
from ableton.v2.control_surface.component import Component
# from ableton.v2.control_surface.components.scroll import Scrollable, ScrollComponent

from .my_scroll_component import ScrollComponent

import logging
logger = logging.getLogger(__name__)


class MySessionNavigationComponent(Component):
    track_scroller_type = SessionRingTrackScroller
    scene_scroller_type = SessionRingSceneScroller
    track_pager_type = SessionRingTrackPager
    scene_pager_type = SessionRingScenePager

    def __init__(self, session_ring=None, *a, **k):
        (super(MySessionNavigationComponent, self).__init__)(*a, **k)
        self._session_ring = session_ring
        self._MySessionNavigationComponent__on_offset_changed.subject = self._session_ring
        self._MySessionNavigationComponent__on_tracks_changed.subject = self._session_ring
        self._MySessionNavigationComponent__on_scene_list_changed.subject = self.song
        self._vertical_banking = ScrollComponent((self.scene_scroller_type(session_ring)),
          parent=self)
        self._horizontal_banking = ScrollComponent((self.track_scroller_type(session_ring)),
          parent=self)
        self._vertical_paginator = ScrollComponent((self.scene_pager_type(session_ring)),
          parent=self)
        self._horizontal_paginator = ScrollComponent((self.track_pager_type(session_ring)),
          parent=self)

    @listens('offset')
    def __on_offset_changed(self, track_offset, _):
        self._update_vertical()
        self._update_horizontal()

    @listens('tracks')
    def __on_tracks_changed(self):
        self._update_horizontal()

    @listens('scenes')
    def __on_scene_list_changed(self):
        self._update_vertical()

    def _update_vertical(self):
        if self.is_enabled():
            self._vertical_banking.update()
            self._vertical_paginator.update()

    def _update_horizontal(self):
        if self.is_enabled():
            self._horizontal_banking.update()
            self._horizontal_paginator.update()

    def set_up_button(self, button):
        self._vertical_banking.set_scroll_up_button(button)

    def set_down_button(self, button):
        self._vertical_banking.set_scroll_down_button(button)

    def set_left_button(self, button):
        self._horizontal_banking.set_scroll_up_button(button)
        self._horizontal_banking.update()

    def set_right_button(self, button):
        self._horizontal_banking.set_scroll_down_button(button)

    def set_page_up_button(self, page_up_button):
        self._vertical_paginator.set_scroll_up_button(page_up_button)

    def set_page_down_button(self, page_down_button):
        self._vertical_paginator.set_scroll_down_button(page_down_button)

    def set_page_left_button(self, page_left_button):
        self._horizontal_paginator.set_scroll_up_button(page_left_button)

    def set_page_right_button(self, page_right_button):
        self._horizontal_paginator.set_scroll_down_button(page_right_button)