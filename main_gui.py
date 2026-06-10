# Your main file (original name)
import os
import time

from PyQt5.QtWidgets import QMainWindow, QLineEdit, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt

from config import Config
from receiver_manager import ReceiverManager
from email_formatter_v3 import EmailFormatter
from outlook_sender import OutlookEmailSender
from PopEmailConfig import PopEmailConfig
from csv_logger import EmailRecordLogger
from ui_builder import UIBuilder
from theme_manager import ThemeManager


# ══════════════════════════════════════════════════════════════════════
#  SOCEmailGeneratorApp - Main Application Class
# ══════════════════════════════════════════════════════════════════════

class SOCEmailGeneratorApp(QMainWindow):
    """Main PyQt5 GUI — mirrors the Flet layout with selection-aware rich-text editors."""

    def __init__(self):
        super().__init__()
        try:
            print("[SOCEmailGeneratorApp] Initializing UI...")
            self.setWindowTitle("SOC Security News Email Generator")
            self.resize(1500, 960)
            
            # Apply dark theme
            ThemeManager.apply_dark_theme(self)

            # Initialize core components
            self.config = Config()
            self.receiver_manager = ReceiverManager(self.config.RECEIVERS_DIR)
            self.formatter = EmailFormatter()
            self.pop_config = PopEmailConfig(None)
            self.sender = OutlookEmailSender(self.config)
            self.recommendation_mode = "recommendation"  # default value
            self.csv_logger = EmailRecordLogger(self.config.RECEIVERS_DIR)

            # Build UI using UIBuilder
            self.ui_builder = UIBuilder(self)
            self.ui_builder.build_main_ui()
            
            print("[SOCEmailGeneratorApp] UI ready.")
        except Exception as e:
            print(f"[SOCEmailGeneratorApp][ERROR in __init__] {e}")

    # ══════════════════════════════════════════════════════════════════
    #  UI Interaction Methods
    # ══════════════════════════════════════════════════════════════════

    def _toggle_all_receivers(self, checked: bool):
        """Toggle all receiver checkboxes."""
        try:
            for cb, _ in self.receiver_checkboxes_map:
                cb.setChecked(checked)
        except Exception as ex:
            print(f"[SOCEmailGeneratorApp][ERROR in _toggle_all_receivers] {ex}")

    def _on_sender_email_changed(self, email: str, checked: bool):
        """Handle sender email radio button change."""
        try:
            if checked:  # Only act when button is checked (not unchecked)
                self.config.update_sender_email(email)
                print(f"[SOCEmailGeneratorApp] Sender email changed to: {email}")
        except Exception as ex:
            print(f"[SOCEmailGeneratorApp][ERROR in _on_sender_email_changed] {ex}")

    def _clear_field(self, tf: QLineEdit):
        """Clear a text field."""
        try:
            tf.clear()
        except Exception as e:
            print(f"[SOCEmailGeneratorApp][ERROR in _clear_field] {e}")

    def _pick_file(self, target_field: QLineEdit):
        """Open file dialog to select an image."""
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

    def _set_status(self, text: str, color: str):
        """Update status label with colored text."""
        try:
            self.status_label.setText(text)
            self.status_label.setStyleSheet(f"color: {color};")
        except Exception as e:
            print(f"[SOCEmailGeneratorApp][ERROR in _set_status] {e}")


    # def _on_receiver_checkbox_changed(self, receiver_name: str, state: int):
    #     """Handle receiver checkbox changes - auto-select sender for FDCT."""
    #     try:
    #         # Check if FDCT is being selected (state == 2 means checked)
    #         if state == 2 and ("fdct" in receiver_name.lower()):
    #             print(f"[SOCEmailGeneratorApp] FDCT selected, switching to cyberupdate@soc2.ctm.net")
                
    #             # Find and check the cyberupdate@soc2.ctm.net radio button
    #             for btn in self.sender_email_btn_group.buttons():
    #                 if btn.text() == "cyberupdate@soc2.ctm.net":
    #                     btn.setChecked(True)
    #                     self._on_sender_email_changed("cyberupdate@soc2.ctm.net", True)
    #                     break
            
    #         # When FDCT is unchecked, check if any other FDCT is still selected
    #         elif state == 0 and ("fdct" in receiver_name.lower()):
    #             # Check if any other FDCT checkbox is still checked
    #             any_fdct_checked = any(
    #                 cb.isChecked() and ("fdct" in name.lower())
    #                 for cb, name in self.receiver_checkboxes_map
    #             )
                
    #             # If no FDCT is selected anymore, switch back to default sender
    #             if not any_fdct_checked:
    #                 print(f"[SOCEmailGeneratorApp] No FDCT selected, switching to default sender")
    #                 for btn in self.sender_email_btn_group.buttons():
    #                     if btn.text() == self.config.DEFAULT_SENDER_EMAIL:
    #                         btn.setChecked(True)
    #                         self._on_sender_email_changed(self.config.DEFAULT_SENDER_EMAIL, True)
    #                         break
                            
    #     except Exception as ex:
    #         print(f"[SOCEmailGeneratorApp][ERROR in _on_receiver_checkbox_changed] {ex}")


    def _on_receiver_checkbox_changed(self, receiver_name: str, state: int):
        """Handle receiver checkbox changes - auto-select sender for FDCT."""
        try:
            # Check if FDCT is being selected (state == 2 means checked)
            if state == 2 and ("fdct" in receiver_name.lower()):
                print(f"[SOCEmailGeneratorApp] FDCT selected, switching to cyberupdate@soc2.ctm.net")
                
                # Find and check the cyberupdate@soc2.ctm.net radio button
                for btn in self.sender_email_btn_group.buttons():
                    if btn.text() == "cyberupdate@soc2.ctm.net":
                        old_sender = self.config.SENDER_EMAIL
                        btn.setChecked(True)
                        self._on_sender_email_changed("cyberupdate@soc2.ctm.net", True)
                        
                        # Show popup notification
                        if old_sender != "cyberupdate@soc2.ctm.net":
                            QMessageBox.information(
                                self,
                                "Sender Email Changed",
                                f"Sender email has been automatically changed to:\n\n"
                                f"cyberupdate@soc2.ctm.net\n\n"
                                f"(FDCT receiver selected)"
                            )
                        break
            
            # When FDCT is unchecked, check if any other FDCT is still selected
            elif state == 0 and ("fdct" in receiver_name.lower()):
                # Check if any other FDCT checkbox is still checked
                any_fdct_checked = any(
                    cb.isChecked() and ("fdct" in name.lower())
                    for cb, name in self.receiver_checkboxes_map
                )
                
                # If no FDCT is selected anymore, switch back to default sender
                if not any_fdct_checked:
                    print(f"[SOCEmailGeneratorApp] No FDCT selected, switching to default sender")
                    old_sender = self.config.SENDER_EMAIL
                    for btn in self.sender_email_btn_group.buttons():
                        if btn.text() == self.config.DEFAULT_SENDER_EMAIL:
                            btn.setChecked(True)
                            self._on_sender_email_changed(self.config.DEFAULT_SENDER_EMAIL, True)
                            
                            # Show popup notification
                            if old_sender != self.config.DEFAULT_SENDER_EMAIL:
                                QMessageBox.information(
                                    self,
                                    "Sender Email Changed",
                                    f"Sender email has been automatically changed back to:\n\n"
                                    f"{self.config.DEFAULT_SENDER_EMAIL}\n\n"
                                    f"(No FDCT receiver selected)"
                                )
                            break
                            
        except Exception as ex:
            print(f"[SOCEmailGeneratorApp][ERROR in _on_receiver_checkbox_changed] {ex}")

            
            
    # ══════════════════════════════════════════════════════════════════
    #  Data Collection and Processing
    # ══════════════════════════════════════════════════════════════════

    def _collect_form(self) -> dict:
        """Collect all form data into a dictionary."""
        print("This is in the _build_ui function--------------new version------------------")

        try:
            # Collect industries
            industries = []
            if self.cb_ind_all.isChecked():
                industries.append("All")
            if self.cb_ind_bank.isChecked():
                industries.append("Bank")
            if self.cb_ind_logistic.isChecked():
                industries.append("Logistic")
            if self.cb_ind_enterprise.isChecked():
                industries.append("Enterprise")
            if self.cb_ind_gov.isChecked():
                industries.append("Government")
            if self.cb_ind_others.isChecked() and self.tf_ind_others.text().strip():
                industries.append(self.tf_ind_others.text().strip())

            # Collect threats
            threats = []
            if self.cb_thr_vuln.isChecked():
                threats.append("Vulnerability Exploit")
            if self.cb_thr_info.isChecked():
                threats.append("Information Theft")
            if self.cb_thr_fin.isChecked():
                threats.append("Financial")
            if self.cb_thr_pol.isChecked():
                threats.append("Political")
            if self.cb_thr_others.isChecked() and self.tf_thr_others.text().strip():
                threats.append(self.tf_thr_others.text().strip())

            # Collect systems
            systems = []
            if self.cb_sys_linux.isChecked():
                systems.append("Linux")
            if self.cb_sys_win.isChecked():
                systems.append("Windows")
            if self.cb_sys_and.isChecked():
                systems.append("Android")
            if self.cb_sys_ios.isChecked():
                systems.append("iOS")
            if self.cb_sys_others.isChecked() and self.tf_sys_others.text().strip():
                systems.append(self.tf_sys_others.text().strip())

            # Get severity
            sev_btn = self.severity_btn_group.checkedButton()
            severity = sev_btn.text() if sev_btn else ""
            
            # Get mode
            mode = "preview" if self.rb_preview.isChecked() else "confirm"

            # Parse CC emails
            cc_emails_raw = self.tf_cc_emails.text().strip()
            cc_emails = []
            if cc_emails_raw:
                cc_emails = [email.strip() for email in cc_emails_raw.split(';') if email.strip()]

            # Collect receiver selections
            selected_receivers = {}
            for cb, receiver_name in self.receiver_checkboxes_map:
                selected_receivers[receiver_name] = cb.isChecked()

            # Get Excel logging preference
            log_to_excel = self.rb_excel_yes.isChecked()
            
            return {
                "title": self.tf_title.text() or "",
                "severity": severity,
                "industries": industries,
                "threats": threats,
                "systems": systems,
                "summary": self.editor_summary.value or "",
                "content": self.editor_content.value or "",
                "content2": self.editor_content2.value or "",
                "recommendation": self.editor_recommendation.value or "",
                "recommendation_mode": "recommendation" if self.rb_rec_recommendation.isChecked() else "none",
                "reference": self.tf_reference.value or "",
                "image1": self.tf_image1.text() or "",
                "image2": self.tf_image2.text() or "",
                "mode": mode,
                "cc_emails": cc_emails,
                "selected_receivers": selected_receivers,
                "log_to_excel": log_to_excel,
            }
        except Exception as e:
            print(f"[SOCEmailGeneratorApp][ERROR in _collect_form] {e}")
            return {}

    # ══════════════════════════════════════════════════════════════════
    #  Email Sending Logic
    # ══════════════════════════════════════════════════════════════════

    def _send_email(self):
        """Handle email sending based on form data."""
        try:
            

            
            data = self._collect_form()
            if not data.get("title"):
                self._set_status("Please provide a News Title.", "red")
                return

            # Validate image paths
            img1 = data["image1"] if data["image1"] and os.path.exists(data["image1"]) else None
            img2 = data["image2"] if data["image2"] and os.path.exists(data["image2"]) else None

            if data["image1"] and not img1:
                print(f"[SOCEmailGeneratorApp][WARN] Image 1 path not found: {data['image1']}")
            if data["image2"] and not img2:
                print(f"[SOCEmailGeneratorApp][WARN] Image 2 path not found: {data['image2']}")

            # Build subject
            severity = data.get("severity", "")
            subject = (
                f"[ASL SOC+]Cyber Security News - [{severity}] {data['title']}"
                if severity else
                f"[ASL SOC+]Cyber Security News - {data['title']}"
            )

            mode = data["mode"]
            receiver_groups = self.receiver_checkboxes_map
            selected_groups = [(cb, n) for cb, n in receiver_groups if cb.isChecked()]

            # Get custom CC emails
            custom_cc_emails = data.get("cc_emails", [])

            # ---- Preview mode ----------------------------------------
            if mode == "preview":
                print("[SOCEmailGeneratorApp] Preview mode -> sending to sender only")
                mtr_selected = any("MTR" in g.upper() for _, g in selected_groups)
                is_fdct_selected = any("fdct" in g.lower() for _, g in selected_groups)
                
                html_builder = lambda cid1, cid2: self.formatter.build_html(
                    data, cid1, cid2, sender_email=self.config.SENDER_EMAIL
                )

                if is_fdct_selected:
                    preview_subject = (
                        f"[Preview] [FDCT]Cyber Security News - [{severity}] {data['title']}"
                        if severity else
                        f"[Preview] [FDCT]Cyber Security News - {data['title']}"
                    )
                    print("[SOCEmailGeneratorApp] Preview with FDCT format")
                elif mtr_selected:
                    preview_subject = (
                        f"[Preview] [MTR]Cyber Security News - [{severity}] {data['title']}"
                        if severity else
                        f"[Preview] [MTR]Cyber Security News - {data['title']}"
                    )
                    print("[SOCEmailGeneratorApp] Preview with MTR format")
                else:
                    # preview_subject = subject
                    preview_subject = (
                    f"[Preview] [ASL SOC+]Cyber Security News - [{severity}] {data['title']}"
                    if severity else
                    f"[Preview] [ASL SOC+]Cyber Security News - {data['title']}"
                )
                    print("[SOCEmailGeneratorApp] Preview with regular format")

                preview_cc = self.config.get_cc_for_receiver_group(self.config.SENDER_EMAIL)

                if self.pop_config.is_pop_email(self.config.SENDER_EMAIL):
                    print("[SOCEmailGeneratorApp] Using POP sender for preview")
                    ok = self.sender.preview(preview_subject, html_builder, img1, img2)
                else:
                    ok = self.sender.send(
                        [self.config.SENDER_EMAIL],
                        preview_subject,
                        html_builder,
                        img1,
                        img2,
                        cc_list=preview_cc,
                        sender_email=self.config.SENDER_EMAIL
                    )

                self._set_status(
                    "Preview sent to sender." if ok else "Failed to send preview.",
                    "green" if ok else "red"
                )
                return

            # ---- Confirm mode ----------------------------------------
            print(f"[SOCEmailGeneratorApp] Confirm mode: {len(selected_groups)} group(s) selected")
            print("This is in the _build_ui Confirm function--------------New version------------------")


            if not selected_groups:
                self._set_status("No receiver group selected.", "red")
                return

            results = []
            any_selected = False
            
            for checkbox, group_name in receiver_groups:
                if not checkbox.isChecked():
                    continue
                    
                any_selected = True
                emails = self.receiver_manager.load_group(group_name)

                if emails:
                    print(f"[SOCEmailGeneratorApp] Sending to {group_name}: {len(emails)} recipients")

                    is_fdct_group = "fdct" in group_name.lower()
                    cc_list = (
                        custom_cc_emails if custom_cc_emails
                        else self.config.get_cc_for_receiver_group(self.config.SENDER_EMAIL)
                    )

                    # Determine subject prefix
                    if is_fdct_group:
                        group_subject = (
                            f"[FDCT]Cyber Security News - [{severity}] {data['title']}"
                            if severity else
                            f"[FDCT]Cyber Security News - {data['title']}"
                        )
                    elif "MTR" in group_name.upper():
                        group_subject = (
                            f"[SOC][MTR]Cyber Security News - [{severity}] {data['title']}"
                            if severity else
                            f"[SOC][MTR]Cyber Security News - {data['title']}"
                        )
                    else:
                        group_subject = subject

                    def make_html_builder(cid1, cid2):
                        return self.formatter.build_html(
                            data, cid1, cid2, sender_email=self.config.SENDER_EMAIL
                        )

                    ok = self.sender.send(
                        emails,
                        group_subject,
                        make_html_builder,
                        img1,
                        img2,
                        cc_list=cc_list,
                        sender_email=self.config.SENDER_EMAIL
                    )
                    
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

            # Log to CSV or update last row if enabled and email sent successfully
            if data.get("log_to_excel") and mode == "confirm":
                # Check if all sends were successful
                all_successful = all("OK" in r for r in results if "SKIPPED" not in r)
                
                if all_successful:
                    try:
                        # Check if "Update Last Row" is selected
                        update_last_row = self.rb_update_last_yes.isChecked()
                        update_all_columns = self.rb_update_all_yes.isChecked()
                        
                        if update_last_row:
                            # Update existing row instead of creating new one
                            print("[SOCEmailGeneratorApp] Updating last CSV row...")
                            csv_success = self.csv_logger.update_last_row_receivers(
                                selected_receivers=data.get('selected_receivers', {}),
                                update_all_columns=update_all_columns,
                                form_data=data if update_all_columns else None
                            )
                            if csv_success:
                                print("[SOCEmailGeneratorApp] CSV row update successful")
                            else:
                                print("[SOCEmailGeneratorApp] CSV row update failed")
                        else:
                            # Normal logging - create new record
                            print("[SOCEmailGeneratorApp] Logging to CSV...")
                            csv_success = self.csv_logger.log_record(data)
                            if csv_success:
                                print("[SOCEmailGeneratorApp] CSV logging successful")
                            else:
                                print("[SOCEmailGeneratorApp] CSV logging failed")
                    except Exception as log_err:
                        print(f"[EmailLogger][ERROR] {log_err}")
                else:
                    print("[SOCEmailGeneratorApp] Skipping CSV logging - email send was not fully successful")

        except Exception as ex:
            print(f"[SOCEmailGeneratorApp][ERROR in _send_email] {ex}")
            self._set_status(f"Error: {ex}", "red")

    # ══════════════════════════════════════════════════════════════════
    #  Form Reset
    # ══════════════════════════════════════════════════════════════════

    def _reset_form(self):
        """Reset all form fields to their default state."""
        try:
            print("[SOCEmailGeneratorApp] Resetting form...")
            
            # Clear text fields
            self.tf_title.clear()
            self.tf_image1.clear()
            self.tf_image2.clear()
            self.tf_cc_emails.clear()
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
            
            # Reset severity radio buttons
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
            
            # Reset Excel logging to No
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


