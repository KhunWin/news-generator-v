# ui_components.py
from PyQt5.QtWidgets import (
    QGroupBox, QVBoxLayout, QHBoxLayout, QRadioButton, 
    QButtonGroup, QCheckBox, QLineEdit, QWidget
)


class UIComponents:
    """Reusable UI component builders."""
    
    @staticmethod
    def create_boxed_group(title: str, layout_items: list = None) -> QGroupBox:
        """
        Returns a titled QGroupBox whose body contains the supplied items.
        Items may be QWidget or any QLayout subclass.
        """
        try:
            group = QGroupBox(title)
            group.setStyleSheet(
                "QGroupBox {"
                "  font-weight: bold;"
                "  border: 1px solid #aaa;"
                "  border-radius: 5px;"
                "  margin-top: 10px;"
                "  padding: 6px 4px 4px 4px;"
                "}"
                "QGroupBox::title {"
                "  subcontrol-origin: margin;"
                "  left: 10px;"
                "  padding: 0 4px;"
                "}"
            )
            inner = QVBoxLayout(group)
            inner.setSpacing(5)

            for item in (layout_items or []):
                if isinstance(item, QWidget):
                    inner.addWidget(item)
                else:  # assume any QLayout subclass
                    inner.addLayout(item)

            return group
        except Exception as e:
            print(f"[UIComponents][ERROR in create_boxed_group] {e}")
            return QGroupBox(title)
    
    @staticmethod
    def create_radio_group(options: list, default_index: int = 0) -> tuple:
        """
        Create a radio button group with given options.
        
        Args:
            options: List of option labels
            default_index: Index of default selected option
            
        Returns:
            tuple: (QButtonGroup, list of QRadioButton)
        """
        try:
            btn_group = QButtonGroup()
            radio_buttons = []
            
            for idx, option in enumerate(options):
                rb = QRadioButton(option)
                btn_group.addButton(rb, idx)
                radio_buttons.append(rb)
                
                if idx == default_index:
                    rb.setChecked(True)
            
            return btn_group, radio_buttons
        except Exception as e:
            print(f"[UIComponents][ERROR in create_radio_group] {e}")
            return QButtonGroup(), []
    
    @staticmethod
    def create_checkbox_group(options: list) -> list:
        """
        Create a list of checkboxes.
        
        Args:
            options: List of checkbox labels
            
        Returns:
            list: List of QCheckBox
        """
        try:
            checkboxes = []
            for option in options:
                cb = QCheckBox(option)
                checkboxes.append(cb)
            return checkboxes
        except Exception as e:
            print(f"[UIComponents][ERROR in create_checkbox_group] {e}")
            return []
    
    @staticmethod
    def create_checkbox_with_textfield(label: str, placeholder: str = "", max_width: int = 250) -> tuple:
        """
        Create a checkbox with an associated text field.
        
        Args:
            label: Checkbox label
            placeholder: Placeholder text for text field
            max_width: Maximum width of text field
            
        Returns:
            tuple: (QCheckBox, QLineEdit)
        """
        try:
            checkbox = QCheckBox(label)
            textfield = QLineEdit()
            textfield.setPlaceholderText(placeholder)
            textfield.setMaximumWidth(max_width)
            return checkbox, textfield
        except Exception as e:
            print(f"[UIComponents][ERROR in create_checkbox_with_textfield] {e}")
            return QCheckBox(label), QLineEdit()
    
    @staticmethod
    def create_horizontal_layout(widgets: list, add_stretch: bool = True) -> QHBoxLayout:
        """
        Create a horizontal layout with given widgets.
        
        Args:
            widgets: List of widgets to add
            add_stretch: Whether to add stretch at the end
            
        Returns:
            QHBoxLayout
        """
        try:
            layout = QHBoxLayout()
            for widget in widgets:
                layout.addWidget(widget)
            if add_stretch:
                layout.addStretch()
            return layout
        except Exception as e:
            print(f"[UIComponents][ERROR in create_horizontal_layout] {e}")
            return QHBoxLayout()
        



        