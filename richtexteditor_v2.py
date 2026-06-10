from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont,QColor, QBrush


class RichTextEditor(QWidget):
    """
    Rich text editor that preserves HTML formatting from pasted content
    while also allowing manual markdown-style formatting.
    """

    def __init__(self, label_text: str, min_height: int = 60, max_height: int = 200):
        super().__init__()
        try:
            self.label_text = label_text
            layout = QVBoxLayout(self)
            layout.setSpacing(4)
            layout.setContentsMargins(0, 0, 0, 0)

            # Label
            label = QLabel(label_text)
            label.setStyleSheet("font-weight: bold; font-size: 12px;")
            layout.addWidget(label)

            # Toolbar
            toolbar = QHBoxLayout()
            toolbar.setSpacing(5)

            self.btn_bold = QPushButton("B")
            self.btn_bold.setFont(QFont("Arial", 10, QFont.Bold))
            self.btn_bold.setFixedSize(30, 25)
            self.btn_bold.setToolTip("Bold")
            self.btn_bold.clicked.connect(self._apply_bold)

            self.btn_italic = QPushButton("I")
            self.btn_italic.setFont(QFont("Arial", 10, QFont.StyleItalic))
            self.btn_italic.setFixedSize(30, 25)
            self.btn_italic.setToolTip("Italic")
            self.btn_italic.clicked.connect(self._apply_italic)

            self.btn_list = QPushButton("•≡")
            self.btn_list.setFixedSize(30, 25)
            self.btn_list.setToolTip("Bullet List")
            self.btn_list.clicked.connect(self._apply_list)

            toolbar.addWidget(self.btn_bold)
            toolbar.addWidget(self.btn_italic)
            toolbar.addWidget(self.btn_list)
            toolbar.addStretch()

            layout.addLayout(toolbar)

            # Text editor - CHANGED TO QTextEdit with HTML support
            self.text_edit = QTextEdit()
            self.text_edit.setMinimumHeight(min_height)
            self.text_edit.setMaximumHeight(max_height)
            self.text_edit.setAcceptRichText(True)  # Enable rich text
             # Set white background for the text editor
            self.text_edit.setStyleSheet("QTextEdit { background-color: white; color: black; }")

            layout.addWidget(self.text_edit)

        except Exception as e:
            print(f"[RichTextEditor][ERROR in __init__] {e}")

    @property
    def value(self) -> str:
        """
        Returns the HTML content of the editor.
        This preserves all formatting including pasted HTML.
        """
        try:
            return self.text_edit.toHtml()
        except Exception as e:
            print(f"[RichTextEditor][ERROR in value getter] {e}")
            return ""

    def _apply_bold(self):
        try:
            cursor = self.text_edit.textCursor()
            if cursor.hasSelection():
                # Use HTML formatting
                fmt = cursor.charFormat()
                font = fmt.font()
                font.setBold(not font.bold())
                fmt.setFont(font)
                cursor.mergeCharFormat(fmt)
            else:
                current_font = self.text_edit.currentFont()
                current_font.setBold(not current_font.bold())
                self.text_edit.setCurrentFont(current_font)
        except Exception as e:
            print(f"[RichTextEditor][ERROR in _apply_bold] {e}")

    def _apply_italic(self):
        try:
            cursor = self.text_edit.textCursor()
            if cursor.hasSelection():
                fmt = cursor.charFormat()
                font = fmt.font()
                font.setItalic(not font.italic())
                fmt.setFont(font)
                cursor.mergeCharFormat(fmt)
            else:
                current_font = self.text_edit.currentFont()
                current_font.setItalic(not current_font.italic())
                self.text_edit.setCurrentFont(current_font)

        except Exception as e:
            print(f"[RichTextEditor][ERROR in _apply_italic] {e}")

    def _apply_list(self):
        try:
            cursor = self.text_edit.textCursor()
            if cursor.hasSelection():
                selected = cursor.selectedText()
                lines = selected.split('\u2029')  # Qt paragraph separator
                formatted_lines = [f"- {line.strip()}" if line.strip() else line 
                                 for line in lines]
                cursor.insertText('\n'.join(formatted_lines))
        except Exception as e:
            print(f"[RichTextEditor][ERROR in _apply_list] {e}")

    def clear(self):
        """Clear the text editor content."""
        try:
            self.text_edit.clear()
        except Exception as e:
            print(f"[RichTextEditor][ERROR in clear] {e}")




