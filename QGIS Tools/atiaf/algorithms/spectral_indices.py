"""Native ATIAF spectral_indices adapter; shared workflow is in atiaf_core."""
from .common import ATIAFAlgorithm


class SpectralIndicesAlgorithm(ATIAFAlgorithm):
    tool_id = "spectral_indices"
