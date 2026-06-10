# ui_builder.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QCheckBox, QScrollArea, QFileDialog, QGroupBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from ui_components import UIComponents
from richtexteditor_v2 import RichTextEditor


class UIBuilder:
    """Handles all UI construction for SOC Email Generator."""
    
    def __init__(self, parent):
        """
        Args:
            parent: The main application window (SOCEmailGeneratorApp instance)
        """
        self.parent = parent
        self.ui_components = UIComponents()
    
    def build_main_ui(self):
        """Build the complete UI structure."""
        try:
            # Create scroll wrapper
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)

            content_widget = QWidget()
            main_h = QHBoxLayout(content_widget)
            main_h.setSpacing(30)
            main_h.setAlignment(Qt.AlignTop)

            scroll.setWidget(content_widget)
            self.parent.setCentralWidget(scroll)

            # Build left and right columns
            left_widget = self._build_left_column()
            right_widget = self._build_right_column()

            # Assemble columns
            main_h.addWidget(left_widget, stretch=3)
            main_h.addWidget(right_widget, stretch=2)
            
        except Exception as e:
            print(f"[UIBuilder][ERROR in build_main_ui] {e}")
    
    def _build_left_column(self) -> QWidget:
        """Build the left column containing news content fields."""
        try:
            left_w = QWidget()
            left_v = QVBoxLayout(left_w)
            left_v.setSpacing(10)
            left_v.setAlignment(Qt.AlignTop)

            # App heading
            heading = QLabel("SOC Security News Email Generator")
            heading.setFont(QFont("Arial", 16, QFont.Bold))
            left_v.addWidget(heading)

            # News Title
            title_label = QLabel("News Title (Email Subject)")
            title_label.setStyleSheet("font-weight: bold; font-size: 12px;")
            left_v.addWidget(title_label)

            self.parent.tf_title = QLineEdit()
            self.parent.tf_title.setPlaceholderText("Enter email subject…")
            self.parent.tf_title.setMaximumWidth(600)
            self.parent.tf_title.setStyleSheet("QLineEdit { background-color: white; color: black; }")
            left_v.addWidget(self.parent.tf_title)

            # Formatting help note
            help_note = QLabel(
                "Formatting tips:  **bold**   *italic*   - bullet item (on its own line)\n"
                "✦  Select text inside any field, then click  B / I / •≡  to wrap the selection."
            )
            help_note.setStyleSheet("color: #777; font-style: italic; font-size: 10px;")
            help_note.setWordWrap(True)
            left_v.addWidget(help_note)

            # Rich text editors
            self.parent.editor_summary = RichTextEditor("Summary", min_height=60, max_height=120)
            left_v.addWidget(self.parent.editor_summary)

            # Image 1
            left_v.addLayout(self._create_image_picker_row(1))
            
            self.parent.editor_content = RichTextEditor("Content 1", min_height=100, max_height=240)
            left_v.addWidget(self.parent.editor_content)

            # Image 2
            left_v.addLayout(self._create_image_picker_row(2))
            
            self.parent.editor_content2 = RichTextEditor("Content 2 (Optional)", min_height=60, max_height=180)
            left_v.addWidget(self.parent.editor_content2)

            # Recommendation Mode
            left_v.addWidget(self._build_recommendation_mode_section())

            self.parent.editor_recommendation = RichTextEditor("Recommendation (Optional)", min_height=40, max_height=120)
            left_v.addWidget(self.parent.editor_recommendation)

            # Reference
            self.parent.tf_reference = RichTextEditor("Reference (Link)", min_height=40, max_height=120)
            left_v.addWidget(self.parent.tf_reference)

            left_v.addStretch()
            
            return left_w
            
        except Exception as e:
            print(f"[UIBuilder][ERROR in _build_left_column] {e}")
            return QWidget()
    
    def _create_image_picker_row(self, image_number: int) -> QHBoxLayout:
        """Create an image picker row with select and clear buttons."""
        try:
            row = QHBoxLayout()
            
            textfield = QLineEdit()
            textfield.setPlaceholderText(f"File Path (Image {image_number})")
            textfield.setMaximumWidth(420)
            
            btn_pick = QPushButton("Select Image")
            btn_clear = QPushButton("✕")
            btn_clear.setFixedWidth(30)
            btn_clear.setToolTip(f"Clear Image {image_number}")
            
            # Store references in parent
            setattr(self.parent, f"tf_image{image_number}", textfield)
            
            # Connect signals
            btn_pick.clicked.connect(lambda: self.parent._pick_file(textfield))
            btn_clear.clicked.connect(lambda: self.parent._clear_field(textfield))
            
            row.addWidget(textfield)
            row.addWidget(btn_pick)
            row.addWidget(btn_clear)
            row.addStretch()
            
            return row
            
        except Exception as e:
            print(f"[UIBuilder][ERROR in _create_image_picker_row] {e}")
            return QHBoxLayout()
    
    def _build_recommendation_mode_section(self) -> QWidget:
        """Build the recommendation mode radio button section."""
        try:
            section = QWidget()
            layout = QVBoxLayout(section)
            layout.setSpacing(5)
            
            rec_mode_label = QLabel("Recommendation Section:")
            rec_mode_label.setStyleSheet("font-weight: bold; font-size: 12px;")
            layout.addWidget(rec_mode_label)

            btn_group, radio_buttons = self.ui_components.create_radio_group(
                ["Recommendation:", "None"],
                default_index=0
            )
            
            self.parent.recommendation_mode_btn_group = btn_group
            self.parent.rb_rec_recommendation = radio_buttons[0]
            self.parent.rb_rec_none = radio_buttons[1]

            rec_mode_row = self.ui_components.create_horizontal_layout(radio_buttons)
            layout.addLayout(rec_mode_row)
            
            return section
            
        except Exception as e:
            print(f"[UIBuilder][ERROR in _build_recommendation_mode_section] {e}")
            return QWidget()
    
    def _build_right_column(self) -> QWidget:
        """Build the right column containing configuration options."""
        try:
            right_w = QWidget()
            right_v = QVBoxLayout(right_w)
            right_v.setSpacing(10)
            right_v.setAlignment(Qt.AlignTop)

            # Build each section
            right_v.addWidget(self._build_receivers_section())
            right_v.addWidget(self._build_sender_email_section())
            right_v.addWidget(self._build_cc_email_section())
            right_v.addWidget(self._build_severity_section())
            right_v.addWidget(self._build_impacted_industry_section())
            right_v.addWidget(self._build_threat_intention_section())
            right_v.addWidget(self._build_affected_systems_section())
            right_v.addWidget(self._build_excel_logging_section())
            right_v.addWidget(self._build_send_mode_section())
            
            right_v.addStretch()
            
            return right_w
            
        except Exception as e:
            print(f"[UIBuilder][ERROR in _build_right_column] {e}")
            return QWidget()
    
    def _build_receivers_section(self) -> QGroupBox:
        """Build the receivers selection section."""
        try:
            receiver_names = self.parent.config.RECEIVER_NAMES
            self.parent.receiver_checkboxes_map = []
            receiver_checkboxes = []

            for idx, name in enumerate(receiver_names, start=1):
                cb = QCheckBox(name)
                setattr(self.parent, f"cb_receiver_{idx}", cb)
                receiver_checkboxes.append(cb)
                self.parent.receiver_checkboxes_map.append((cb, name))

                 # Connect state change signal for each checkbox (to track fdct)
                cb.stateChanged.connect(
                    lambda state, receiver_name=name: self.parent._on_receiver_checkbox_changed(receiver_name, state)
                )

            # Arrange in 4 columns
            receivers_per_col = max(1, (len(receiver_checkboxes) + 3) // 4)
            recv_row = QHBoxLayout()
            recv_row.setAlignment(Qt.AlignLeft)

            for col in range(4):
                start = col * receivers_per_col
                end = min(start + receivers_per_col, len(receiver_checkboxes))
                if start >= len(receiver_checkboxes):
                    break
                    
                col_w = QWidget()
                col_v = QVBoxLayout(col_w)
                col_v.setSpacing(5)
                col_v.setAlignment(Qt.AlignTop)
                
                for cb in receiver_checkboxes[start:end]:
                    col_v.addWidget(cb)
                    
                recv_row.addWidget(col_w)

            self.parent.cb_receiver_select_all = QCheckBox("Select All")
            self.parent.cb_receiver_select_all.toggled.connect(self.parent._toggle_all_receivers)

            return self.ui_components.create_boxed_group(
                "To Customer (Receivers)",
                layout_items=[recv_row, self.parent.cb_receiver_select_all]
            )
            
        except Exception as e:
            print(f"[UIBuilder][ERROR in _build_receivers_section] {e}")
            return QGroupBox("To Customer (Receivers)")
    
    def _build_sender_email_section(self) -> QGroupBox:
        """Build the sender email selection section."""
        try:
            self.parent.sender_email_btn_group, sender_radios = self.ui_components.create_radio_group(
                self.parent.config.AVAILABLE_SENDER_EMAILS,
                default_index=self.parent.config.AVAILABLE_SENDER_EMAILS.index(
                    self.parent.config.DEFAULT_SENDER_EMAIL
                )
            )
            
            # Connect signals
            for rb in sender_radios:
                email = rb.text()
                rb.toggled.connect(
                    lambda checked, e=email: self.parent._on_sender_email_changed(e, checked)
                )
            
            # Layout in 2 columns
            sender_rows = []
            for i in range(0, len(sender_radios), 2):
                row = QHBoxLayout()
                row.addWidget(sender_radios[i])
                if i + 1 < len(sender_radios):
                    row.addWidget(sender_radios[i + 1])
                row.addStretch()
                sender_rows.append(row)
            
            return self.ui_components.create_boxed_group(
                "Sender Email Address",
                layout_items=sender_rows
            )
            
        except Exception as e:
            print(f"[UIBuilder][ERROR in _build_sender_email_section] {e}")
            return QGroupBox("Sender Email Address")
    
    def _build_cc_email_section(self) -> QGroupBox:
        """Build the CC email input section."""
        try:
            cc_label = QLabel("CC Email Address (Optional)")
            cc_label.setStyleSheet("font-weight: bold; font-size: 12px;")
            cc_label.setToolTip("Enter multiple email addresses separated by semicolons (;)")

            self.parent.tf_cc_emails = QLineEdit()
            self.parent.tf_cc_emails.setPlaceholderText("email1@example.com; email2@example.com")
            self.parent.tf_cc_emails.setMaximumWidth(600)

            cc_layout = QVBoxLayout()
            cc_layout.addWidget(cc_label)
            cc_layout.addWidget(self.parent.tf_cc_emails)

            return self.ui_components.create_boxed_group(
                "CC Email Address",
                layout_items=[cc_layout]
            )
            
        except Exception as e:
            print(f"[UIBuilder][ERROR in _build_cc_email_section] {e}")
            return QGroupBox("CC Email Address")
    
    def _build_severity_section(self) -> QGroupBox:
        """Build the news severity section."""
        try:
            self.parent.severity_btn_group, sev_radios = self.ui_components.create_radio_group(
                ["Low", "Medium", "High", "Critical"],
                default_index=-1  # None selected by default
            )
            
            sev_row = self.ui_components.create_horizontal_layout(sev_radios)
            
            return self.ui_components.create_boxed_group(
                "News Severity",
                layout_items=[sev_row]
            )
            
        except Exception as e:
            print(f"[UIBuilder][ERROR in _build_severity_section] {e}")
            return QGroupBox("News Severity")
    
    def _build_impacted_industry_section(self) -> QGroupBox:
        """Build the impacted industry section."""
        try:
            industries = ["All", "Bank", "Logistic", "Enterprise", "Government"]
            checkboxes = self.ui_components.create_checkbox_group(industries)
            
            self.parent.cb_ind_all = checkboxes[0]
            self.parent.cb_ind_bank = checkboxes[1]
            self.parent.cb_ind_logistic = checkboxes[2]
            self.parent.cb_ind_enterprise = checkboxes[3]
            self.parent.cb_ind_gov = checkboxes[4]
            
            self.parent.cb_ind_others, self.parent.tf_ind_others = \
                self.ui_components.create_checkbox_with_textfield("Others", "Others (specify)")

            ind_r1 = self.ui_components.create_horizontal_layout(checkboxes[:3])
            ind_r2 = self.ui_components.create_horizontal_layout(checkboxes[3:])
            ind_r3 = self.ui_components.create_horizontal_layout([
                self.parent.cb_ind_others,
                self.parent.tf_ind_others
            ])

            return self.ui_components.create_boxed_group(
                "Impacted Industry",
                layout_items=[ind_r1, ind_r2, ind_r3]
            )
            
        except Exception as e:
            print(f"[UIBuilder][ERROR in _build_impacted_industry_section] {e}")
            return QGroupBox("Impacted Industry")
    
    def _build_threat_intention_section(self) -> QGroupBox:
        """Build the threat intention section."""
        try:
            threats = ["Vulnerability Exploit", "Information Theft", "Financial", "Political"]
            checkboxes = self.ui_components.create_checkbox_group(threats)
            
            self.parent.cb_thr_vuln = checkboxes[0]
            self.parent.cb_thr_info = checkboxes[1]
            self.parent.cb_thr_fin = checkboxes[2]
            self.parent.cb_thr_pol = checkboxes[3]
            
            self.parent.cb_thr_others, self.parent.tf_thr_others = \
                self.ui_components.create_checkbox_with_textfield("Others", "Others (specify)")

            thr_r1 = self.ui_components.create_horizontal_layout(checkboxes[:2])
            thr_r2 = self.ui_components.create_horizontal_layout(checkboxes[2:])
            thr_r3 = self.ui_components.create_horizontal_layout([
                self.parent.cb_thr_others,
                self.parent.tf_thr_others
            ])

            return self.ui_components.create_boxed_group(
                "Threat Intention / Reason",
                layout_items=[thr_r1, thr_r2, thr_r3]
            )
            
        except Exception as e:
            print(f"[UIBuilder][ERROR in _build_threat_intention_section] {e}")
            return QGroupBox("Threat Intention / Reason")
    
    def _build_affected_systems_section(self) -> QGroupBox:
        """Build the affected systems section."""
        try:
            systems = ["Linux", "Windows", "Android", "iOS"]
            checkboxes = self.ui_components.create_checkbox_group(systems)
            
            self.parent.cb_sys_linux = checkboxes[0]
            self.parent.cb_sys_win = checkboxes[1]
            self.parent.cb_sys_and = checkboxes[2]
            self.parent.cb_sys_ios = checkboxes[3]
            
            self.parent.cb_sys_others, self.parent.tf_sys_others = \
                self.ui_components.create_checkbox_with_textfield("Others", "Others (specify)")

            sys_r1 = self.ui_components.create_horizontal_layout(checkboxes[:2])
            sys_r2 = self.ui_components.create_horizontal_layout(checkboxes[2:])
            sys_r3 = self.ui_components.create_horizontal_layout([
                self.parent.cb_sys_others,
                self.parent.tf_sys_others
            ])

            return self.ui_components.create_boxed_group(
                "Affected Systems",
                layout_items=[sys_r1, sys_r2, sys_r3]
            )
            
        except Exception as e:
            print(f"[UIBuilder][ERROR in _build_affected_systems_section] {e}")
            return QGroupBox("Affected Systems")
    
    # def _build_excel_logging_section(self) -> QGroupBox:
    #     """Build the Excel logging option section."""
    #     try:
    #         self.parent.excel_btn_group, excel_radios = self.ui_components.create_radio_group(
    #             ["Yes", "No"],
    #             default_index=1  # Default to No
    #         )
            
    #         self.parent.rb_excel_yes = excel_radios[0]
    #         self.parent.rb_excel_no = excel_radios[1]

    #         excel_row = self.ui_components.create_horizontal_layout(excel_radios)

    #         return self.ui_components.create_boxed_group(
    #             "Excel",
    #             layout_items=[excel_row]
    #         )
            
    #     except Exception as e:
    #         print(f"[UIBuilder][ERROR in _build_excel_logging_section] {e}")
    #         return QGroupBox("Excel")
    
    def _build_excel_logging_section(self) -> QGroupBox:
        """Build the Excel logging option section with update options."""
        try:
            # Excel Yes/No
            self.parent.excel_btn_group, excel_radios = self.ui_components.create_radio_group(
                ["Yes", "No"],
                default_index=1  # Default to No
            )
            
            self.parent.rb_excel_yes = excel_radios[0]
            self.parent.rb_excel_no = excel_radios[1]

            excel_row = self.ui_components.create_horizontal_layout(excel_radios)
            
            # Update Last Row option
            self.parent.update_last_btn_group, update_last_radios = self.ui_components.create_radio_group(
                ["Yes", "No"],
                default_index=1  # Default to No
            )
            
            self.parent.rb_update_last_yes = update_last_radios[0]
            self.parent.rb_update_last_no = update_last_radios[1]
            
            update_last_label = QLabel("Update Last Row:")
            update_last_label.setStyleSheet("font-size: 11px; margin-top: 8px;")
            update_last_row = self.ui_components.create_horizontal_layout(update_last_radios)
            
            # Update All Columns option
            self.parent.update_all_btn_group, update_all_radios = self.ui_components.create_radio_group(
                ["Yes", "No"],
                default_index=1  # Default to No
            )
            
            self.parent.rb_update_all_yes = update_all_radios[0]
            self.parent.rb_update_all_no = update_all_radios[1]
            
            update_all_label = QLabel("Update All Columns:")
            update_all_label.setStyleSheet("font-size: 11px;")
            update_all_row = self.ui_components.create_horizontal_layout(update_all_radios)

            return self.ui_components.create_boxed_group(
                "Excel",
                layout_items=[
                    excel_row,
                    update_last_label,
                    update_last_row,
                    update_all_label,
                    update_all_row
                ]
            )
            
        except Exception as e:
            print(f"[UIBuilder][ERROR in _build_excel_logging_section] {e}")
            return QGroupBox("Excel")


    def _build_send_mode_section(self) -> QGroupBox:
        """Build the send mode and action buttons section."""
        try:
            self.parent.mode_btn_group, mode_radios = self.ui_components.create_radio_group(
                ["Preview (To sender only)", "Confirm (To customers)"],
                default_index=0
            )
            
            self.parent.rb_preview = mode_radios[0]
            self.parent.rb_confirm = mode_radios[1]

            mode_row = self.ui_components.create_horizontal_layout(mode_radios)

            # Button row
            button_row = QHBoxLayout()

            self.parent.btn_send = QPushButton("Send Email")
            self.parent.btn_send.setStyleSheet(
                "QPushButton {"
                "  background-color: #c0392b; color: white;"
                "  padding: 6px 20px; font-weight: bold; border-radius: 4px;"
                "}"
                "QPushButton:hover  { background-color: #e74c3c; }"
                "QPushButton:pressed{ background-color: #922b21; }"
            )
            self.parent.btn_send.clicked.connect(self.parent._send_email)

            self.parent.btn_reset = QPushButton("Reset Form")
            self.parent.btn_reset.setStyleSheet(
                "QPushButton {"
                "  background-color: #34495e; color: white;"
                "  padding: 6px 20px; font-weight: bold; border-radius: 4px;"
                "}"
                "QPushButton:hover  { background-color: #5d6d7e; }"
                "QPushButton:pressed{ background-color: #2c3e50; }"
            )
            self.parent.btn_reset.clicked.connect(self.parent._reset_form)

            button_row.addWidget(self.parent.btn_send)
            button_row.addWidget(self.parent.btn_reset)
            button_row.addStretch()

            self.parent.status_label = QLabel("")
            self.parent.status_label.setWordWrap(True)

            return self.ui_components.create_boxed_group(
                "Send Mode",
                layout_items=[mode_row, button_row, self.parent.status_label]
            )
            
        except Exception as e:
            print(f"[UIBuilder][ERROR in _build_send_mode_section] {e}")
            return QGroupBox("Send Mode")
        




