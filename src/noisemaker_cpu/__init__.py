"""noisemaker-cpu — Python port of the noisemaker-cpu shader engine.

Renders the canonical Noisemaker effect catalog by transpiling upstream GLSL to
native Python kernels (bundled ahead of time), runtime-compiling and caching
them, and executing them through a CPU render graph. See docs/superpowers/specs.
"""

__version__ = "0.0.0"

from .frame_export import FrameExportQueue
from .renderer import CpuRenderer
from .sink import SinkManager

__all__ = ["CpuRenderer", "FrameExportQueue", "SinkManager", "__version__"]
