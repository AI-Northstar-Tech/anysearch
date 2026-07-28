"""Provider registry: name/alias -> provider class, plus selection priority."""

from __future__ import annotations

from typing import Dict, List, Type

from .base import BaseProvider, Capability
from .brave import BraveProvider
from .duckduckgo import DuckDuckGoProvider
from .exa import ExaProvider
from .firecrawl import FirecrawlProvider
from .gemini import GeminiProvider
from .google_pse import GooglePSEProvider
from .jina import JinaProvider
from .kagi import KagiProvider
from .keiro import KeiroProvider
from .linkup import LinkupProvider
from .octen import OctenProvider
from .parallel import ParallelProvider
from .perplexity import PerplexityProvider
from .searchapi import SearchApiProvider
from .searxng import SearxngProvider
from .serpapi import SerpApiProvider
from .serper import SerperProvider
from .tavily import TavilyProvider
from .you import YouProvider

PROVIDER_CLASSES: List[Type[BaseProvider]] = [
    OctenProvider,
    ExaProvider,
    ParallelProvider,
    TavilyProvider,
    BraveProvider,
    KeiroProvider,
    LinkupProvider,
    PerplexityProvider,
    GeminiProvider,
    SerperProvider,
    SerpApiProvider,
    SearchApiProvider,
    YouProvider,
    JinaProvider,
    KagiProvider,
    FirecrawlProvider,
    GooglePSEProvider,
    SearxngProvider,
    DuckDuckGoProvider,
]

# Auto-selection order when the caller does not name a provider. Keyed, high-quality
# providers come first; the keyless DuckDuckGo fallback is last so the SDK works
# out of the box even with no credentials configured.
DEFAULT_PRIORITY: List[str] = [p.name for p in PROVIDER_CLASSES]

_REGISTRY: Dict[str, Type[BaseProvider]] = {}
for _cls in PROVIDER_CLASSES:
    _REGISTRY[_cls.name] = _cls
    for _alias in _cls.aliases:
        _REGISTRY[_alias] = _cls


def get_provider_class(name: str) -> Type[BaseProvider]:
    from ..exceptions import ProviderNotFoundError

    key = (name or "").strip().lower().replace("-", "_")
    if key not in _REGISTRY:
        raise ProviderNotFoundError(name, list_provider_names())
    return _REGISTRY[key]


def list_provider_names() -> List[str]:
    return [c.name for c in PROVIDER_CLASSES]


__all__ = [
    "BaseProvider",
    "Capability",
    "PROVIDER_CLASSES",
    "DEFAULT_PRIORITY",
    "get_provider_class",
    "list_provider_names",
]
