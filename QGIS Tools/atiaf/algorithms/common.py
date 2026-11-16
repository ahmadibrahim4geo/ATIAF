"""Native QGIS parameter and execution adapter; scientific imports are deferred."""
from pathlib import Path
import sys

for candidate in (Path(__file__).resolve().parents[3], Path(__file__).resolve().parents[1]):
    if (candidate / 'atiaf_core').is_dir() and str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))
from atiaf_core.tool_contract import CATALOG, SENSORS, title, label, help_text, calculations, arabic_error
from atiaf_core.ui_schema import fields, ui_rows
try:
    from qgis.core import (QgsProcessing, QgsProcessingAlgorithm, QgsProcessingException,
                           QgsProcessingParameterBoolean, QgsProcessingParameterCrs,
                           QgsProcessingParameterEnum, QgsProcessingParameterFeatureSource,
                           QgsProcessingParameterFile, QgsApplication, QgsProcessingParameterString,
                           QgsProcessingParameterNumber, QgsProcessingParameterDefinition)
except ImportError:
    QgsProcessingAlgorithm = object
    QgsProcessing = None


class ATIAFAlgorithm(QgsProcessingAlgorithm):
    tool_id = ''
    language = None
    INPUT_FOLDER, T1_FOLDER, T2_FOLDER = 'INPUT_FOLDER', 'INPUT_FOLDER', 'SECOND_FOLDER'
    APPLY_QA, ENABLE_MOSAIC, INDICES = 'APPLY_QA', 'ENABLE_MOSAIC', 'INDICES'
    AOI, CRS, OUTPUT_FOLDER = 'AOI', 'CRS', 'OUTPUT_FOLDER'

    def lang(self):
        if self.language:
            return self.language
        if QgsProcessing:
            from qgis.PyQt.QtCore import QLocale
            return 'ar' if QLocale().name().startswith('ar') else 'en'
        return 'en'

    def name(self):
        return self.tool_id

    def displayName(self):
        return title(self.tool_id, self.lang())

    def group(self):
        return 'تحليل المرئيات' if self.lang() == 'ar' else 'Imagery Analysis'

    def groupId(self):
        return 'imagery_analysis'

    def shortHelpString(self):
        return help_text(self.tool_id, self.lang())

    def helpUrl(self):
        plugin = Path(__file__).resolve().parents[1]
        page = 'GEOLOGICAL_COLOR_COMPOSITES.html' if self.tool_id == 'geological_composites' else 'INDICATORS_CATALOG.html'
        packaged = plugin/'help'/self.lang()/page
        source = plugin.parents[1]/'documentation'/self.lang()/page
        return (packaged if packaged.is_file() else source).as_uri()

    def createInstance(self):
        instance = type(self)()
        instance.language = self.language
        return instance

    def initAlgorithm(self, config=None):
        if QgsProcessing is None:
            return
        lang = self.lang()
        self.sensor_keys = [s for s in SENSORS if s != 'EXPERT']
        self.addParameter(QgsProcessingParameterEnum('SENSOR', label('sensor_product', lang), options=self.sensor_keys, defaultValue=0))
        self.addParameter(QgsProcessingParameterFile(self.INPUT_FOLDER, label('input_folder', lang), behavior=QgsProcessingParameterFile.Folder))
        if self.tool_id == 'temporal_change':
            self.addParameter(QgsProcessingParameterFile(self.T2_FOLDER, label('second_folder', lang), behavior=QgsProcessingParameterFile.Folder))
        self.field_specs = fields(self.tool_id)
        for spec in [s for s in self.field_specs if s['group'] in (None, 'Manual')]:
            self._add_field(spec)
        self.addParameter(QgsProcessingParameterBoolean(self.APPLY_QA, label('apply_qa_mask', lang), defaultValue=True))
        qa_choices = [
            ('Cloud_Only_Arid', 'Arid Region / Cloud Only (Recommended)', 'المناطق الجافة والصحراوية / سحب فقط (موصى به)'),
            ('Full_Strict', 'Full Strict (Clouds, Cirrus, Shadows)', 'حجب صارم كامل (سحب وسمحاق وظلال)'),
            ('Water_Protected', 'Water-Protected (Preserve Water & Coasts)', 'حماية المسطحات المائية والشواطئ'),
            ('None', 'None (Cloud-free scene)', 'بدون قناع (مرئية خالية من السحب)'),
        ]
        self.addParameter(QgsProcessingParameterEnum(
            'QA_MASK_MODE', label('qa_mask_mode', lang),
            options=[c[2 if lang == 'ar' else 1] for c in qa_choices],
            defaultValue=0
        ))
        self.addParameter(QgsProcessingParameterBoolean(self.ENABLE_MOSAIC, label('enable_mosaic', lang), defaultValue=False))
        rows = calculations(self.tool_id, lang)
        self.index_keys = [i for i, _ in rows]
        # Retain the old enum only for saved processing models; never show the old flat list.
        legacy = QgsProcessingParameterEnum(self.INDICES, 'Legacy calculation IDs', options=[text for _, text in rows],
                                             allowMultiple=True, defaultValue=[], optional=True)
        legacy.setFlags(legacy.flags() | QgsProcessingParameterDefinition.Flag.FlagHidden)
        self.addParameter(legacy)
        for row in ui_rows(self.tool_id):
            self.addParameter(QgsProcessingParameterBoolean('calc_' + row['id'], row['id'] + ' — ' + row[lang], defaultValue=False))
        for spec in [s for s in self.field_specs if s['group'] not in (None, 'Manual')]:
            self._add_field(spec)
        self.addParameter(QgsProcessingParameterString('STUDY_AREA_NAME', label('study_area_name', lang), optional=True))
        self.addParameter(QgsProcessingParameterFeatureSource(self.AOI, label('aoi_features', lang), types=[QgsProcessing.TypeVectorPolygon], optional=True))
        self.addParameter(QgsProcessingParameterCrs(self.CRS, label('output_crs', lang), optional=True))
        self.addParameter(QgsProcessingParameterBoolean('ADD_TO_MAP', label('add_to_map', lang), defaultValue=False))
        # An optional folder input avoids QGIS silently choosing a temporary destination.
        self.addParameter(QgsProcessingParameterFile(self.OUTPUT_FOLDER, label('output_folder', lang), behavior=QgsProcessingParameterFile.Folder, optional=True))

    def _add_field(self, spec):
        name, text, default = spec['name'], spec[self.lang()], spec['default']
        if spec['kind'] == 'bool':
            p = QgsProcessingParameterBoolean(name, text, defaultValue=default)
        elif spec['kind'] == 'enum':
            choices = spec['choices']
            p = QgsProcessingParameterEnum(name, text, options=[c[2 if self.lang() == 'ar' else 1] for c in choices],
                defaultValue=next(i for i, c in enumerate(choices) if c[0] == default))
        elif spec['kind'] == 'float':
            p = QgsProcessingParameterNumber(name, text, type=QgsProcessingParameterNumber.Double, optional=True, defaultValue=default)
        elif spec['kind'] == 'file':
            p = QgsProcessingParameterFile(name, text, optional=True)
        else:
            p = QgsProcessingParameterString(name, text, optional=True, defaultValue=default)
        self.addParameter(p)

    def createCustomParametersWidget(self, parent=None):
        from .parameters_panel import ATIAFParametersPanel
        return ATIAFParametersPanel(parent, self)

    def _field_values(self, parameters, context):
        values = {}
        for spec in fields(self.tool_id):
            if spec['when'] and not self.parameterAsBool(parameters, spec['when'], context):
                continue
            name, kind = spec['name'], spec['kind']
            if kind == 'bool':
                value = self.parameterAsBool(parameters, name, context)
            elif kind == 'enum':
                value = spec['choices'][self.parameterAsEnum(parameters, name, context)][0]
            elif kind == 'float':
                value = None if parameters.get(name) in (None, '') else self.parameterAsDouble(parameters, name, context)
            else:
                value = self.parameterAsString(parameters, name, context)
            values[name] = value
        return values

    def _options(self, parameters, context):
        legacy_selected = self.parameterAsEnums(parameters, self.INDICES, context)
        if any(i < 0 or i >= len(self.index_keys) for i in legacy_selected):
            raise ValueError('Unknown calculation ID')
        selected = [r['id'] for r in ui_rows(self.tool_id) if self.parameterAsBool(parameters, 'calc_' + r['id'], context)]
        selected = list(dict.fromkeys(selected + [self.index_keys[i] for i in legacy_selected]))
        crs = self.parameterAsCrs(parameters, self.CRS, context)
        if parameters.get(self.CRS) and not crs.isValid():
            raise ValueError('Decision D-007: invalid output CRS')
        field_opts = self._field_values(parameters, context)
        qa_choices = ['Cloud_Only_Arid', 'Full_Strict', 'Water_Protected', 'None']
        if 'QA_MASK_MODE' in parameters:
            qa_idx = self.parameterAsEnum(parameters, 'QA_MASK_MODE', context)
            if 0 <= qa_idx < len(qa_choices):
                field_opts['qa_mask_mode'] = qa_choices[qa_idx]
        study_val = self.parameterAsString(parameters, 'STUDY_AREA_NAME', context) if parameters.get('STUDY_AREA_NAME') else None
        if study_val:
            field_opts['study_area_name'] = study_val
        return dict(tool=self.tool_id, input_folder=self.parameterAsString(parameters, self.INPUT_FOLDER, context),
                    selected=selected, options=field_opts,
                    sensor=self.sensor_keys[self.parameterAsEnum(parameters, 'SENSOR', context)],
                    apply_qa=self.parameterAsBool(parameters, self.APPLY_QA, context),
                    mosaic=self.parameterAsBool(parameters, self.ENABLE_MOSAIC, context),
                    output_crs=crs.toWkt() if parameters.get(self.CRS) and crs.isValid() else None,
                    output_folder=self.parameterAsString(parameters, self.OUTPUT_FOLDER, context) or None,
                    second_folder=self.parameterAsString(parameters, self.T2_FOLDER, context) if self.tool_id == 'temporal_change' else None,
                    language=self.lang())

    def checkParameterValues(self, parameters, context):
        valid, message = super().checkParameterValues(parameters, context)
        if not valid:
            return valid, message
        try:
            from atiaf_core.workflow import discover, preflight
            options = self._options(parameters, context)
            if self.tool_id == 'geological_composites':
                from atiaf_core.composites.engine import validate_request
                validate_request(**options)
                return True, ''
            scenes = discover(options['input_folder'], options['sensor'], manual_options=options['options'])
            preflight(self.tool_id, scenes, options['selected'], options['apply_qa'], options['mosaic'], options['output_crs'], options['options'])
            return True, ''
        except Exception as exc:
            return False, arabic_error(str(exc)) if self.lang() == 'ar' else str(exc)

    def processAlgorithm(self, parameters, context, feedback):
        try:
            from atiaf_core.workflow import run_tool
            options = self._options(parameters, context)
            aoi, aoi_crs = None, None
            source = self.parameterAsSource(parameters, self.AOI, context)
            if parameters.get(self.AOI) and source is None:
                raise ValueError('AOI source is invalid')
            if source is not None:
                from shapely import wkt
                from shapely.ops import unary_union
                aoi_crs = source.sourceCrs().toWkt() if source.sourceCrs().isValid() else None
                shapes = [wkt.loads(f.geometry().asWkt()) for f in source.getFeatures() if f.hasGeometry()]
                if not shapes:
                    raise ValueError('AOI is empty')
                aoi = unary_union(shapes)
            result = run_tool(**options, aoi_geometry=aoi, aoi_crs=aoi_crs,
                              canceled=feedback.isCanceled, progress=feedback.pushInfo)
            for path in result.get('PREVIEWS', []):
                feedback.pushInfo(('المعاينة: ' if self.lang() == 'ar' else 'Preview: ') + path)
            self._pending_layers = (result.get('DISPLAY_RASTERS') or result['OUTPUT_RASTERS']) if self.parameterAsBool(parameters, 'ADD_TO_MAP', context) else []
            feedback.setProgress(100)
            return result
        except Exception as exc:
            raise QgsProcessingException(arabic_error(str(exc)) if self.lang() == 'ar' else str(exc)) from exc

    def postProcessAlgorithm(self, context, feedback):
        from qgis.core import QgsProject, QgsRasterLayer, QgsMessageLog
        from qgis.PyQt.QtCore import QTimer
        project = context.project() or QgsProject.instance()
        queue = list(getattr(self, '_pending_layers', []))
        def add_next():
            if not queue:
                return
            path = queue.pop(0)
            layer = QgsRasterLayer(path, Path(path).stem)
            if layer.isValid():
                if self.tool_id == 'geological_composites':
                    from qgis.core import QgsMultiBandColorRenderer
                    layer.setRenderer(QgsMultiBandColorRenderer(layer.dataProvider(), 1, 2, 3))
                project.addMapLayer(layer)
            else:
                QgsMessageLog.logMessage(f'Layer load failed; saved raster: {path}', 'ATIAF')
            QTimer.singleShot(0, add_next)
        if queue:
            QTimer.singleShot(0, add_next)
        return {}
