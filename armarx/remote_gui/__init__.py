import warnings

warnings.warn(
    "Use 'armarx_core.remote_gui' instead.", DeprecationWarning
)

from armarx_core.remote_gui import (
    Label,
    LineEdit,
    ComboBox,
    IntSpinBox,
    IntSlider,
    FloatSpinBox,
    FloatSlider,
    Button,
    ToggleButton,
    CheckBox,
    HBoxLayout,
    VBoxLayout,
    GridLayout,
    GroupBox,
    VSpacer,
    HSpacer,

    NdArrayWidget,

    Client,
)
