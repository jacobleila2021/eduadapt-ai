"""UVIE provider package exports."""

from engines.universal_visual_intelligence.providers.computation import provide_computation_visuals
from engines.universal_visual_intelligence.providers.geography import provide_geography_visuals
from engines.universal_visual_intelligence.providers.knowledge import provide_knowledge_visuals
from engines.universal_visual_intelligence.providers.pedagogy import provide_pedagogy_visuals
from engines.universal_visual_intelligence.providers.timeline import provide_timeline_visuals

__all__ = [
    "provide_knowledge_visuals",
    "provide_computation_visuals",
    "provide_pedagogy_visuals",
    "provide_timeline_visuals",
    "provide_geography_visuals",
]
