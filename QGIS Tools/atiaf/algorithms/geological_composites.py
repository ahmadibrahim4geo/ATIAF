"""Native geological RGB tool; the shared core owns all scientific calculations."""
from .common import ATIAFAlgorithm


class GeologicalCompositesAlgorithm(ATIAFAlgorithm):
    tool_id = 'geological_composites'

    def groupId(self):
        return 'geological_analysis'

    def group(self):
        return 'التحليل الجيولوجي' if self.lang() == 'ar' else 'Geological Analysis'
