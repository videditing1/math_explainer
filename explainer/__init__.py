"""House toolkit for 3b1b-style math explainers.

In a scene file:   from explainer import *
gives you Manim, the house style, VoiceScene (word-synced timeline) and components.
"""
from manim import *  # noqa: F401,F403

from .components import *  # noqa: F401,F403
from .style import *  # noqa: F401,F403
from .sync import VoiceScene  # noqa: F401
