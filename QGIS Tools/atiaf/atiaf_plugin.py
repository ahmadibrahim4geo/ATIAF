# -*- coding: utf-8 -*-
"""ATIAF QGIS Plugin lifecycle manager."""

try:
    from qgis.core import QgsApplication
except ImportError:
    QgsApplication = None

from .provider import ATIAFProcessingProvider


class ATIAFPlugin:
    """QGIS plugin registering ATIAF Processing Provider."""

    def __init__(self, iface):
        self.iface = iface
        self.provider = None

    def initProcessing(self):
        """Init Processing provider for QGIS."""
        self.provider = ATIAFProcessingProvider()
        if QgsApplication and hasattr(QgsApplication, "processingRegistry"):
            QgsApplication.processingRegistry().addProvider(self.provider)

    def initGui(self):
        """Init GUI elements if needed."""
        self.initProcessing()

    def unload(self):
        """Unload plugin and remove provider."""
        if self.provider and QgsApplication and hasattr(QgsApplication, "processingRegistry"):
            QgsApplication.processingRegistry().removeProvider(self.provider)
