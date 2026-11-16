"""Thin ArcGIS adapter. Dialog metadata has no NumPy/Rasterio import dependency."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
import site
try:
    user_site = site.getusersitepackages()
    if user_site and Path(user_site).exists() and user_site not in sys.path:
        sys.path.append(user_site)
except Exception:
    pass
try:
    import arcpy
except ImportError:
    arcpy = None
from atiaf_core.tool_contract import CATALOG, SENSORS, title, label, help_text
from atiaf_core.ui_schema import fields, ui_rows, group_name


class NativeTool:
    tool_id = ''
    language = 'en'

    def __init__(self):
        self.label = title(self.tool_id, self.language)
        self.description = help_text(self.tool_id, self.language)
        self.canRunInBackground = False
        if self.tool_id == 'geological_composites':
            self.category = 'التحليل الجيولوجي' if self.language == 'ar' else 'Geological Analysis'

    def getParameterInfo(self):
        if arcpy is None:
            return []
        def param(name, datatype, required=False, default=None):
            p = arcpy.Parameter(name=name, displayName=label(name, self.language), datatype=datatype,
                                parameterType='Required' if required else 'Optional', direction='Input')
            if default is not None:
                p.value = default
            return p
        sensor = param('sensor_product', 'GPString', default='AUTO')
        sensor.filter.type, sensor.filter.list = 'ValueList', [s for s in SENSORS if s != 'EXPERT']
        params = [sensor, param('input_folder', 'DEFolder', True)]
        if self.tool_id == 'temporal_change':
            params.append(param('second_folder', 'DEFolder', True))
        self.field_specs = fields(self.tool_id)
        for spec in [s for s in self.field_specs if s['group'] in (None, 'Manual')]:
            p = self._field(spec)
            params.append(p)
        qa_param = param('apply_qa_mask', 'GPBoolean', default=True)
        qa_mode = param('qa_mask_mode', 'GPString', default='Cloud_Only_Arid')
        qa_mode.filter.type = 'ValueList'
        qa_mode_choices = [
            ('Cloud_Only_Arid', 'Arid Region / Cloud Only (Recommended)', 'المناطق الجافة والصحراوية / سحب فقط (موصى به)'),
            ('Full_Strict', 'Full Strict (Clouds, Cirrus, Shadows)', 'حجب صارم كامل (سحب وسمحاق وظلال)'),
            ('Water_Protected', 'Water-Protected (Preserve Water & Coasts)', 'حماية المسطحات المائية والشواطئ'),
            ('None', 'None (Cloud-free scene)', 'بدون قناع (مرئية خالية من السحب)'),
        ]
        qa_mode.filter.list = [c[2 if self.language == 'ar' else 1] for c in qa_mode_choices]
        qa_mode.value = qa_mode_choices[0][2 if self.language == 'ar' else 1]
        params.extend([qa_param, qa_mode, param('enable_mosaic', 'GPBoolean', default=False)])
        for row in ui_rows(self.tool_id):
            p = arcpy.Parameter(name='calc_' + row['id'], displayName=f"{row['id']} — {row[self.language]}",
                                datatype='GPBoolean', parameterType='Optional', direction='Input')
            p.value = False
            p.category = group_name(row['category'], self.language)
            params.append(p)
        params.extend(self._field(s) for s in self.field_specs if s['group'] not in (None, 'Manual'))
        study_area = param('study_area_name', 'GPString')
        aoi = param('aoi_features', 'GPFeatureLayer')
        aoi.filter.list = ['Polygon']
        params.extend([study_area, aoi, param('output_crs', 'GPCoordinateSystem'),
                       param('add_to_map', 'GPBoolean', default=False), param('output_folder', 'DEFolder')])
        return params

    def _field(self, spec):
        types = {'bool': 'GPBoolean', 'str': 'GPString', 'enum': 'GPString', 'float': 'GPDouble', 'file': 'DEFile'}
        p = arcpy.Parameter(name=spec['name'], displayName=spec[self.language], datatype=types[spec['kind']],
                            parameterType='Optional', direction='Input')
        if spec['default'] is not None:
            p.value = spec['default']
        if spec['choices']:
            p.filter.type, p.filter.list = 'ValueList', [c[2 if self.language == 'ar' else 1] for c in spec['choices']]
            if spec['default'] is not None:
                p.value = next(c[2 if self.language == 'ar' else 1] for c in spec['choices'] if c[0] == spec['default'])
        if spec['group']:
            p.category = group_name(spec['group'], self.language)
        p.enabled = not spec['when']
        return p

    def _values(self, p):
        result = {}
        for spec in fields(self.tool_id):
            if spec['when'] and not p[spec['when']].value:
                continue
            v = p[spec['name']]
            value = bool(v.value) if spec['kind'] == 'bool' else v.valueAsText
            if spec['kind'] == 'float' and value not in (None, ''):
                value = float(value)
            if spec['choices']:
                value = next((c[0] for c in spec['choices'] if value in c), value)
            result[spec['name']] = value
        if 'study_area_name' in p and p['study_area_name'].valueAsText:
            result['study_area_name'] = p['study_area_name'].valueAsText
        if 'qa_mask_mode' in p and p['qa_mask_mode'].valueAsText:
            val_text = p['qa_mask_mode'].valueAsText
            for code, en_name, ar_name in [
                ('Cloud_Only_Arid', 'Arid Region / Cloud Only (Recommended)', 'المناطق الجافة والصحراوية / سحب فقط (موصى به)'),
                ('Full_Strict', 'Full Strict (Clouds, Cirrus, Shadows)', 'حجب صارم كامل (سحب وسمحاق وظلال)'),
                ('Water_Protected', 'Water-Protected (Preserve Water & Coasts)', 'حماية المسطحات المائية والشواطئ'),
                ('None', 'None (Cloud-free scene)', 'بدون قناع (مرئية خالية من السحب)'),
            ]:
                if val_text in (code, en_name, ar_name):
                    result['qa_mask_mode'] = code
                    break
            else:
                result['qa_mask_mode'] = val_text
        return result

    def isLicensed(self):
        return True

    def updateParameters(self, parameters):
        p = {x.name: x for x in parameters}
        source, dest = p['input_folder'], p['output_folder']
        if source.valueAsText and (not dest.altered or not dest.valueAsText):
            dest.value = source.valueAsText
        if 'qa_mask_mode' in p and 'apply_qa_mask' in p:
            p['qa_mask_mode'].enabled = bool(p['apply_qa_mask'].value)
        for spec in fields(self.tool_id):
            p[spec['name']].enabled = not spec['when'] or bool(p[spec['when']].value)

    def updateMessages(self, parameters):
        p = {x.name: x for x in parameters}
        for item in parameters:
            item.clearMessage()
        if not p['input_folder'].valueAsText:
            return
        try:
            from atiaf_core.workflow import discover, unavailable_reason, preflight
            values = self._values(p)
            if self.tool_id == 'geological_composites':
                from atiaf_core.composites.engine import validate_request
                selected = [r['id'] for r in ui_rows(self.tool_id) if p['calc_' + r['id']].value]
                if selected:
                    validate_request(p['input_folder'].valueAsText, selected, p['sensor_product'].valueAsText or 'AUTO',
                        values, bool(p['apply_qa_mask'].value), bool(p['enable_mosaic'].value), self._crs(p['output_crs']))
                return
            scenes = discover(p['input_folder'].valueAsText, p['sensor_product'].valueAsText or 'AUTO',
                              manual_options=values)
            selected = [r['id'] for r in ui_rows(self.tool_id) if p['calc_' + r['id']].value]
            for row in ui_rows(self.tool_id):
                reasons = [unavailable_reason(self.tool_id, row['id'], sc, values) for sc in scenes]
                reason = next((x for x in reasons if x), '')
                if reason:
                    message = self._error(reason)
                    item = p['calc_' + row['id']]
                    (item.setErrorMessage if item.value else item.setWarningMessage)(message)
            if not selected:
                rows = ui_rows(self.tool_id)
                if rows and ('calc_' + rows[0]['id']) in p:
                    p['calc_' + rows[0]['id']].setWarningMessage('اختر حسابًا واحدًا على الأقل من المربعات أدناه.' if self.language == 'ar'
                                                                 else 'Select at least one calculation checkbox below.')
            crs = self._crs(p['output_crs'])
            if selected:
                preflight(self.tool_id, scenes, selected, bool(p['apply_qa_mask'].value), bool(p['enable_mosaic'].value), crs, values)
        except ImportError as exc:
            p['input_folder'].setErrorMessage(self._error(f'Missing dependency: {exc}. See documentation/en/INSTALLATION.md'))
        except Exception as exc:
            p['input_folder'].setErrorMessage(self._error(str(exc)))

    def _error(self, message):
        if self.language == 'ar':
            from atiaf_core.tool_contract import arabic_error
            return arabic_error(message)
        return message

    @staticmethod
    def _crs(parameter):
        if not parameter.valueAsText:
            return None
        sr = arcpy.SpatialReference()
        sr.loadFromString(parameter.valueAsText)
        return sr.exportToString().split(';')[0]

    def execute(self, parameters, messages):
        from atiaf_core.workflow import run_tool
        p = {x.name: x for x in parameters}
        aoi, aoi_crs = None, None
        try:
            if p['aoi_features'].valueAsText:
                from shapely import wkt
                from shapely.ops import unary_union
                source = p['aoi_features'].valueAsText
                desc = arcpy.Describe(source)
                aoi_crs = desc.spatialReference.exportToString().split(';')[0]
                with arcpy.da.SearchCursor(source, ['SHAPE@WKT']) as rows:
                    shapes = [wkt.loads(row[0]) for row in rows if row[0]]
                if not shapes:
                    raise ValueError('AOI is empty; supply a valid polygon')
                aoi = unary_union(shapes)
            selected = [r['id'] for r in ui_rows(self.tool_id) if p['calc_' + r['id']].value]
            result = run_tool(self.tool_id, p['input_folder'].valueAsText, selected,
                              sensor=p['sensor_product'].valueAsText or 'AUTO', options=self._values(p),
                              apply_qa=bool(p['apply_qa_mask'].value), mosaic=bool(p['enable_mosaic'].value),
                              aoi_geometry=aoi, aoi_crs=aoi_crs, output_crs=self._crs(p['output_crs']),
                              output_folder=p['output_folder'].valueAsText,
                              second_folder=p.get('second_folder').valueAsText if 'second_folder' in p else None,
                              canceled=lambda: arcpy.env.isCancelled, progress=arcpy.AddMessage, language=self.language)
        except Exception as exc:
            arcpy.AddError(self._error(str(exc)))
            raise arcpy.ExecuteError from exc
        for path in result['OUTPUT_RASTERS']:
            arcpy.AddMessage(path)
        for path in result.get('PREVIEWS', []):
            arcpy.AddMessage(('المعاينة: ' if self.language == 'ar' else 'Preview: ') + path)
        self._pending_layers = (result.get('DISPLAY_RASTERS') or result['OUTPUT_RASTERS']) if p['add_to_map'].value else []

    def postExecute(self, parameters):
        """Host invokes this on its UI thread after execution. Saved outputs survive rendering failures."""
        if not getattr(self, '_pending_layers', []):
            return
        try:
            active = arcpy.mp.ArcGISProject('CURRENT').activeMap
            if active is None:
                raise ValueError('No active map')
            for path in self._pending_layers:
                try:
                    layer = active.addDataFromPath(path)
                    if self.tool_id == 'geological_composites' and Path(path).stem.endswith('_DISPLAY'):
                        self.style_composite_display(layer)
                except Exception as exc:
                    arcpy.AddWarning(self._error(f'Map loading failed: {exc}; saved raster: {path}'))
        except Exception as exc:
            arcpy.AddWarning(self._error(f'Map loading failed: {exc}; saved products are preserved'))

    @staticmethod
    def style_composite_display(layer):
        """Saved display pixels already contain enhancement: do not stretch them twice."""
        definition=layer.getDefinition('V3')
        colorizer=arcpy.cim.CreateCIMObjectFromClassName('CIMRasterRGBColorizer','V3')
        colorizer.redBandIndex,colorizer.greenBandIndex,colorizer.blueBandIndex=0,1,2
        colorizer.useRedBand=colorizer.useGreenBand=colorizer.useBlueBand=True
        colorizer.useDefaultMapping=False
        colorizer.stretchType='None'
        colorizer.useGammaStretch=False
        colorizer.gammaR=colorizer.gammaG=colorizer.gammaB=1.0
        definition.colorizer=colorizer
        layer.setDefinition(definition)
