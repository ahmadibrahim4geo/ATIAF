"""Small native Processing-panel extension: real groups and conditional file controls.

Depends on the separately installed QGIS Processing GUI; no host source is bundled.
"""
from processing.gui.ParametersPanel import ParametersPanel
from qgis.PyQt.QtWidgets import QGroupBox, QVBoxLayout
from qgis.PyQt.QtCore import Qt
from atiaf_core.ui_schema import fields, ui_rows, group_name


class ATIAFParametersPanel(ParametersPanel):
    def __init__(self, parent, alg):
        self._group_boxes, self._field_widgets, self._field_labels = {}, {}, {}
        self._specs = {s['name']: s for s in fields(alg.tool_id)}
        self._categories = {s['name']: s['group'] for s in fields(alg.tool_id)}
        self._categories.update({'calc_' + r['id']: r['category'] for r in ui_rows(alg.tool_id)})
        self._language = alg.lang()
        self._algorithm = alg
        super().__init__(parent, alg)
        if self._language == 'ar':
            self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        for name in {s['when'] for s in self._specs.values() if s['when']}:
            wrapper = self.wrappers[name]
            signal = getattr(wrapper, 'widgetValueHasChanged', None)
            if signal is not None:
                signal.connect(self.refresh_visibility)
            elif hasattr(wrapper, 'widget'):
                wrapper.widget.toggled.connect(self.refresh_visibility)
        self.refresh_visibility()
        if alg.tool_id == 'geological_composites':
            from qgis.PyQt.QtWidgets import QPushButton
            self._preview_button = QPushButton('معاينة RGB قبل وبعد' if self._language == 'ar' else 'Preview RGB before / after',self)
            self._preview_button.clicked.connect(self.preview_composite)
            super().addParameterWidget(alg.parameterDefinition('preview_only'),self._preview_button,0)

    def preview_composite(self):
        """Bounded source sampling runs on a native background task; widgets stay on UI thread."""
        from qgis.core import QgsApplication, QgsTask, QgsProcessingContext, QgsProject
        from qgis.PyQt.QtWidgets import QMessageBox, QDialog, QHBoxLayout, QVBoxLayout, QLabel
        from qgis.PyQt.QtGui import QPixmap
        from pathlib import Path
        from atiaf_core.tool_contract import arabic_error
        context=QgsProcessingContext(); context.setProject(QgsProject.instance())
        parameters={name:(w.parameterValue() if hasattr(w,'parameterValue') else w.value()) for name,w in self.wrappers.items()}
        try:
            options=self._algorithm._options(parameters,context)
            options['options']['preview_only']=True
            options['mosaic']=False
            # Resolve AOI on the UI thread; the worker receives only independent geometry.
            source=self._algorithm.parameterAsSource(parameters,self._algorithm.AOI,context)
            if source is not None:
                from shapely import wkt
                from shapely.ops import unary_union
                shapes=[wkt.loads(f.geometry().asWkt()) for f in source.getFeatures() if f.hasGeometry()]
                if shapes:
                    options.update(aoi_geometry=unary_union(shapes),aoi_crs=source.sourceCrs().toWkt())
        except Exception as exc:
            QMessageBox.warning(self,'ATIAF',arabic_error(str(exc)) if self._language=='ar' else str(exc)); return
        self._preview_button.setEnabled(False)
        def work(task):
            from atiaf_core.workflow import run_tool
            return run_tool(**options,canceled=task.isCanceled)
        def done(exception,result=None):
            from qgis.PyQt import sip
            if sip.isdeleted(self): return
            self._preview_button.setEnabled(True)
            if exception or not result:
                text=str(exception or 'Composite preview canceled')
                QMessageBox.warning(self,'ATIAF',arabic_error(text) if self._language=='ar' else text); return
            directory=Path(result['PREVIEWS'][0]).parent
            dialog=QDialog(self); dialog.setWindowTitle('معاينة RGB' if self._language=='ar' else 'RGB preview')
            import json
            config=json.loads((directory/'Preview.json').read_text('utf-8'))
            dialog.setLayout(QVBoxLayout())
            channels=QLabel(config['preset_id']+' | RGB: '+'; '.join(config['channels']))
            channels.setLayoutDirection(Qt.LayoutDirection.LeftToRight); dialog.layout().addWidget(channels)
            grid=config['sample_grid']
            coordinates=QLabel(f"{grid['crs']} | {grid['width']} × {grid['height']} | {grid['pixel_size']} m | {grid['transform']}")
            coordinates.setWordWrap(True); coordinates.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
            dialog.layout().addWidget(coordinates); row=QHBoxLayout()
            labels=['قبل','بعد'] if self._language=='ar' else ['Before','After']
            for title,name in zip(labels,['Before.png','Preview.png']):
                column=QVBoxLayout(); column.addWidget(QLabel(title)); picture=QLabel()
                picture.setPixmap(QPixmap(str(directory/name)).scaled(480,480,Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation)); column.addWidget(picture); row.addLayout(column)
            dialog.layout().addLayout(row)
            text=('الفرق في العرض فقط؛ لا يمثل تصنيفًا. السماوي يعني ارتفاع قناتي العرض الخضراء والزرقاء بالنسبة للحمراء بعد التمديد؛ لا يثبت معدنًا. المصدر العلمي: ' if self._language=='ar' else
                  'Only display changes; no classification. Cyan means stronger green/blue display channels relative to red after stretch; it does not confirm a mineral. Scientific source: ')
            text+=str(config.get('scientific_source',''))
            note=QLabel(text); note.setWordWrap(True); dialog.layout().addWidget(note)
            location=QLabel(result['PREVIEWS'][0]); location.setWordWrap(True)
            location.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
            location.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            dialog.layout().addWidget(location)
            dialog.setLayoutDirection(Qt.LayoutDirection.RightToLeft if self._language=='ar' else Qt.LayoutDirection.LeftToRight)
            self._preview_dialog=dialog; dialog.show()
        self._preview_task=QgsTask.fromFunction('ATIAF RGB preview',work,on_finished=done)
        QgsApplication.taskManager().addTask(self._preview_task)

    def addParameterLabel(self, parameter, label):
        name = parameter.name()
        self._field_labels[name] = label
        if not self._categories.get(name):
            return super().addParameterLabel(parameter, label)

    def addParameterWidget(self, parameter, widget, stretch=0):
        name, category = parameter.name(), self._categories.get(parameter.name())
        self._field_widgets[name] = widget
        if not category:
            return super().addParameterWidget(parameter, widget, stretch)
        if category not in self._group_boxes:
            box = QGroupBox(group_name(category, self._language), self)
            box.setLayout(QVBoxLayout())
            self._group_boxes[category] = box
            super().addParameterWidget(parameter, box, 0)
        layout = self._group_boxes[category].layout()
        if name in self._field_labels:
            layout.addWidget(self._field_labels[name])
        layout.addWidget(widget, stretch)

    def refresh_visibility(self, *unused):
        for name, spec in self._specs.items():
            visible = True
            if spec['when']:
                wrapper = self.wrappers[spec['when']]
                value = wrapper.parameterValue() if hasattr(wrapper, 'parameterValue') else wrapper.value()
                visible = bool(value)
            for mapping in (self._field_widgets, self._field_labels):
                if name in mapping:
                    mapping[name].setVisible(visible)
        for category in ('Manual', 'Retrieval'):
            if category in self._group_boxes:
                parent = 'manual_mode' if category == 'Manual' else 'ndvi_assisted'
                wrapper = self.wrappers[parent]
                self._group_boxes[category].setVisible(bool(wrapper.parameterValue() if hasattr(wrapper, 'parameterValue') else wrapper.value()))
