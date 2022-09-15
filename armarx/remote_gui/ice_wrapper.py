import copy
import numpy as np

from armarx import RemoteGuiInterfacePrx
from armarx import RemoteGui as rg


def make_value_variant(py_value) -> rg.ValueVariant:
    result = rg.ValueVariant()
    if py_value is None:
        result.type = rg.ValueVariantType.VALUE_VARIANT_EMPTY
    elif isinstance(py_value, bool):
        result.type = rg.ValueVariantType.VALUE_VARIANT_BOOL
        result.i = 1 if py_value else 0
    elif isinstance(py_value, int):
        result.type = rg.ValueVariantType.VALUE_VARIANT_INT
        result.i = py_value
    elif isinstance(py_value, float):
        result.type = rg.ValueVariantType.VALUE_VARIANT_FLOAT
        result.f = py_value
    elif isinstance(py_value, str):
        result.type = rg.ValueVariantType.VALUE_VARIANT_STRING
        result.s = py_value
    elif isinstance(py_value, list):
        if len(py_value) == 3:
            if isinstance(py_value[0], float):
                # Vector3 (float)
                result.type = rg.ValueVariantType.VALUE_VARIANT_VECTOR3
                result.v = py_value
            elif isinstance(py_value[0], int):
                # Vector3 (int ==> convert to float)
                result.type = rg.ValueVariantType.VALUE_VARIANT_VECTOR3
                result.v = [float(item) for item in py_value]
            elif isinstance(py_value[0], list):
                flat_list = [item for sublist in py_value for item in sublist]
                if len(flat_list) == 16:
                    result.type = rg.ValueVariantType.VALUE_VARIANT_MATRIX4
                    result.v = flat_list
                else:
                    raise ValueError(
                        "Error while creating ValueVariant from list",
                        "Number of elements in the list:",
                        len(flat_list),
                        "Value:",
                        py_value,
                    )
            else:
                raise ValueError(
                    "Error while creating ValueVariant from list",
                    "Type of first element:",
                    type(py_value[0]),
                    "Value:",
                    py_value,
                )
    elif isinstance(py_value, np.ndarray):
        return make_value_variant(py_value.tolist())
    else:
        raise ValueError(
            "Error while creating ValueVariant from unknown type",
            "Type of value:",
            type(py_value),
            "Value:",
            py_value,
        )
    return result


def unwrap_value_variant(variant: rg.ValueVariant):
    if variant.type == rg.ValueVariantType.VALUE_VARIANT_EMPTY:
        return None
    elif variant.type == rg.ValueVariantType.VALUE_VARIANT_BOOL:
        return variant.i != 0
    elif variant.type == rg.ValueVariantType.VALUE_VARIANT_INT:
        return variant.i
    elif variant.type == rg.ValueVariantType.VALUE_VARIANT_FLOAT:
        return variant.f
    elif variant.type == rg.ValueVariantType.VALUE_VARIANT_STRING:
        return variant.s
    elif variant.type == rg.ValueVariantType.VALUE_VARIANT_VECTOR3:
        return variant.v
    elif variant.type == rg.ValueVariantType.VALUE_VARIANT_MATRIX4:
        return [variant.v[0:4], variant.v[4:8], variant.v[8:12], variant.v[12:16]]
    else:
        raise ValueError("Unknown value variant type", variant)


def are_equal(left, right):
    if type(left) != type(right):
        return False
    if isinstance(left, list):
        for l, r in zip(left, right):
            return are_equal(l, r)
    else:
        return left == right


def make_widget_state(hidden: bool = False, disabled: bool = False) -> rg.WidgetState:
    result = rg.WidgetState()
    result.hidden = hidden
    result.disabled = disabled
    return result


class TabProxy:
    def __init__(self, proxy: RemoteGuiInterfacePrx, tab_id: str):
        self.proxy = proxy

        self.tab_id = tab_id

        self.current_values = {}
        self.old_values = {}
        self.new_values = {}
        self.dirty_values = {}

        self.current_widget_states = {}
        self.old_widget_states = {}
        self.new_widget_states = {}

        self.values_changed = False
        self.widget_changed = False

    def initialize_widget(self, widget):
        widget.tab = self
        for child_widget in widget.children:
            self.initialize_widget(child_widget)

    def remove(self):
        self.proxy.removeTab(self.tab_id)

    def receive_updates(self):
        self.old_values = self.current_values
        self.current_values = self.proxy.getValues(self.tab_id)
        self.new_values = copy.deepcopy(self.current_values)
        self.values_changed = False
        self.dirty_values.clear()

        self.old_widget_states = self.current_widget_states
        self.current_widget_states = self.proxy.getWidgetStates(self.tab_id)
        self.new_widget_states = copy.deepcopy(self.current_widget_states)
        self.widget_changed = False

    def send_updates(self):
        if self.values_changed:
            self.proxy.setValues(self.tab_id, self.dirty_values)
            self.dirty_values.clear()
        if self.widget_changed:
            self.proxy.setWidgetStates(self.tab_id, self.new_widget_states)

    def set_value(self, name: str, py_value):
        # Keep track of changed values, dirty values and so on
        current_value = self.get_value(name)
        new_value_variant = make_value_variant(py_value)
        if not are_equal(current_value, py_value):
            self.values_changed = True
            self.dirty_values[name] = new_value_variant
        self.new_values[name] = new_value_variant

    def get_value(self, name: str):
        current_value_variant = self.current_values[name]
        current_value = unwrap_value_variant(current_value_variant)
        return current_value

    def has_value_changed(self, name: str):
        old_value = self.old_values.get(name, None)
        if old_value is None:
            return True
        old_value = unwrap_value_variant(old_value)
        current_value = self.get_value(name)
        return not are_equal(old_value, current_value)

    def was_button_clicked(self, name: str):
        if name not in self.old_values:
            return False

        if name not in self.new_values:
            raise Exception(
                "Button with name", name, "not found in new values", self.new_values
            )

        old_value = unwrap_value_variant(self.old_values[name])
        new_value = unwrap_value_variant(self.new_values[name])
        return new_value > old_value

    def set_hidden(self, name: str, hidden: bool):
        state = self.new_widget_states[name]
        if state.hidden != hidden:
            self.widget_changed = True
        state.hidden = hidden

    def is_hidden(self, name: str) -> bool:
        state = self.current_widget_states[name]
        return state.hidden

    def set_disabled(self, name: str, disabled: bool):
        state = self.new_widget_states[name]
        if state.disabled != disabled:
            self.widget_changed = True
        state.disabled = disabled

    def is_disabled(self, name: str) -> bool:
        state = self.current_widget_states[name]
        return state.disabled
