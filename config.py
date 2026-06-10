import os, sys
import glob
from discover_acc_v3 import OutlookAccountDiscovery

class Config:
    """Central configuration."""
    def __init__(self):
        try:
            print("[Config] Initializing...")
            
            # --- Email Discovery ---
            
            self.discoverer = OutlookAccountDiscovery()
            
            # Run discovery to get all available email addresses
            if self.discoverer.connect_outlook():
                self.discoverer.discover_personal_accounts()
                self.discoverer.discover_shared_mailboxes()
            
            # Build sorted list of all available sender emails
            self.AVAILABLE_SENDER_EMAILS = []
            for acc in self.discoverer.personal_accounts:
                if acc['email']:
                    self.AVAILABLE_SENDER_EMAILS.append(acc['email'])
            for mb in self.discoverer.shared_mailboxes:
                if mb['email']:
                    self.AVAILABLE_SENDER_EMAILS.append(mb['email'])
            
            # Remove duplicates and sort alphabetically
            self.AVAILABLE_SENDER_EMAILS = sorted(list(set(self.AVAILABLE_SENDER_EMAILS)))
            
            # --- Default sender configuration ---
            # Try to find soc_oper@asl.com.hk as default, otherwise use first available
            self.DEFAULT_SENDER_EMAIL = "soc_oper@asl.com.hk"
            if self.DEFAULT_SENDER_EMAIL not in self.AVAILABLE_SENDER_EMAILS:
                self.DEFAULT_SENDER_EMAIL = self.AVAILABLE_SENDER_EMAILS[0] if self.AVAILABLE_SENDER_EMAILS else ""
            
            self.SENDER_EMAIL = self.DEFAULT_SENDER_EMAIL
            
            # Find the shared mailbox display name for the default sender
            self.SHARED_MAILBOX_DISPLAY = "ASL_HK_SOC_OPER"  # Default fallback
            for mb in self.discoverer.shared_mailboxes:
                if mb['email'] == self.DEFAULT_SENDER_EMAIL:
                    self.SHARED_MAILBOX_DISPLAY = mb['display_name']
                    break
            
            # Static CC recipients (always included)
            self.CC_RECIPIENTS = ["soc_oper@asl.com.hk"]

            
            # Attempt to find the Mail_list folder in the current directory dynamically, whether running as script or exe
            foler_path = self.find_mail_list_folder()
            if foler_path:
                print(f"[Config] Found Mail_list folder at: {foler_path}")
                self.RECEIVERS_DIR = foler_path

                # --- POP Email Configuration ---
                pop_mail_path = self.find_pop_mail_folder()
                if pop_mail_path:
                    print(f"[Config] Found pop_mail folder at: {pop_mail_path}")
                    self.POP_MAIL_DIR = pop_mail_path
                else:
                    print("[Config] pop_mail folder not found")
                    self.POP_MAIL_DIR = None
                
                # --- FDCT Configuration ---
                self.CTM_CC_EMAIL = "security.admin@asl.com.mo"  # Special CC for FDCT receivers

                
            else:
                raise FileNotFoundError("Mail_list folder not found in current directory.")
            
            # Dynamically load receiver names from .txt files
            self.RECEIVER_NAMES = self._get_receiver_names_from_dir()
            
            print(f"[Config] Available sender emails: {self.AVAILABLE_SENDER_EMAILS}")
            print(f"[Config] Default sender: {self.DEFAULT_SENDER_EMAIL}")
            print(f"[Config] Shared mailbox display: {self.SHARED_MAILBOX_DISPLAY}")
            print(f"[Config] Receivers dir: {self.RECEIVERS_DIR}")
            print(f"[Config] Loaded receivers: {self.RECEIVER_NAMES}")
        except Exception as e:
            print(f"[Config][ERROR in __init__] {e}")
            # Fallback values if discovery fails
            self.AVAILABLE_SENDER_EMAILS = ["soc_oper@asl.com.hk"]
            self.DEFAULT_SENDER_EMAIL = "soc_oper@asl.com.hk"
            self.SENDER_EMAIL = "soc_oper@asl.com.hk"
            self.SHARED_MAILBOX_DISPLAY = "ASL_HK_SOC_OPER"
            self.CC_RECIPIENTS = ["soc_oper@asl.com.hk"]
            # self.RECEIVERS_DIR = r"."
            self.RECEIVER_NAMES = self._get_receiver_names_from_dir()

    def _get_receiver_names_from_dir(self):
        """Scans the RECEIVERS_DIR for .txt files and returns their base names."""
        try:
            if not os.path.exists(self.RECEIVERS_DIR):
                print(f"[Config][WARN] Directory does not exist: {self.RECEIVERS_DIR}")
                return []
            
            # Find all .txt files in the directory
            txt_files = glob.glob(os.path.join(self.RECEIVERS_DIR, "*.txt"))
            # Extract the filename without the .txt extension
            names = [os.path.splitext(os.path.basename(f))[0] for f in txt_files]
            
            return sorted(names) # Sort alphabetically for a cleaner GUI
        except Exception as e:
            print(f"[Config][ERROR in _get_receiver_names_from_dir] {e}")
            return []
    
    def update_sender_email(self, new_email):
        """Update the sender email and corresponding shared mailbox display name."""
        try:
            self.SENDER_EMAIL = new_email
            
            # Update shared mailbox display name to match the new sender
            for mb in self.discoverer.shared_mailboxes:
                if mb['email'] == new_email:
                    self.SHARED_MAILBOX_DISPLAY = mb['display_name']
                    print(f"[Config] Updated sender to: {new_email} ({self.SHARED_MAILBOX_DISPLAY})")
                    return
            
            # If not found in shared mailboxes, check personal accounts
            for acc in self.discoverer.personal_accounts:
                if acc['email'] == new_email:
                    self.SHARED_MAILBOX_DISPLAY = acc['display_name']
                    print(f"[Config] Updated sender to: {new_email} ({self.SHARED_MAILBOX_DISPLAY})")
                    return
                    
            print(f"[Config] Updated sender to: {new_email}")
        except Exception as e:
            print(f"[Config][ERROR in update_sender_email] {e}")

    def get_current_directory(self):
        """Get the correct current directory whether running as script or exe"""
        if getattr(sys, 'frozen', False):
            # Running as compiled EXE
            return os.path.dirname(sys.executable)
        else:
            # Running as Python script
            print("it is running as script")
            return os.path.dirname(os.path.abspath(__file__))

    def find_mail_list_folder(self):
        """Find the Mail_list folder in the current directory"""
        current_dir = self.get_current_directory()
        
        # Check if Mail_list folder exists in current directory
        mail_list_path = os.path.join(current_dir, "mail_list")
        
        print(f"[DEBUG] Looking for Mail_list in: {current_dir}")  # Debug output
        
        if os.path.exists(mail_list_path) and os.path.isdir(mail_list_path):
            return mail_list_path
        else:
            return None

    def find_pop_mail_folder(self):
        """Find the pop_mail folder in the current directory"""
        current_dir = self.get_current_directory()
        
        # Check if pop_mail folder exists in current directory
        pop_mail_path = os.path.join(current_dir, "pop_mail")
        
        print(f"[DEBUG] Looking for pop_mail in: {current_dir}")
        
        if os.path.exists(pop_mail_path) and os.path.isdir(pop_mail_path):
            print(f"[DEBUG] Found pop_mail folder at: {pop_mail_path}")
            return pop_mail_path
        else:
            print(f"[DEBUG] pop_mail folder not found in: {current_dir}")
            return None
    
    def get_cc_for_receiver_group(self, group_name):
        """Get the appropriate CC email address based on receiver group."""
        try:

            # # Check if FDCT is in the group name
            # if "fdct" in group_name.lower():
            #     print(f"[Config] Using FDCT CC email for group: {group_name}")
            #     return [self.FDCT_CC_EMAIL]
            if group_name.lower() == "cyberupdate@soc2.ctm.net":
                print(f"[Config] Using sender's email as CC for group: {group_name}")
                return [self.CTM_CC_EMAIL]
            

            else:
                # Use sender's own email as CC
                print(f"[Config] Using sender's email as CC for group: {group_name}")
                return [self.SENDER_EMAIL]
        except Exception as e:
            print(f"[Config][ERROR in get_cc_for_receiver_group] {e}")
            return [self.SENDER_EMAIL]



