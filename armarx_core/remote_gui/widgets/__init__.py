"""
This module provides remote GUI widget classes.

Widget classes:
 - Label: Display a text string.
 - LineEdit: Edit text in a box.
 - ComboBox: Select an option from a predefined list.
 - IntSpinBox: Edit an integer value in a box.
 - IntSlider: Select an integer value with a slider.
 - FloatSpinBox: Edit a floating point value in a box.
 - FloatSlider: Select a floating point value with a slider.
 - Button: Click a button.
 - CheckBox: Mark a box with a check mark.
 - ToggleButton: Toggle a button.
 - HBoxLayout: Layout widgets horizontally.
 - VBoxLayout: Layout widgets vertically.
 - GridLayout: Layout widgets in a grid.
 - GroupBox: Group widgets in box.
 - VSpacer: Add vertical spacing to fill a layout.
 - HSpacer: Add horizontal spacing to fill a layout.
"""
from typing import List, Tuple

from armarx import RemoteGuiInterfacePrx
from armarx import RemoteGui as rg
from armarx.remote_gui.ice_wrapper import make_value_variant
from armarx.remote_gui.ice_wrapper import make_widget_state
from armarx.remote_gui.ice_wrapper import TabProxy


class Widget:
    """
    Base class for widgets.

    This class provides the following properties:
     - hidden: Controls whether the widget is visible or hidden.
     - disabled: Controls whether the widget is enabled or disabled.
    """

    next_id = 0

    def __init__(self, desc: rg.Widget):
        self.desc = desc
        self.desc.name = f"Widget_{Widget.next_id}"
        Widget.next_id = Widget.next_id + 1
        self.desc.defaultValue = make_value_variant(None)
        self.desc.defaultState = make_widget_state(hidden=False, disabled=False)
        # List of rg.Widget (only Ice description)
        self.desc.children = []

        # List of Widgets (Python instances of this class)
        self.children = []

        # Tab proxy object will be set once we create the remote tab
        self.tab: TabProxy = None

    def _check_initialized(self, property_name: str):
        if self.tab is None:
            raise Exception(
                f"Cannot query widget property '{property_name}': Widget has not been initialized"
            )

    @property
    def hidden(self):
        """Returns whether the widget is currently hidden."""
        self._check_initialized("hidden")
        return self.tab.is_hidden(self.desc.name)

    @hidden.setter
    def hidden(self, new_hidden: bool):
        """Hides or shows the widget."""
        self._check_initialized("hidden")
        self.tab.set_hidden(self.desc.name, new_hidden)

    @property
    def disabled(self):
        """Returns whether the widget is currently disabled."""
        self._check_initialized("disabled")
        return self.tab.is_disabled(self.desc.name)

    @disabled.setter
    def disabled(self, new_disabled: bool):
        """Enables or disables the widget."""
        self._check_initialized("disabled")
        self.tab.set_disabled(self.desc.name, new_disabled)


class ValueWidget(Widget):
    """
    Base class for widgets, which store values (e.g. IntSpinBox, LineEdit).

    This class provides the 'value' property, whose type is determined by the derived class.
    A LineEdit will accept 'str' values while an IntSpinBox accepts 'int' values.
    """

    def __init__(self, desc: rg.Widget):
        super().__init__(desc)

    @property
    def value(self):
        """Returns the current values stored in the widget."""
        return self.tab.get_value(self.desc.name)

    @value.setter
    def value(self, new_value):
        """
        Sets the value of the widget.

        The new value will be stored locally until the updates have been sent to the remote server.
        Sending the updates can be done via :meth:`Client.send_updates` or :meth:`Tab.send_updates`.
        """
        self.desc.defaultValue = make_value_variant(new_value)

        if self.tab is not None:
            self.tab.set_value(self.desc.name, new_value)

    def has_value_changed(self) -> bool:
        """Indicates whether the value has changed since the last update."""
        return self.tab.has_value_changed(self.desc.name)


class Label(ValueWidget):
    """The label widget displays its value as a text string."""

    def __init__(self, text: str = ""):
        super().__init__(rg.Label())
        self.value = text


class LineEdit(ValueWidget):
    """A line edit displays its value as an editable text box."""

    def __init__(self):
        super().__init__(rg.LineEdit())
        self.value = ""


class ComboBox(ValueWidget):
    """
    A combo box displays its value as a text string selected from a list of
    predefined options.
    """

    def __init__(self, options: List[str] = None):
        super().__init__(rg.ComboBox())
        if options is None:
            self.desc.options = []
        elif not options:
            raise Exception("Options must not be empty", options)
        else:
            self.desc.options = options
            self.value = options[0]

    def add_option(self, option: str):
        """Add an option to the list of predefined values of this combo box."""
        self.desc.options.append(option)

        # Set the default value to the first option that is set
        if self.desc.defaultValue.type == rg.ValueVariantType.VALUE_VARIANT_EMPTY:
            self.desc.defaultValue = make_value_variant(option)

    @property
    def options(self):
        """Returns the list of predefined options of this combo box."""
        return self.desc.options

    @options.setter
    def options(self, new_options: list):
        """Sets the list of predefined options of this combo box."""
        self.desc.options = new_options

        # Set the default value to the first option that is set
        if self.desc.defaultValue.type == rg.ValueVariantType.VALUE_VARIANT_EMPTY:
            self.desc.defaultValue = make_value_variant(new_options[0])

    @property
    def index(self) -> int:
        """Returns the index of the current value in the list of predefined options."""
        value: str = self.value
        for index, option in enumerate(self.desc.options):
            if option == value:
                return index
        return -1

    @index.setter
    def index(self, new_index: int):
        """Sets the current value to the entry of predefined options with the given index."""
        if new_index < 0 or new_index >= len(self.desc.options):
            raise Exception(
                "Index out of range for combo box",
                new_index,
                "Options:",
                self.desc.options,
            )
        self.value = self.desc.options[new_index]


class IntSpinBox(ValueWidget):
    """
    An int spin box displays its value as an integer in a text box with up-down arrows for editing.

    The 'range' property defines the allowed range of values by specifying a
    minimum and maximum value.
    The current value of the widget can only be set between these two values.
    The GUI does not allow the user to change the value outside of the defined range.
    """

    def __init__(self, value=0, range_min=0, range_max=1):
        super().__init__(rg.IntSpinBox())
        self.range = (range_min, range_max)
        self.value = value

    @property
    def range(self) -> Tuple[int, int]:
        """Returns the allowed value range as tuple (minimum value, maximum value)."""
        return self.desc.min, self.desc.max

    @range.setter
    def range(self, range_tuple: Tuple[int, int]):
        """Sets the allowed value range as tuple (minimum value, maximum value)."""
        self.desc.min = int(range_tuple[0])
        self.desc.max = int(range_tuple[1])


class IntSlider(ValueWidget):
    """
    An int slider displays its value as a horizontal slider.

    The 'range' property defines the allowed range of values by specifying a
    minimum and maximum value.
    The current value of the widget can only be set between these two values.
    The GUI does not allow the user to change the value outside of the defined range.
    """

    def __init__(self, value: int = 0, range_min: int = 0, range_max: int = 1):
        super().__init__(rg.IntSlider())
        self.range = (range_min, range_max)
        self.value = value

    @property
    def range(self) -> Tuple[int, int]:
        """Returns the allowed value range as tuple (minimum value, maximum value)."""
        return self.desc.min, self.desc.max

    @range.setter
    def range(self, range_tuple: Tuple[int, int]):
        """Sets the allowed value range as tuple (minimum value, maximum value)."""
        self.desc.min = int(range_tuple[0])
        self.desc.max = int(range_tuple[1])


class FloatSpinBox(ValueWidget):
    """
    A float spin box displays its value as a decimal number in a text box with up-down arrows for editing.

    The 'range' property defines the allowed range of values by specifying a minimum and maximum value.
    The current value of the widget can only be set between these two values.
    The GUI does not allow the user to change the value outside of the defined range.

    The 'steps' property defines in how many steps the value can be changed from its minimum to its maximum.

    The 'decimals' property defines how many decimal places of the current value are displayed in the widget.
    """

    def __init__(
        self,
        value: float = 0.0,
        range_min: float = 0.0,
        range_max: float = 1.0,
        steps: int = 100,
        decimals: int = 3,
    ):
        super().__init__(rg.FloatSpinBox())
        self.value = value
        self.range = (range_min, range_max)
        self.steps = steps
        self.decimals = decimals

    @property
    def range(self) -> Tuple[float, float]:
        """Returns the allowed value range as tuple (minimum value, maximum value)."""
        return self.desc.min, self.desc.max

    @range.setter
    def range(self, range_tuple: Tuple[float, float]):
        """Sets the allowed value range as tuple (minimum value, maximum value)."""
        self.desc.min = float(range_tuple[0])
        self.desc.max = float(range_tuple[1])

    @property
    def steps(self) -> int:
        """Returns the number of steps in which the value can be changed from minimum to maximum."""
        return self.desc.steps

    @steps.setter
    def steps(self, new_steps: int):
        """Sets the number of steps in which the value can be changed from minimum to maximum."""
        self.desc.steps = int(new_steps)

    @property
    def decimals(self) -> int:
        """Returns the number of decimal places, which are displayed in the widget."""
        return self.desc.decimals

    @decimals.setter
    def decimals(self, new_decimals: int):
        """Sets the number of decimal places, which are displayed in the widget."""
        self.desc.decimals = int(new_decimals)


class FloatSlider(ValueWidget):
    """
    A float slider displays its value as a horizontal slider.

    The 'range' property defines the allowed range of values by specifying a
    minimum and maximum value.
    The current value of the widget can only be set between these two values.
    The GUI does not allow the user to change the value outside of the defined range.

    The 'steps' property defines in how many steps the value can be changed
    from its minimum to its maximum.
    """

    def __init__(
        self,
        value: float = 0.0,
        range_min: float = 0.0,
        range_max: float = 1.0,
        steps: int = 100,
    ):
        super().__init__(rg.FloatSlider())
        self.value = value
        self.range = (range_min, range_max)
        self.steps = steps

    @property
    def range(self) -> Tuple[float, float]:
        """Returns the allowed value range as tuple (minimum value, maximum value)."""
        return self.desc.min, self.desc.max

    @range.setter
    def range(self, range_tuple: Tuple[float, float]):
        """Sets the allowed value range as tuple (minimum value, maximum value)."""
        self.desc.min = float(range_tuple[0])
        self.desc.max = float(range_tuple[1])

    @property
    def steps(self) -> int:
        """Returns the number of steps in which the value can be changed from minimum to maximum."""
        return self.desc.steps

    @steps.setter
    def steps(self, new_steps: int):
        """Sets the number of steps in which the value can be changed from minimum to maximum."""
        self.desc.steps = int(new_steps)


class Button(ValueWidget):
    """
    A button can be clicked.

    Internally a button is still a value widget with type 'int'.
    The value stores the number of times a button has been clicked.

    The 'label' property defines the text displayed on the button.
    """

    def __init__(self, label: str = "Button"):
        super().__init__(rg.Button())
        self.value = 0
        self.label = label

    @property
    def label(self) -> str:
        """Return the label text."""
        return self.desc.label

    @label.setter
    def label(self, new_label: str):
        """Set the label text."""
        self.desc.label = new_label

    def was_clicked(self):
        """Return whether the button has been clicked."""
        return self.tab.was_button_clicked(self.desc.name)


class CheckBox(ValueWidget):
    """A check box displays its boolean value as a check mark in a box."""

    def __init__(self, checked: bool = False):
        super().__init__(rg.CheckBox())
        self.value = checked


class ToggleButton(ValueWidget):
    """
    A toggle button displays its boolean value as a pushed in button.

    The 'label' property defines the text displayed on the button.
    """

    def __init__(self, label: str = "Button", toggled: bool = False):
        super().__init__(rg.ToggleButton())
        self.value = toggled
        self.label = label

    @property
    def label(self) -> str:
        """Return the label text."""
        return self.desc.label

    @label.setter
    def label(self, new_label: str):
        """Set the label text."""
        self.desc.label = new_label


class ContainerWidget(Widget):
    """This is the base class for all widgets containing child widgets."""

    def __init__(self, desc: rg.Widget, children: List[Widget] = None):
        super().__init__(desc)
        if children is not None:
            self.add_children(children)

    def add_child(self, child: Widget):
        """Add a widget to the list of child widgets."""
        self.desc.children.append(child.desc)
        self.children.append(child)

    def add_children(self, children: List[Widget]):
        """Add a list of widgets to the list of child widgets."""
        for child in children:
            self.add_child(child)

    def set_children(self, children: List[Widget]):
        """Set the list of child widgets (overwrites previous children)."""
        self.desc.children = [child.desc for child in children]
        self.children = children

    def set_child(self, child: Widget):
        """Set a single child widget (overwrites previous children)."""
        self.set_children([child])


class HBoxLayout(ContainerWidget):
    """A container widget with a horizontal box layout for the child widgets."""

    def __init__(self, children: List[Widget] = None):
        super().__init__(rg.HBoxLayout(), children)


class VBoxLayout(ContainerWidget):
    """A container widget with a vertical box layout for the child widgets."""

    def __init__(self, children: List[Widget] = None):
        super().__init__(rg.VBoxLayout(), children)


class GridLayout(ContainerWidget):
    """A container widget with a grid layout for the child widgets."""

    def __init__(self):
        super().__init__(rg.GridLayout())
        self.desc.childrenLayoutInfo = []

    def add(
        self, child: Widget, pos: Tuple[int, int] = None, span: Tuple[int, int] = None
    ):
        """Add a child widget at the specified grid position (x, y) and span (width, height)."""

        if span is None:
            span = (1, 1)

        self.add_child(child)

        layout = rg.GridLayoutData()
        layout.row = pos[0]
        layout.col = pos[1]
        layout.spanRow = span[0]
        layout.spanCol = span[1]
        self.desc.childrenLayoutInfo.append(layout)

        return self


class GroupBox(ContainerWidget):
    """
    A group box is a container widget which can only hold a single child widget.

    The 'label' property is displayed at the top of the border of the group box.
    The 'collapsed' property determines whether the group box is collapsed or expanded.
    """

    def __init__(self, label: str = "GroupBox", child: Widget = None):
        if child is None:
            super().__init__(rg.GroupBox())
        else:
            super().__init__(rg.GroupBox(), [child])
        self.label = label

    @property
    def label(self) -> str:
        """Return the label text."""
        return self.desc.label

    @label.setter
    def label(self, new_label: str):
        """Set the label text."""
        self.desc.label = new_label

    @property
    def collapsed(self) -> bool:
        """Return whether the group box was initially collapsed or expanded."""
        return self.desc.collapsed

    @collapsed.setter
    def collapsed(self, new_collapsed: bool):
        """Set whether the group box is initially collapsed or expanded."""
        self.desc.collapsed = new_collapsed


class VSpacer(Widget):
    """A spacer that fills vertical space until the parent widget is filled."""

    def __init__(self):
        super().__init__(rg.VSpacer())


class HSpacer(Widget):
    """A spacer that fills horizontal space until the parent widget is filled."""

    def __init__(self):
        super().__init__(rg.HSpacer())
