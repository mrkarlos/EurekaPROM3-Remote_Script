
from __future__ import absolute_import, print_function, unicode_literals
from builtins import range
from itertools import count
import Live
from ableton.v2.base import EventObject, in_range, listens, listens_group, product
from ableton.v2.control_surface.components import SessionComponent
from .my_scene_component import MySceneComponent

import logging
logger = logging.getLogger(__name__)


class MySessionComponent(SessionComponent):
    scene_component_type = MySceneComponent

    def __init__(self, *args, **keywords):
        logger.info('in __init__()')
        (super(MySessionComponent, self).__init__)(*args, **keywords)
