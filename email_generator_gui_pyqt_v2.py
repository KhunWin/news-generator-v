import os
import time

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QTextEdit, QPushButton,
    QCheckBox, QRadioButton, QButtonGroup, QGroupBox,
    QScrollArea, QFileDialog, QSizePolicy, QFrame,
)

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from config import Config
from receiver_manager import ReceiverManager
from email_formatter_v3 import EmailFormatter
from outlook_sender import OutlookEmailSender
from richtexteditor_v2 import RichTextEditor
from PopEmailConfig import PopEmailConfig
from csv_logger import EmailRecordLogger


# ══════════════════════════════════════════════════════════════════════
#  SOCEmailGeneratorApp
# ══════════════════════════════════════════════════════════════════════

class SOCEmailGeneratorApp(QMainWindow):
    """Main PyQt5 GUI — mirrors the Flet layout with selection-aware rich-text editors."""

    def __init__(self):
        super().__init__()
        try:
            print("[SOCEmailGeneratorApp] Initializing UI...")
            self.setWindowTitle("SOC Security News Email Generator")

            # # ADD THIS DARK STYLESHEET HERE ↓
            self.setStyleSheet("""
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
            """)


            self.resize(1500, 960)
            self.config           = Config()
            self.receiver_manager = ReceiverManager(self.config.RECEIVERS_DIR)
            # self.formatter        = EmailFormatter("default_signature.html")
            self.formatter        = EmailFormatter()
            self.pop_config       = PopEmailConfig(None)
            self.sender           = OutlookEmailSender(self.config)
            self.recommendation_mode = "recommendation"  # default value
            self.csv_logger = EmailRecordLogger(self.config.RECEIVERS_DIR)


            self._build_ui()
            print("[SOCEmailGeneratorApp] UI ready.")
        except Exception as e:
            print(f"[SOCEmailGeneratorApp][ERROR in __init__] {e}")


    def _boxed(self, title: str, layout_items: list = None) -> QGroupBox:
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
                else:                        # assume any QLayout subclass
                    inner.addLayout(item)

            return group
        except Exception as e:
            print(f"[SOCEmailGeneratorApp][ERROR in _boxed] {e}")
            return QGroupBox(title)

    def _build_ui(self):
        print("This is in the _build_ui function--------------old version------------------")
        try:
            # ── scroll wrapper ──────────────────────────────────────────
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)

            content_widget = QWidget()
            main_h = QHBoxLayout(content_widget)
            main_h.setSpacing(30)
            main_h.setAlignment(Qt.AlignTop)

            scroll.setWidget(content_widget)
            self.setCentralWidget(scroll)

            # ════════════════════════════════════════════════════════════
            #  LEFT COLUMN
            # ════════════════════════════════════════════════════════════
            left_w = QWidget()
            left_v = QVBoxLayout(left_w)
            left_v.setSpacing(10)
            left_v.setAlignment(Qt.AlignTop)

            # App heading
            heading = QLabel("SOC Security News Email Generator")
            heading.setFont(QFont("Arial", 16, QFont.Bold))
            left_v.addWidget(heading)

            # News Title
            # left_v.addWidget(QLabel("News Title (Email Subject)"))

            title_label = QLabel("News Title (Email Subject)")
            title_label.setStyleSheet("font-weight: bold; font-size: 12px;")
            left_v.addWidget(title_label)

            self.tf_title = QLineEdit()
            self.tf_title.setPlaceholderText("Enter email subject…")
            self.tf_title.setMaximumWidth(600)
            self.tf_title.setStyleSheet("QLineEdit { background-color: white; color: black; }")

            left_v.addWidget(self.tf_title)

            # Formatting help note
            help_note = QLabel(
                "Formatting tips:  **bold**   *italic*   - bullet item (on its own line)\n"
                "✦  Select text inside any field, then click  B / I / •≡  to wrap the selection."
            )
            help_note.setStyleSheet(
                "color: #777; font-style: italic; font-size: 10px;"
            )
            help_note.setWordWrap(True)
            left_v.addWidget(help_note)

            # ── Rich editors ────────────────────────────────────────────
            self.editor_summary = RichTextEditor(
                "Summary", min_height=60, max_height=120)
            left_v.addWidget(self.editor_summary)

            # Image 1 row
            img1_row = QHBoxLayout()
            self.tf_image1 = QLineEdit()
            self.tf_image1.setPlaceholderText("File Path (Image 1)")
            self.tf_image1.setMaximumWidth(420)
            btn_pick1  = QPushButton("Select Image")
            btn_clear1 = QPushButton("✕")
            btn_clear1.setFixedWidth(30)
            btn_clear1.setToolTip("Clear Image 1")
            btn_pick1.clicked.connect(lambda: self._pick_file(self.tf_image1))
            btn_clear1.clicked.connect(lambda: self._clear_field(self.tf_image1))
            img1_row.addWidget(self.tf_image1)
            img1_row.addWidget(btn_pick1)
            img1_row.addWidget(btn_clear1)
            img1_row.addStretch()
            left_v.addLayout(img1_row)

            self.editor_content = RichTextEditor(
                "Content 1", min_height=100, max_height=240)
            left_v.addWidget(self.editor_content)

            # Image 2 row
            img2_row = QHBoxLayout()
            self.tf_image2 = QLineEdit()
            self.tf_image2.setPlaceholderText("File Path (Image 2)")
            self.tf_image2.setMaximumWidth(420)
            btn_pick2  = QPushButton("Select Image")
            btn_clear2 = QPushButton("✕")
            btn_clear2.setFixedWidth(30)
            btn_clear2.setToolTip("Clear Image 2")
            btn_pick2.clicked.connect(lambda: self._pick_file(self.tf_image2))
            btn_clear2.clicked.connect(lambda: self._clear_field(self.tf_image2))
            img2_row.addWidget(self.tf_image2)
            img2_row.addWidget(btn_pick2)
            img2_row.addWidget(btn_clear2)
            img2_row.addStretch()
            left_v.addLayout(img2_row)

            self.editor_content2 = RichTextEditor(
                "Content 2 (Optional)", min_height=60, max_height=180)
            left_v.addWidget(self.editor_content2)

            # Recommendation Mode Radio Buttons
            rec_mode_label = QLabel("Recommendation Section:")
            rec_mode_label.setStyleSheet("font-weight: bold; font-size: 12px;")
            left_v.addWidget(rec_mode_label)

            self.recommendation_mode_btn_group = QButtonGroup(self)
            rec_mode_row = QHBoxLayout()

            self.rb_rec_recommendation = QRadioButton("Recommendation:")
            self.rb_rec_none = QRadioButton("None")
            self.rb_rec_recommendation.setChecked(True)  # Default selection

            self.recommendation_mode_btn_group.addButton(self.rb_rec_recommendation)
            self.recommendation_mode_btn_group.addButton(self.rb_rec_none)

            rec_mode_row.addWidget(self.rb_rec_recommendation)
            rec_mode_row.addWidget(self.rb_rec_none)
            rec_mode_row.addStretch()
            left_v.addLayout(rec_mode_row)

            # # Connect to toggle editor visibility
            # self.rb_rec_recommendation.toggled.connect(self._toggle_recommendation_editor)
            # self.rb_rec_none.toggled.connect(self._toggle_recommendation_editor)

            self.editor_recommendation = RichTextEditor(
                "Recommendation (Optional)", min_height=40, max_height=120)
            left_v.addWidget(self.editor_recommendation)

            # Reference
            self.tf_reference = RichTextEditor(
                "Reference (Link)", min_height=40, max_height=120)
            left_v.addWidget(self.tf_reference)

            left_v.addStretch()

            # ════════════════════════════════════════════════════════════
            #  RIGHT COLUMN
            # ════════════════════════════════════════════════════════════
            right_w = QWidget()
            right_v = QVBoxLayout(right_w)
            right_v.setSpacing(10)
            right_v.setAlignment(Qt.AlignTop)

            # ── Receivers ───────────────────────────────────────────────
            receiver_names = self.config.RECEIVER_NAMES
            self.receiver_checkboxes_map = []
            receiver_checkboxes = []

            for idx, name in enumerate(receiver_names, start=1):
                cb = QCheckBox(name)
                setattr(self, f"cb_receiver_{idx}", cb)
                receiver_checkboxes.append(cb)
                self.receiver_checkboxes_map.append((cb, name))

            receivers_per_col = max(1, (len(receiver_checkboxes) + 3) // 4)
            recv_row = QHBoxLayout()
            recv_row.setAlignment(Qt.AlignLeft)

            for col in range(4):
                start = col * receivers_per_col
                end   = min(start + receivers_per_col, len(receiver_checkboxes))
                if start >= len(receiver_checkboxes):
                    break
                col_w = QWidget()
                col_v = QVBoxLayout(col_w)
                col_v.setSpacing(5)
                col_v.setAlignment(Qt.AlignTop)
                for cb in receiver_checkboxes[start:end]:
                    col_v.addWidget(cb)
                recv_row.addWidget(col_w)

            self.cb_receiver_select_all = QCheckBox("Select All")
            self.cb_receiver_select_all.toggled.connect(self._toggle_all_receivers)

            right_v.addWidget(
                self._boxed("To Customer (Receivers)",
                            layout_items=[recv_row, self.cb_receiver_select_all])
            )

            ###adding sender email buttons
            # Create radio buttons for each available sender email
            self.sender_email_btn_group = QButtonGroup(self)
            sender_emails = self.config.AVAILABLE_SENDER_EMAILS
            sender_radios = []
            for email in sender_emails:
                rb = QRadioButton(email)
                self.sender_email_btn_group.addButton(rb)
                sender_radios.append(rb)
                
                # Set default selection
                if email == self.config.DEFAULT_SENDER_EMAIL:
                    rb.setChecked(True)
                
                # Connect to handler
                rb.toggled.connect(lambda checked, e=email: self._on_sender_email_changed(e, checked))
            
            # Layout sender email radio buttons in columns (2 per row for better readability)
            sender_rows = []
            for i in range(0, len(sender_radios), 2):
                row = QHBoxLayout()
                row.addWidget(sender_radios[i])
                if i + 1 < len(sender_radios):
                    row.addWidget(sender_radios[i + 1])
                row.addStretch()
                sender_rows.append(row)
            
            right_v.addWidget(
                self._boxed("Sender Email Address", layout_items=sender_rows)
            )
            ##end of sender email buttons

            # Right after the sender email section and before News Severity
            # Add CC Email Address input
            cc_label = QLabel("CC Email Address (Optional)")
            cc_label.setStyleSheet("font-weight: bold; font-size: 12px;")
            cc_label.setToolTip("Enter multiple email addresses separated by semicolons (;)")

            self.tf_cc_emails = QLineEdit()
            self.tf_cc_emails.setPlaceholderText("email1@example.com; email2@example.com")
            self.tf_cc_emails.setMaximumWidth(600)

            cc_layout = QVBoxLayout()
            cc_layout.addWidget(cc_label)
            cc_layout.addWidget(self.tf_cc_emails)

            right_v.addWidget(
                self._boxed("CC Email Address", layout_items=[cc_layout])
            )

            # ── News Severity ────────────────────────────────────────────
            self.severity_btn_group = QButtonGroup(self)
            sev_row = QHBoxLayout()
            for val in ["Low", "Medium", "High", "Critical"]:
                rb = QRadioButton(val)
                self.severity_btn_group.addButton(rb)
                sev_row.addWidget(rb)
            sev_row.addStretch()
            right_v.addWidget(self._boxed("News Severity", layout_items=[sev_row]))

            # ── Impacted Industry ────────────────────────────────────────
            self.cb_ind_all       = QCheckBox("All")
            self.cb_ind_bank      = QCheckBox("Bank")
            self.cb_ind_logistic  = QCheckBox("Logistic")
            self.cb_ind_enterprise= QCheckBox("Enterprise")
            self.cb_ind_gov       = QCheckBox("Government")
            self.cb_ind_others    = QCheckBox("Others")
            self.tf_ind_others    = QLineEdit()
            self.tf_ind_others.setPlaceholderText("Others (specify)")
            self.tf_ind_others.setMaximumWidth(250)

            ind_r1 = QHBoxLayout()
            for w in [self.cb_ind_all, self.cb_ind_bank, self.cb_ind_logistic]:
                ind_r1.addWidget(w)
            ind_r1.addStretch()

            ind_r2 = QHBoxLayout()
            for w in [self.cb_ind_enterprise, self.cb_ind_gov]:
                ind_r2.addWidget(w)
            ind_r2.addStretch()

            ind_r3 = QHBoxLayout()
            ind_r3.addWidget(self.cb_ind_others)
            ind_r3.addWidget(self.tf_ind_others)
            ind_r3.addStretch()

            right_v.addWidget(
                self._boxed("Impacted Industry", layout_items=[ind_r1, ind_r2, ind_r3])
            )

            # ── Threat Intention / Reason ────────────────────────────────
            self.cb_thr_vuln   = QCheckBox("Vulnerability Exploit")
            self.cb_thr_info   = QCheckBox("Information Theft")
            self.cb_thr_fin    = QCheckBox("Financial")
            self.cb_thr_pol    = QCheckBox("Political")
            self.cb_thr_others = QCheckBox("Others")
            self.tf_thr_others = QLineEdit()
            self.tf_thr_others.setPlaceholderText("Others (specify)")
            self.tf_thr_others.setMaximumWidth(250)

            thr_r1 = QHBoxLayout()
            for w in [self.cb_thr_vuln, self.cb_thr_info]:
                thr_r1.addWidget(w)
            thr_r1.addStretch()

            thr_r2 = QHBoxLayout()
            for w in [self.cb_thr_fin, self.cb_thr_pol]:
                thr_r2.addWidget(w)
            thr_r2.addStretch()

            thr_r3 = QHBoxLayout()
            thr_r3.addWidget(self.cb_thr_others)
            thr_r3.addWidget(self.tf_thr_others)
            thr_r3.addStretch()

            right_v.addWidget(
                self._boxed("Threat Intention / Reason",
                            layout_items=[thr_r1, thr_r2, thr_r3])
            )

            # ── Affected Systems ─────────────────────────────────────────
            self.cb_sys_linux  = QCheckBox("Linux")
            self.cb_sys_win    = QCheckBox("Windows")
            self.cb_sys_and    = QCheckBox("Android")
            self.cb_sys_ios    = QCheckBox("iOS")
            self.cb_sys_others = QCheckBox("Others")
            self.tf_sys_others = QLineEdit()
            self.tf_sys_others.setPlaceholderText("Others (specify)")
            self.tf_sys_others.setMaximumWidth(250)

            sys_r1 = QHBoxLayout()
            for w in [self.cb_sys_linux, self.cb_sys_win]:
                sys_r1.addWidget(w)
            sys_r1.addStretch()

            sys_r2 = QHBoxLayout()
            for w in [self.cb_sys_and, self.cb_sys_ios]:
                sys_r2.addWidget(w)
            sys_r2.addStretch()

            sys_r3 = QHBoxLayout()
            sys_r3.addWidget(self.cb_sys_others)
            sys_r3.addWidget(self.tf_sys_others)
            sys_r3.addStretch()

            right_v.addWidget(
                self._boxed("Affected Systems", layout_items=[sys_r1, sys_r2, sys_r3])
            )
            
            # ── Excel Logging Option ─────────────────────────────────────
            self.rb_excel_yes = QRadioButton("Yes")
            self.rb_excel_no = QRadioButton("No")
            self.rb_excel_no.setChecked(True)  # Default to No

            self.excel_btn_group = QButtonGroup(self)
            self.excel_btn_group.addButton(self.rb_excel_yes)
            self.excel_btn_group.addButton(self.rb_excel_no)

            excel_row = QHBoxLayout()
            excel_row.addWidget(self.rb_excel_yes)
            excel_row.addWidget(self.rb_excel_no)
            excel_row.addStretch()

            right_v.addWidget(
                self._boxed("Excel", layout_items=[excel_row])
            )

            # ── Send Mode ────────────────────────────────────────────────
            self.rb_preview = QRadioButton("Preview (To sender only)")
            self.rb_confirm = QRadioButton("Confirm (To customers)")
            self.rb_preview.setChecked(True)

            self.mode_btn_group = QButtonGroup(self)
            self.mode_btn_group.addButton(self.rb_preview, 0)
            self.mode_btn_group.addButton(self.rb_confirm, 1)

            mode_row = QHBoxLayout()
            mode_row.addWidget(self.rb_preview)
            mode_row.addWidget(self.rb_confirm)
            mode_row.addStretch()

            # Button row with Send and Reset
            button_row = QHBoxLayout()

            self.btn_send = QPushButton("Send Email")
            self.btn_send.setStyleSheet(
                "QPushButton {"
                "  background-color: #c0392b; color: white;"
                "  padding: 6px 20px; font-weight: bold; border-radius: 4px;"
                "}"
                "QPushButton:hover  { background-color: #e74c3c; }"
                "QPushButton:pressed{ background-color: #922b21; }"
            )
            self.btn_send.clicked.connect(self._send_email)

            self.btn_reset = QPushButton("Reset Form")
            self.btn_reset.setStyleSheet(
                "QPushButton {"
                "  background-color: #34495e; color: white;"
                "  padding: 6px 20px; font-weight: bold; border-radius: 4px;"
                "}"
                "QPushButton:hover  { background-color: #5d6d7e; }"
                "QPushButton:pressed{ background-color: #2c3e50; }"
            )
            self.btn_reset.clicked.connect(self._reset_form)

            button_row.addWidget(self.btn_send)
            button_row.addWidget(self.btn_reset)
            button_row.addStretch()

            self.status_label = QLabel("")
            self.status_label.setWordWrap(True)

            right_v.addWidget(
                self._boxed("Send Mode",
                            layout_items=[mode_row, button_row, self.status_label])
            )
            right_v.addStretch()

            # ── Assemble columns ─────────────────────────────────────────
            main_h.addWidget(left_w,  stretch=3)
            main_h.addWidget(right_w, stretch=2)

        except Exception as e:
            print(f"[SOCEmailGeneratorApp][ERROR in _build_ui] {e}")

    def _toggle_all_receivers(self, checked: bool):
        try:
            for cb, _ in self.receiver_checkboxes_map:
                cb.setChecked(checked)
        except Exception as ex:
            print(f"[SOCEmailGeneratorApp][ERROR in _toggle_all_receivers] {ex}")

    def _toggle_recommendation_editor(self):
        try:
            if self.rb_rec_recommendation.isChecked():
                # Show editor, hide "None" text
                self.editor_recommendation.setVisible(True)
                if hasattr(self, 'lbl_rec_none'):
                    self.lbl_rec_none.setVisible(False)
            else:
                # Hide editor, show "None" text
                self.editor_recommendation.setVisible(False)
                if hasattr(self, 'lbl_rec_none'):
                    self.lbl_rec_none.setVisible(True)
        except Exception as e:
            print(f"[SOCEmailGeneratorApp][ERROR in _toggle_recommendation_editor] {e}")

    ##remove this function when sender email button is removed
    def _on_sender_email_changed(self, email: str, checked: bool):
        """Handle sender email radio button change."""
        try:
            if checked:  # Only act when button is checked (not unchecked)
                self.config.update_sender_email(email)
                print(f"[SOCEmailGeneratorApp] Sender email changed to: {email}")
        except Exception as ex:
            print(f"[SOCEmailGeneratorApp][ERROR in _on_sender_email_changed] {ex}")


    def _clear_field(self, tf: QLineEdit):
        try:
            tf.clear()
        except Exception as e:
            print(f"[SOCEmailGeneratorApp][ERROR in _clear_field] {e}")

    def _pick_file(self, target_field: QLineEdit):
        """Synchronous file dialog — replaces Flet's async FilePicker."""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Select Image",
                "",
                "Images (*.png *.jpg *.jpeg *.gif *.bmp)"
            )
            if file_path:
                target_field.setText(file_path)
                print(f"[SOCEmailGeneratorApp] Picked: {file_path}")
        except Exception as e:
            print(f"[SOCEmailGeneratorApp][ERROR in _pick_file] {e}")

    def _collect_form(self) -> dict:
        try:

            industries = []
            if self.cb_ind_all.isChecked():        industries.append("All")
            if self.cb_ind_bank.isChecked():       industries.append("Bank")
            if self.cb_ind_logistic.isChecked():   industries.append("Logistic")
            if self.cb_ind_enterprise.isChecked(): industries.append("Enterprise")
            if self.cb_ind_gov.isChecked():        industries.append("Government")
            if self.cb_ind_others.isChecked() and self.tf_ind_others.text().strip():
                industries.append(self.tf_ind_others.text().strip())

            threats = []
            if self.cb_thr_vuln.isChecked():  threats.append("Vulnerability Exploit")
            if self.cb_thr_info.isChecked():  threats.append("Information Theft")
            if self.cb_thr_fin.isChecked():   threats.append("Financial")
            if self.cb_thr_pol.isChecked():   threats.append("Political")
            if self.cb_thr_others.isChecked() and self.tf_thr_others.text().strip():
                threats.append(self.tf_thr_others.text().strip())

            systems = []
            if self.cb_sys_linux.isChecked(): systems.append("Linux")
            if self.cb_sys_win.isChecked():   systems.append("Windows")
            if self.cb_sys_and.isChecked():   systems.append("Android")
            if self.cb_sys_ios.isChecked():   systems.append("iOS")
            if self.cb_sys_others.isChecked() and self.tf_sys_others.text().strip():
                systems.append(self.tf_sys_others.text().strip())

            sev_btn  = self.severity_btn_group.checkedButton()
            severity = sev_btn.text() if sev_btn else ""
            mode     = "preview" if self.rb_preview.isChecked() else "confirm"

             # Add CC emails parsing
            cc_emails_raw = self.tf_cc_emails.text().strip()
            cc_emails = []
            if cc_emails_raw:
                # Split by semicolon and clean up whitespace
                cc_emails = [email.strip() for email in cc_emails_raw.split(';') if email.strip()]

              # ADD THIS: Collect receiver selections
            selected_receivers = {}
            for cb, receiver_name in self.receiver_checkboxes_map:
                selected_receivers[receiver_name] = cb.isChecked()

            # ADD THIS: Collect Excel logging preference
            log_to_excel = self.rb_excel_yes.isChecked()
            
            return {
                "title":          self.tf_title.text() or "",
                "severity":       severity,
                "industries":     industries,
                "threats":        threats,
                "systems":        systems,
                "summary":        self.editor_summary.value or "",
                "content":        self.editor_content.value or "",
                "content2":       self.editor_content2.value or "",
                "recommendation": self.editor_recommendation.value or "",
                "recommendation_mode": "recommendation" if self.rb_rec_recommendation.isChecked() else "none", 
                "reference":      self.tf_reference.value or "",
                "image1":         self.tf_image1.text() or "",
                "image2":         self.tf_image2.text() or "",
                "mode":           mode,
                "cc_emails":      cc_emails,  
                "selected_receivers": selected_receivers,  
                "log_to_excel":   log_to_excel,            

            }
        except Exception as e:
            print(f"[SOCEmailGeneratorApp][ERROR in _collect_form] {e}")
            return {}

    def _send_email(self):
        try:
            data = self._collect_form()
            if not data.get("title"):
                self._set_status("Please provide a News Title.", "red")
                return

            img1 = data["image1"] if data["image1"] and os.path.exists(data["image1"]) else None
            img2 = data["image2"] if data["image2"] and os.path.exists(data["image2"]) else None

            if data["image1"] and not img1:
                print(f"[SOCEmailGeneratorApp][WARN] Image 1 path not found: {data['image1']}")
            if data["image2"] and not img2:
                print(f"[SOCEmailGeneratorApp][WARN] Image 2 path not found: {data['image2']}")

            # html_builder = lambda cid1, cid2: self.formatter.build_html(data, cid1, cid2)
            

            severity = data.get("severity", "")
            subject = (
                f"[ASL SOC+]Cyber Security News - [{severity}] {data['title']}"
                if severity else
                f"[ASL SOC+]Cyber Security News - {data['title']}"
            )

            mode            = data["mode"]
            receiver_groups = self.receiver_checkboxes_map
            selected_groups = [(cb, n) for cb, n in receiver_groups if cb.isChecked()]

            # is_fdct = any("fdct" in g.lower() for _, g in selected_groups if cb.isChecked())
            # is_fdct = any("fdct" in group_name.lower() for _, group_name in selected_groups)
            # print("[DEBUG] is_fdct (True or FALSE):", is_fdct)

            # html_builder = lambda cid1, cid2: self.formatter.build_html(data, cid1, cid2, is_fdct=is_fdct)


            # Get custom CC emails from form data
            custom_cc_emails = data.get("cc_emails", [])

            # ---- Preview mode ----------------------------------------
            if mode == "preview":
                print("This is in the _build_ui function in Preview--------------old version------------------")

                print("[SOCEmailGeneratorApp] Preview mode -> sending to sender only")
                mtr_selected = any("MTR" in g.upper() for _, g in selected_groups)
                is_fdct_selected = any("fdct" in g.lower() for _, g in selected_groups)
                html_builder = lambda cid1, cid2: self.formatter.build_html(data, cid1, cid2, sender_email=self.config.SENDER_EMAIL)

                if is_fdct_selected:
                    preview_subject = (
                        f"[FDCT]Cyber Security News - [{severity}] {data['title']}"
                        if severity else
                        f"[FDCT]Cyber Security News - {data['title']}"
                    )
                    print("[SOCEmailGeneratorApp] Preview with FDCT format (FDCT group selected)")

                elif mtr_selected:
                    preview_subject = (
                        f"[SOC][MTR]Cyber Security News - [{severity}] {data['title']}"
                        if severity else
                        f"[SOC][MTR]Cyber Security News - {data['title']}"
                    )
                    print("[SOCEmailGeneratorApp] Preview with MTR format (MTR group selected)")
                else:
                    preview_subject = subject
                    print("[SOCEmailGeneratorApp] Preview with regular format (no MTR group selected)")

                # ok = self.sender.send([self.config.SENDER_EMAIL], preview_subject, html_builder, img1, img2, cc_list=self.config.CC_RECIPIENTS)
                preview_cc = self.config.get_cc_for_receiver_group(self.config.SENDER_EMAIL)  # Get CC list for the sender's email address      
                # Use custom CC if provided, otherwise use config
                # preview_cc = custom_cc_emails if custom_cc_emails else self.config.get_cc_for_receiver_group(self.config.SENDER_EMAIL)
            

                if self.pop_config.is_pop_email(self.config.SENDER_EMAIL):
                    print("[SOCEmailGeneratorApp] Detected POP email for preview, using POP sender")
                    ok = self.sender.preview(preview_subject, html_builder, img1, img2)
                else:
                    ok = self.sender.send([self.config.SENDER_EMAIL], preview_subject, html_builder, img1, img2, cc_list=preview_cc, sender_email=self.config.SENDER_EMAIL)
                    print("Printing sender's email for preview in gui:", self.config.SENDER_EMAIL)

                self._set_status(
                    "Preview sent to sender." if ok else "Failed to send preview.",
                    "green" if ok else "red"
                )
                is_fdct_selected = False  # Reset FDCT flag after preview
                return

            # ---- Confirm mode ----------------------------------------
            print(f"-------[SOCEmailGeneratorApp] DEBUG: {len(selected_groups)} receiver group(s) selected.")

            if not selected_groups:
                self._set_status("No receiver group selected.", "red")
                return

            results      = []
            any_selected = False
            print(f"-------[SOCEmailGeneratorApp] Starting to send emails to selected groups (mode before clicking 'send')")
            print("This is in the _build_ui Confirm function--------------old version------------------")

            for checkbox, group_name in receiver_groups:
                if not checkbox.isChecked():
                    continue
                any_selected = True
                emails = self.receiver_manager.load_group(group_name)

                if emails:
                    print(f"[SOCEmailGeneratorApp] Sending to {group_name}: {len(emails)} recipients")

                     # Determine if this is FDCT group
                    is_fdct_group = "fdct" in group_name.lower()
                    # Get appropriate CC list
                    # cc_list = self.config.get_cc_for_receiver_group(group_name)
                    # cc_list = self.config.get_cc_for_receiver_group(self.config.SENDER_EMAIL)  # Get CC list based on group name
                    cc_list = custom_cc_emails if custom_cc_emails else self.config.get_cc_for_receiver_group(self.config.SENDER_EMAIL)

                    print("This is in sending mode, printing sender's email for cc list retrieval:", self.config.SENDER_EMAIL)
                    # Determine subject prefix
                    if is_fdct_group:
                        print("This is sending to fdct group")
                        group_subject = (
                            f"[FDCT]Cyber Security News - [{severity}] {data['title']}"
                            if severity else
                            f"[FDCT]Cyber Security News - {data['title']}"
                        )  
                    elif "MTR" in group_name.upper():
                        group_subject = (
                            f"[SOC][MTRC]Cyber Security News - [{severity}] {data['title']}"
                            if severity else
                            f"[SOC][MTRC]Cyber Security News - {data['title']}"
                        )
                    else:
                        group_subject = subject

                    def make_html_builder(cid1, cid2):
                        # return self.formatter.build_html(data, cid1, cid2, is_fdct=is_fdct_group)
                        return self.formatter.build_html(data, cid1, cid2, sender_email=self.config.SENDER_EMAIL)

                    # ok = self.sender.send(emails, group_subject, make_html_builder, img1, img2)
                    ok = self.sender.send(emails, group_subject, make_html_builder, img1, img2, cc_list=cc_list, sender_email=self.config.SENDER_EMAIL)
                    
                    results.append(
                        f"{group_name}: {'OK' if ok else 'FAIL'} ({len(emails)} recipients)"
                    )
                    time.sleep(1)
                else:
                    results.append(f"{group_name}: SKIPPED (no emails in file)")

            if not any_selected:
                self._set_status("No receiver group selected.", "red")
                return

            status_msg = " | ".join(results)
            ok_color = (
                "green"
                if all("OK" in r for r in results if "SKIPPED" not in r)
                else "orange"
            )
            self._set_status(status_msg, ok_color)
            is_fdct_group = False  # Reset FDCT flag after sending
            print(f"-------[SOCEmailGeneratorApp] Email sending completed.")

            # ADD THIS: Log to CSV if Excel logging is enabled and mode is confirm
            if data.get("log_to_excel") and mode == "confirm":
                print("[SOCEmailGeneratorApp] Logging to CSV...")
                csv_success = self.csv_logger.log_record(data)
                if csv_success:
                    print("[SOCEmailGeneratorApp] CSV logging successful")
                else:
                    print("[SOCEmailGeneratorApp] CSV logging failed")

        except Exception as ex:
            print(f"[SOCEmailGeneratorApp][ERROR in _send_email] {ex}")
            self._set_status(f"Error: {ex}", "red")

    def _set_status(self, text: str, color: str):
        try:
            self.status_label.setText(text)
            self.status_label.setStyleSheet(f"color: {color};")
        except Exception as e:
            print(f"[SOCEmailGeneratorApp][ERROR in _set_status] {e}")

    def _reset_form(self):
        """Reset all form fields to their default state."""
        try:
            print("[SOCEmailGeneratorApp] Resetting form...")
            
            # Clear text fields
            self.tf_title.clear()
            self.tf_image1.clear()
            self.tf_image2.clear()
            self.tf_cc_emails.clear()  # Add this line

            self.tf_ind_others.clear()
            self.tf_thr_others.clear()
            self.tf_sys_others.clear()
            
            # Clear rich text editors
            self.editor_summary.clear()
            self.editor_content.clear()
            self.editor_content2.clear()
            self.editor_recommendation.clear()
            self.tf_reference.clear()
            
            # Uncheck all receiver checkboxes
            for cb, _ in self.receiver_checkboxes_map:
                cb.setChecked(False)
            self.cb_receiver_select_all.setChecked(False)
            
            # Reset severity radio buttons (uncheck all)
            sev_btn = self.severity_btn_group.checkedButton()
            if sev_btn:
                self.severity_btn_group.setExclusive(False)
                sev_btn.setChecked(False)
                self.severity_btn_group.setExclusive(True)
            
            # Uncheck all industry checkboxes
            self.cb_ind_all.setChecked(False)
            self.cb_ind_bank.setChecked(False)
            self.cb_ind_logistic.setChecked(False)
            self.cb_ind_enterprise.setChecked(False)
            self.cb_ind_gov.setChecked(False)
            self.cb_ind_others.setChecked(False)
            
            # Uncheck all threat checkboxes
            self.cb_thr_vuln.setChecked(False)
            self.cb_thr_info.setChecked(False)
            self.cb_thr_fin.setChecked(False)
            self.cb_thr_pol.setChecked(False)
            self.cb_thr_others.setChecked(False)
            
            # Uncheck all system checkboxes
            self.cb_sys_linux.setChecked(False)
            self.cb_sys_win.setChecked(False)
            self.cb_sys_and.setChecked(False)
            self.cb_sys_ios.setChecked(False)
            self.cb_sys_others.setChecked(False)

            # Reset recommendation mode to default
            self.rb_rec_recommendation.setChecked(True)
            
            # Reset to preview mode
            self.rb_preview.setChecked(True)
            # Reset Excel logging to No (add this with other radio button resets)
            self.rb_excel_no.setChecked(True)
            
            # Reset sender email to default
            for btn in self.sender_email_btn_group.buttons():
                if btn.text() == self.config.DEFAULT_SENDER_EMAIL:
                    btn.setChecked(True)
                    break
            
            # Clear status
            self.status_label.setText("")
            
            print("[SOCEmailGeneratorApp] Form reset complete")
            
        except Exception as e:
            print(f"[SOCEmailGeneratorApp][ERROR in _reset_form] {e}")




