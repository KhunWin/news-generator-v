
import os
import sys
import json
import smtplib
import poplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.parser import Parser
import uuid


class PopEmailConfig:
    """Manages POP3 email configuration and sending."""
    
    def __init__(self, config_dir):
        """
        config_dir: path to the pop_mail folder
        """
        try:
            print(f"[PopEmailConfig] Initializing with directory: {config_dir}")
            self.config_dir = config_dir
            self.pop_emails = self._load_pop_emails()
            
            # Load POP3/SMTP email server configurations from JSON file
            self.pop_config = self._load_pop_config_from_json()
            
            print(f"[PopEmailConfig] Loaded {len(self.pop_config)} POP3 email configurations")
        except Exception as e:
            print(f"[PopEmailConfig][ERROR in __init__] {e}")
            self.pop_emails = []
            self.pop_config = {}
    
    def _get_base_directory(self):
        """Get the base directory where the config file should be located."""
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            base_dir = os.path.dirname(sys.executable)
        else:
            # Running as script
            base_dir = os.path.dirname(os.path.abspath(__file__))
        return base_dir
    
    def _load_pop_config_from_json(self):
        """Load POP3 configuration from JSON file in the current directory."""
        try:
            # Get the base directory
            base_dir = self._get_base_directory()
            
            # Construct path to pop_config.json
            json_path = os.path.join(base_dir, 'pop_config.json')
            
            print(f"[PopEmailConfig] Looking for config file at: {json_path}")
            
            # Check if file exists
            if not os.path.exists(json_path):
                print(f"[PopEmailConfig] Warning: Config file not found at {json_path}")
                print("[PopEmailConfig] Using empty configuration")
                return {}
            
            # Load JSON file
            with open(json_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            print(f"[PopEmailConfig] Successfully loaded config from {json_path}")
            return config
            
        except json.JSONDecodeError as e:
            print(f"[PopEmailConfig][ERROR] Invalid JSON in config file: {e}")
            return {}
        except Exception as e:
            print(f"[PopEmailConfig][ERROR] Failed to load config file: {e}")
            return {}
    
 
    def add_pop_config(self, email, config_dict):
        """Add or update a POP3 configuration."""
        email_lower = email.lower()
        self.pop_config[email_lower] = config_dict
        print(f"[PopEmailConfig] Added/Updated config for {email}")
        return True
    
    def _load_pop_emails(self):
        """Load POP email addresses from txt file in pop_mail folder."""
        try:
            if not os.path.exists(self.config_dir):
                print(f"[PopEmailConfig] pop_mail folder not found: {self.config_dir}")
                return []
            
            # Find the first .txt file in the directory
            txt_files = [f for f in os.listdir(self.config_dir) if f.endswith('.txt')]
            
            if not txt_files:
                print("[PopEmailConfig] No txt file found in pop_mail folder")
                return []
            
            txt_path = os.path.join(self.config_dir, txt_files[0])
            print(f"[PopEmailConfig] Reading POP emails from: {txt_path}")
            
            with open(txt_path, 'r', encoding='utf-8') as f:
                emails = [line.strip().lower() for line in f if line.strip() and '@' in line]
            
            print(f"[PopEmailConfig] Loaded {len(emails)} POP email addresses")
            return emails
            
        except Exception as e:
            print(f"[PopEmailConfig][ERROR in _load_pop_emails] {e}")
            return []
    
    def is_pop_email(self, email):
        """Check if the given email is a POP email."""
        return email.lower() in self.pop_emails
    
    def get_pop_config(self, email):
        """Get POP3/SMTP configuration for a specific email address."""
        try:
            email_lower = email.lower()
            if email_lower in self.pop_config:
                return self.pop_config[email_lower]
            else:
                print(f"[PopEmailConfig][ERROR] No configuration found for {email}")
                print("[PopEmailConfig] Please add configuration in pop_config.json file")
                return None
        except Exception as e:
            print(f"[PopEmailConfig][ERROR in get_pop_config] {e}")
            return None
    

    def send_pop_email(self, sender_email, to_list, cc_list, subject, html_body, image1_path=None, image2_path=None):
        try:
            print(f"[PopEmailConfig] Attempting to send POP3 email from: {sender_email}")
            
            # Get SMTP configuration for this email
            config = self.get_pop_config(sender_email)
            if not config:
                print(f"[PopEmailConfig][ERROR] No SMTP configuration found for {sender_email}")
                print("[PopEmailConfig] Please add configuration in pop_config.json file")
                return False
            
            # Validate password
            if not config.get('password') or config['password'] in ['your_password_here', 'your_app_password', 'your_password']:
                print(f"[PopEmailConfig][ERROR] Password not configured for {sender_email}")
                print("[PopEmailConfig] Please update the password in pop_config.json file")
                return False
            
            # SANITIZE HTML BODY BEFORE SENDING ↓↓↓
            html_body = self._sanitize_email_content(html_body)


            # Create message with HTML support
            msg = MIMEMultipart('related')
            msg['From'] = sender_email
            msg['To'] = ', '.join(to_list)
            if cc_list:
                msg['Cc'] = ', '.join(cc_list)
            msg['Subject'] = subject
            
            # Create the HTML part
            msg_alternative = MIMEMultipart('alternative')
            msg.attach(msg_alternative)
            
            # Process inline images and update HTML
            final_html = html_body
            
            # Handle Image 1
            if image1_path and os.path.exists(image1_path):
                cid1 = uuid.uuid4().hex
                final_html = final_html.replace('cid:IMAGE1_CID', f'cid:{cid1}')
                
                try:
                    with open(image1_path, 'rb') as f:
                        img_data = f.read()
                        img = MIMEImage(img_data)
                        img.add_header('Content-ID', f'<{cid1}>')
                        img.add_header('Content-Disposition', 'inline', filename=os.path.basename(image1_path))
                        msg.attach(img)
                    print(f"[PopEmailConfig] Image 1 attached with CID: {cid1}")
                except Exception as e:
                    print(f"[PopEmailConfig][WARN] Failed to attach image 1: {e}")
            else:
                # Remove image placeholders when no image is attached
                final_html = final_html.replace('cid:IMAGE1_CID', '')
                # Also remove any empty img tags that might be left
                import re
                final_html = re.sub(r'<img[^>]*src=["\']?cid:IMAGE1_CID["\']?[^>]*>', '', final_html, flags=re.IGNORECASE)
                print("[PopEmailConfig] No image 1 attached, removed placeholder")
            
            # Handle Image 2
            if image2_path and os.path.exists(image2_path):
                cid2 = uuid.uuid4().hex
                final_html = final_html.replace('cid:IMAGE2_CID', f'cid:{cid2}')
                
                try:
                    with open(image2_path, 'rb') as f:
                        img_data = f.read()
                        img = MIMEImage(img_data)
                        img.add_header('Content-ID', f'<{cid2}>')
                        img.add_header('Content-Disposition', 'inline', filename=os.path.basename(image2_path))
                        msg.attach(img)
                    print(f"[PopEmailConfig] Image 2 attached with CID: {cid2}")
                except Exception as e:
                    print(f"[PopEmailConfig][WARN] Failed to attach image 2: {e}")
            else:
                # Remove image placeholders when no image is attached
                final_html = final_html.replace('cid:IMAGE2_CID', '')
                # Also remove any empty img tags that might be left
                import re
                final_html = re.sub(r'<img[^>]*src=["\']?cid:IMAGE2_CID["\']?[^>]*>', '', final_html, flags=re.IGNORECASE)
                print("[PopEmailConfig] No image 2 attached, removed placeholder")
            
            # Attach HTML body
            msg_alternative.attach(MIMEText(final_html, 'html', 'utf-8'))
            
            # Prepare all recipients
            all_recipients = to_list + (cc_list if cc_list else [])
            
            print(f"[PopEmailConfig] Connecting to SMTP server: {config['smtp_server']}:{config['smtp_port']}")
            
            # Determine if SSL should be used
            use_ssl = config.get('use_ssl', False)
            
            # Send email via SMTP
            if use_ssl:
                # Use SSL connection for ports like 465
                with smtplib.SMTP_SSL(config['smtp_server'], config['smtp_port']) as server:
                    print("[PopEmailConfig] SSL encryption enabled")
                    # Login
                    server.login(sender_email, config['password'])
                    print("[PopEmailConfig] SMTP authentication successful")
                    
                    # Send email
                    server.send_message(msg)
                    print(f"[PopEmailConfig] Email sent successfully to {len(all_recipients)} recipient(s)")
            else:
                # Use STARTTLS for ports like 587
                with smtplib.SMTP(config['smtp_server'], config['smtp_port']) as server:
                    # Enable TLS if port is 587 or server supports STARTTLS
                    try:
                        server.starttls()
                        print("[PopEmailConfig] TLS encryption enabled")
                    except Exception as e:
                        print(f"[PopEmailConfig][WARN] STARTTLS not available or failed: {e}")
                    
                    # Login
                    server.login(sender_email, config['password'])
                    print("[PopEmailConfig] SMTP authentication successful")
                    
                    # Send email
                    server.send_message(msg)
                    print(f"[PopEmailConfig] Email sent successfully to {len(all_recipients)} recipient(s)")
            
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            print(f"[PopEmailConfig][ERROR] SMTP Authentication failed: {e}")
            print("[PopEmailConfig] Please check email and password in pop_config.json file")
            return False
        except smtplib.SMTPException as e:
            print(f"[PopEmailConfig][ERROR] SMTP error: {e}")
            return False
        except Exception as e:
            print(f"[PopEmailConfig][ERROR in send_pop_email] {e}")
            import traceback
            print(traceback.format_exc())
            return False


    # ADD THIS NEW METHOD TO PopEmailConfig CLASS ↓↓↓
    def _sanitize_email_content(self, html_content):
        # """Sanitize email content to prevent security alerts."""
        # try:
        #     import re
            
        #     # Defang package@version patterns
        #     html_content = re.sub(
        #         r'([\w\-]+)\s*@\s*(\d+\.\d+\.\d+)',
        #         r'\1 version \2',
        #         html_content,
        #         flags=re.IGNORECASE
        #     )
            
        #     # Defang domains (but preserve actual href links)
        #     html_content = re.sub(
        #         r'(?<!href=")(?<!href=\")(?<!["/])(\w+)\.([a-z]{2,})(?!["\'/])',
        #         r'\1[.]\2',
        #         html_content
        #     )
            
        #     print("[PopEmailConfig] Email content sanitized")
        #     return html_content
            
        # except Exception as e:
        #     print(f"[PopEmailConfig][ERROR in _sanitize_email_content] {e}")
        #     return html_content

        return html_content  # Currently returns unsanitized content, can implement sanitization logic as needed









