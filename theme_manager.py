# theme_manager.py

class ThemeManager:
    """Manages application themes."""
    
    DARK_THEME = """
        QMainWindow {
                    background-color: #2b2b2b;
                }
                QWidget {
                    background-color: #2b2b2b;
                    color: #e0e0e0;
                }
                QLabel {
                    color: #e0e0e0;
                }
                QLineEdit, QTextEdit, QPlainTextEdit {
                    background-color: #3c3c3c;
                    color: #e0e0e0;
                    border: 1px solid #555;
                    border-radius: 3px;
                    padding: 3px;
                }
                QGroupBox {
                    background-color: #2b2b2b;
                    color: #e0e0e0;
                    border: 1px solid #555;
                }
                QCheckBox, QRadioButton {
                    color: #e0e0e0;
                    spacing: 5px;
                }
                QPushButton {
                    background-color: #4a4a4a;
                    color: #e0e0e0;
                    border: 1px solid #666;
                    border-radius: 3px;
                    padding: 5px 10px;
                }
                QPushButton:hover {
                    background-color: #5a5a5a;
                }
                QScrollArea {
                    background-color: #2b2b2b;
                    border: none;
                }
    """
    
    LIGHT_THEME = """
        /* Default light theme - empty or minimal styling */
        QWidget {
            background-color: #f0f0f0;
            color: #000000;
        }
    """
    
    @classmethod
    def apply_dark_theme(cls, widget):
        """Apply dark theme to widget."""
        widget.setStyleSheet(cls.DARK_THEME)
    
    @classmethod
    def apply_light_theme(cls, widget):
        """Apply light theme to widget."""
        widget.setStyleSheet(cls.LIGHT_THEME)