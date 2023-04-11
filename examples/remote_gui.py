#!/usr/bin/env python3

import numpy as np

import armarx_core.remote_gui as rg


# Example code here
class WidgetsTabState:
    def __init__(self):
        self.line = "Hello"
        self.combo = "Second"
        self.checked = True
        self.toggled = False
        self.int_value = 5
        self.float_value = 0.0
        self.button_clicked = False

        self.int_vector = np.array([10, 20, 30])
        self.float_vector = np.array([10.0, 20.0, 30.0])
        self.float_matrix = np.eye(3, dtype=float)


class WidgetsTab(rg.Tab):
    def __init__(self):
        super().__init__("Widgets")

        self.state = WidgetsTabState()

        self.line_edit = rg.LineEdit()
        self.combo = rg.ComboBox(options=["First", "Second", "Third", "Fourth"])
        self.check_box = rg.CheckBox()
        self.toggle = rg.ToggleButton()

        self.int_spin = rg.IntSpinBox()
        self.int_slider = rg.IntSlider(range_min=0, range_max=10)
        self.float_spin = rg.FloatSpinBox()
        self.float_slider = rg.FloatSlider(range_min=0.0, range_max=2.0)

        self.button = rg.Button(label="Button")

        self.collapsible_group = rg.GroupBox(label="Collapsible Group")

        self.int_vector = rg.NdArrayWidget(
            self.state.int_vector, range_min=0, range_max=100
        )
        self.float_vector = rg.NdArrayWidget(
            self.state.float_vector, range_min=-100, range_max=100, column_vector=True
        )
        self.float_matrix = rg.NdArrayWidget(
            self.state.float_matrix, range_min=-1e3, range_max=1e3, steps=4e3
        )

    def create_widget_tree(self):
        v_layout = rg.VBoxLayout()

        self.line_edit.value = self.state.line
        v_layout.add_child(
            rg.HBoxLayout(children=[rg.Label(text="Line: "), self.line_edit])
        )

        self.combo.value = self.state.combo
        v_layout.add_child(
            rg.HBoxLayout(children=[rg.Label(text="Combo: "), self.combo])
        )

        self.check_box.value = self.state.checked
        v_layout.add_child(
            rg.HBoxLayout(children=[rg.Label(text="Check: "), self.check_box])
        )

        self.toggle.value = self.state.toggled
        self.toggle.label = "Toggle"
        v_layout.add_child(
            rg.HBoxLayout(children=[rg.Label(text="Check: "), self.toggle])
        )

        self.int_slider.value = self.state.int_value
        self.int_spin.range = (0, 10)
        self.int_spin.value = self.state.int_value
        v_layout.add_child(
            rg.HBoxLayout(
                children=[rg.Label(text="Int: "), self.int_slider, self.int_spin]
            )
        )

        self.float_slider.value = self.state.float_value
        self.float_spin.range = (0.0, 2.0)
        self.float_spin.value = self.state.float_value
        v_layout.add_child(
            rg.HBoxLayout(
                children=[rg.Label(text="Float: "), self.float_slider, self.float_spin]
            )
        )

        self.button.label = "Button"
        v_layout.add_child(
            rg.HBoxLayout(children=[rg.Label(text="Button: "), self.button])
        )

        v_layout.add_child(rg.VSpacer())

        group_box = rg.GroupBox()
        # Label can be set via property
        group_box.label = "Group VBoxLayout"
        # Child can be added via 'add_child'
        group_box.add_child(v_layout)

        # Label and child can be set via constructor argument
        grid_group_box = rg.GroupBox(
            label="Group GridLayout",
            child=rg.GridLayout()
            .add(rg.Button(label="1"), pos=(0, 0), span=(1, 2))
            .add(rg.Button(label="2"), pos=(0, 2), span=(2, 1))
            .add(rg.Button(label="3"), pos=(1, 1), span=(1, 1))
            .add(rg.Button(label="4"), pos=(1, 0), span=(2, 1))
            .add(rg.Label(text="foooooooooooooooooo"), pos=(2, 1), span=(1, 2))
            .add(rg.HSpacer(), pos=(0, 3), span=(1, 1)),
        )

        self.collapsible_group.collapsed = True
        # Be careful with container widgets that you store in member variables:
        # Use the set_* instead of the add_* methods to override previously added children
        self.collapsible_group.set_child(
            rg.Label(text="This can only be seen if expanded")
        )

        # Nd Array widgets:
        self.int_vector.value = self.state.int_vector
        self.float_vector.value = self.state.float_vector
        self.float_matrix.value = self.state.float_matrix

        layout = rg.GridLayout()
        row = 0

        layout.add(rg.Label("Int Vector:"), pos=(row, 0)).add(
            self.int_vector.create_tree(), pos=(row, 1)
        )
        row += 1
        layout.add(rg.Label("Column Vector:"), pos=(row, 0)).add(
            self.float_vector.create_tree(), pos=(row, 1)
        )
        row += 1
        layout.add(rg.Label("Float Matrix:"), pos=(row, 0)).add(
            self.float_matrix.create_tree(), pos=(row, 1)
        )
        row += 1

        array_group_box = rg.GroupBox(label="Array Widgets", child=layout)

        root = rg.VBoxLayout(
            children=[
                group_box,
                grid_group_box,
                self.collapsible_group,
                array_group_box,
            ]
        )

        return root

    def on_update(self):
        self.state.line = self.line_edit.value
        self.state.combo = self.combo.value

        # Set the spin box value to the value of the slider
        new_int_value = self.int_slider.value
        if new_int_value != self.state.int_value:
            self.state.int_value = new_int_value
            self.int_spin.value = new_int_value

        # Set the slider value to the value of the spin box
        new_float_value = self.float_spin.value
        if new_float_value != self.state.float_value:
            self.state.float_value = new_float_value
            self.float_slider.value = new_float_value

        self.state.toggled = self.toggle.value
        self.state.checked = self.check_box.value
        self.state.button_clicked = self.button.was_clicked()

        self.state.int_vector = self.int_vector.value
        self.state.float_vector = self.float_vector.value
        self.state.float_matrix = self.float_matrix.value


client = rg.Client()

widgets_tab = WidgetsTab()
client.add_tab(widgets_tab)

try:
    while True:
        client.receive_updates()

        if widgets_tab.state.button_clicked:
            print("Clicked")
            print("Int value: ", widgets_tab.state.int_value)

        client.send_updates()
except KeyboardInterrupt:
    pass
