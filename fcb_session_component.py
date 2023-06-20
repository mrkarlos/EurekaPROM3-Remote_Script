
from __future__ import absolute_import, print_function, unicode_literals
from builtins import range
from itertools import count
import Live
from ableton.v2.base import EventObject, in_range, listens, listens_group, product
from ableton.v2.control_surface.components import SessionComponent
from .fcb_scene_component import FcbSceneComponent

import logging
logger = logging.getLogger(__name__)


class FcbSessionComponent(SessionComponent):
    scene_component_type = FcbSceneComponent

    def __init__(self, *args, **keywords):
        logger.info('in __init__()')
        super().__init__(*args, **keywords)
