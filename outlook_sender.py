import os
import uuid
import win32com.client
from PopEmailConfig import PopEmailConfig


class OutlookEmailSender:
    """Sends email through Outlook from a shared mailbox with inline images."""
    PR_ATTACH_CONTENT_ID = "http://schemas.microsoft.com/mapi/proptag/0x3712001F"
    PR_SENDER_EMAIL = "http://schemas.microsoft.com/mapi/proptag/0x0C1F001F"

    def __init__(self, config):
        try:
            print("[OutlookEmailSender] Initialized")
            self.config = config

            # Initialize POP email configuration
            if hasattr(config, 'POP_MAIL_DIR') and config.POP_MAIL_DIR:
                self.pop_config = PopEmailConfig(config.POP_MAIL_DIR)
            else:
                self.pop_config = None
            ##end of pop email

        except Exception as e:
            print(f"[OutlookEmailSender][ERROR in __init__] {e}")

    def _get_outlook(self):
        try:
            print("[OutlookEmailSender] Connecting to Outlook...")
            outlook = win32com.client.Dispatch("Outlook.Application")
            namespace = outlook.GetNamespace("MAPI")
            return outlook, namespace
        except Exception as e:
            print(f"[OutlookEmailSender][ERROR in _get_outlook] {e}")
            return None, None

    def _attach_inline_image(self, mail, image_path):
        """Attach an image inline and return its Content-ID."""
        try:
            if not image_path or not os.path.exists(image_path):
                return None
            cid = uuid.uuid4().hex
            attachment = mail.Attachments.Add(image_path)
            attachment.PropertyAccessor.SetProperty(self.PR_ATTACH_CONTENT_ID, cid)
            print(f"[OutlookEmailSender] Inline image attached: {image_path} (cid={cid})")
            return cid
        except Exception as e:
            print(f"[OutlookEmailSender][ERROR in _attach_inline_image] {e}")
            return None

    def send(self, to_list, subject, html_builder, image1_path=None, image2_path=None, cc_list=None, sender_email=None): #add is_fdct=False parameter for pop
        """
        to_list: list[str] recipients for ONE group
        html_builder: callable(cid1, cid2) -> html string
                      (we need CIDs before we can build the HTML)
        """
        try:

            # Check if this is a POP email
            if self.pop_config and self.pop_config.is_pop_email(self.config.SENDER_EMAIL):
                print(f"[OutlookEmailSender] Detected POP email: {self.config.SENDER_EMAIL}")
                print("[OutlookEmailSender] Using POP/SMTP sending method")
                
                # Build HTML with dummy CIDs first (they'll be replaced in pop_config)
                html_body = html_builder("IMAGE1_CID", "IMAGE2_CID")
                
                return self.pop_config.send_pop_email(
                    self.config.SENDER_EMAIL,
                    to_list,
                    cc_list,
                    subject,
                    html_body,
                    image1_path,
                    image2_path
                )
            ##end of checking pop email
            
            if not to_list:
                print("[OutlookEmailSender] No recipients. Skipping.")
                return False

            outlook, namespace = self._get_outlook()
            if not outlook:
                return False

            # Find shared mailbox store (same approach as your working script)
            shared_store = None
            stores = namespace.Stores
            for i in range(1, stores.Count + 1):
                store = stores.Item(i)
                if self.config.SHARED_MAILBOX_DISPLAY in store.DisplayName:
                    shared_store = store
                    print(f"[OutlookEmailSender] Found shared mailbox: {store.DisplayName}")
                    break

            if not shared_store:
                print(f"[OutlookEmailSender][WARN] Shared mailbox "
                      f"'{self.config.SHARED_MAILBOX_DISPLAY}' not found. Using default account.")

            # Create mail item
            mail = outlook.CreateItem(0)  # olMailItem
            mail.To = ";".join(to_list)

            ##adding cc to the email
            # Add CC recipients if provided
            if cc_list:
                mail.CC = ";".join(cc_list)
                print(f"[OutlookEmailSender] CC recipients: {cc_list}")
            ##end of cc
            mail.Subject = subject

            # Attach inline images first so we know their CIDs
            cid1 = self._attach_inline_image(mail, image1_path)
            cid2 = self._attach_inline_image(mail, image2_path)

            # Build HTML now that we have CIDs
            mail.HTMLBody = html_builder(cid1, cid2)

            # Send-from / SentOnBehalfOf logic
            try:
                mail.SentOnBehalfOfName = self.config.SENDER_EMAIL
                print(f"[OutlookEmailSender] SentOnBehalfOfName={self.config.SENDER_EMAIL}")
            except Exception as e:
                print(f"[OutlookEmailSender][WARN] SentOnBehalfOfName failed: {e}")

            try:
                mail.PropertyAccessor.SetProperty(self.PR_SENDER_EMAIL, self.config.SENDER_EMAIL)
                print("[OutlookEmailSender] Set sender via PropertyAccessor")
            except Exception as e:
                print(f"[OutlookEmailSender][WARN] PropertyAccessor failed: {e}")

            # Try matching an account
            try:
                accounts = namespace.Accounts
                for i in range(1, accounts.Count + 1):
                    account = accounts.Item(i)
                    if account.SmtpAddress.lower() == self.config.SENDER_EMAIL.lower():
                        mail.SendUsingAccount = account
                        print("[OutlookEmailSender] SendUsingAccount set")
                        break
            except Exception as e:
                print(f"[OutlookEmailSender][DEBUG] SendUsingAccount not applied: {e}")

            print(f"[OutlookEmailSender] Sending to: {to_list}")
            mail.Send()
            print("[OutlookEmailSender] Email sent.")
            return True

        except Exception as e:
            print(f"[OutlookEmailSender][ERROR in send] {e}")
            import traceback
            print(traceback.format_exc())
            return False

    def preview(self, subject, html_builder, image1_path=None, image2_path=None):
        """
        Send a preview email to the sender's own email address.
        Works with both Outlook and POP email accounts.
        """
        try:
            print("[OutlookEmailSender] Generating preview email...")
            
            # Determine recipient (sender's own email)
            preview_recipient = [self.config.SENDER_EMAIL]
            
            # Check if this is a POP email - use SMTP method for preview
            if self.pop_config and self.pop_config.is_pop_email(self.config.SENDER_EMAIL):
                print(f"[OutlookEmailSender] POP email detected for preview: {self.config.SENDER_EMAIL}")
                print("[OutlookEmailSender] Using POP/SMTP method for preview")
                
                # Add [PREVIEW] to subject
                preview_subject = f"[PREVIEW] {subject}"
                
                # Build HTML with dummy CIDs first (they'll be replaced in pop_config)
                html_body = html_builder("IMAGE1_CID", "IMAGE2_CID")
                
                return self.pop_config.send_pop_email(
                    self.config.SENDER_EMAIL,
                    preview_recipient,
                    None,  # No CC for preview
                    preview_subject,
                    html_body,
                    image1_path,
                    image2_path
                )
            
            # For Outlook emails, use the standard Outlook method
            outlook, namespace = self._get_outlook()
            if not outlook:
                print("[OutlookEmailSender][ERROR] Cannot connect to Outlook for preview")
                return False

            # Create preview mail item
            mail = outlook.CreateItem(0)  # olMailItem
            mail.To = self.config.SENDER_EMAIL
            mail.Subject = f"[PREVIEW] {subject}"

            # Attach inline images
            cid1 = self._attach_inline_image(mail, image1_path)
            cid2 = self._attach_inline_image(mail, image2_path)

            # Build HTML with CIDs
            mail.HTMLBody = html_builder(cid1, cid2)

            # Set sender properties for Outlook
            try:
                mail.SentOnBehalfOfName = self.config.SENDER_EMAIL
            except Exception as e:
                print(f"[OutlookEmailSender][WARN] Preview SentOnBehalfOfName failed: {e}")

            try:
                mail.PropertyAccessor.SetProperty(self.PR_SENDER_EMAIL, self.config.SENDER_EMAIL)
            except Exception as e:
                print(f"[OutlookEmailSender][WARN] Preview PropertyAccessor failed: {e}")

            # Try matching an account
            try:
                accounts = namespace.Accounts
                for i in range(1, accounts.Count + 1):
                    account = accounts.Item(i)
                    if account.SmtpAddress.lower() == self.config.SENDER_EMAIL.lower():
                        mail.SendUsingAccount = account
                        print("[OutlookEmailSender] Preview SendUsingAccount set")
                        break
            except Exception as e:
                print(f"[OutlookEmailSender][DEBUG] Preview SendUsingAccount not applied: {e}")

            print(f"[OutlookEmailSender] Sending preview to: {self.config.SENDER_EMAIL}")
            mail.Send()
            print("[OutlookEmailSender] Preview email sent successfully")
            return True

        except Exception as e:
            print(f"[OutlookEmailSender][ERROR in preview] {e}")
            import traceback
            print(traceback.format_exc())
            return False  


