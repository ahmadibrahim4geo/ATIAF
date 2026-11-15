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
