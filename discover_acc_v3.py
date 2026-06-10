import os
import win32com.client
import re

class OutlookAccountDiscovery:
    """Discover all Outlook accounts and shared mailboxes dynamically."""
    
    def __init__(self):
        self.outlook = None
        self.namespace = None
        self.personal_accounts = []
        self.shared_mailboxes = []
        self.all_email_addresses = []
        
    def connect_outlook(self):
        """Establish connection to Outlook."""
        try:
            print("[Outlook] Connecting...")
            self.outlook = win32com.client.Dispatch("Outlook.Application")
            self.namespace = self.outlook.GetNamespace("MAPI")
            print("[Outlook] Connected successfully")
            return True
        except Exception as e:
            print(f"[Outlook][ERROR] Failed to connect: {e}")
            return False
    
    def discover_personal_accounts(self):
        """Discover personal email accounts from namespace.Accounts."""
        print("\n" + "="*60)
        print("DISCOVERING PERSONAL EMAIL ACCOUNTS")
        print("="*60)
        
        try:
            accounts = self.namespace.Accounts
            print(f"\nFound {accounts.Count} personal account(s):")
            
            for i in range(1, accounts.Count + 1):
                account = accounts.Item(i)
                account_info = {
                    'display_name': account.DisplayName,
                    'email': account.SmtpAddress,
                    'type': 'personal',
                    'account_index': i
                }
                self.personal_accounts.append(account_info)
                self.all_email_addresses.append(account_info)
                
                print(f"\n  Account {i}:")
                print(f"    Display Name: {account.DisplayName}")
                print(f"    Email Address: {account.SmtpAddress}")
                if hasattr(account, 'UserName'):
                    print(f"    User Name: {account.UserName}")
                    
        except Exception as e:
            print(f"[ERROR] Discovering personal accounts: {e}")
    
    def _get_email_from_recipient(self, store_name):
        """Try to get actual email address by creating a temporary recipient."""
        try:
            # Create a temporary mail item to resolve the address
            mail = self.outlook.CreateItem(0)
            recipient = mail.Recipients.Add(store_name)
            recipient.Resolve()
            
            if recipient.Resolved:
                # Get the actual SMTP address
                if hasattr(recipient, 'Address'):
                    # Try to get Exchange address and convert to SMTP
                    exchange_address = recipient.Address
                    if exchange_address and '/o=' in exchange_address:
                        # This is an Exchange address, try to get SMTP
                        try:
                            # Get the property accessor for SMTP address
                            property_accessor = recipient.PropertyAccessor
                            smtp_address = property_accessor.GetProperty("http://schemas.microsoft.com/mapi/proptag/0x39FE001E")
                            if smtp_address:
                                return smtp_address
                        except:
                            pass
                    
                    # If it looks like an email address, return it
                    if '@' in exchange_address and '.' in exchange_address:
                        return exchange_address
                
                # Try to get the entry ID and resolve to SMTP
                if hasattr(recipient, 'AddressEntry'):
                    address_entry = recipient.AddressEntry
                    if address_entry.Type == "EX":
                        # Exchange address - try to get SMTP
                        try:
                            exchange_user = address_entry.GetExchangeUser()
                            if exchange_user:
                                if hasattr(exchange_user, 'PrimarySmtpAddress'):
                                    return exchange_user.PrimarySmtpAddress
                                elif hasattr(exchange_user, 'Address'):
                                    return exchange_user.Address
                        except:
                            pass
                    elif address_entry.Type == "SMTP":
                        return address_entry.Address
            
            return None
        except Exception as e:
            print(f"      [DEBUG] Recipient resolution failed: {e}")
            return None
    
    def _get_email_from_folder(self, store):
        """Extract email address from store's folder properties."""
        try:
            # Get the root folder of the store
            root_folder = store.GetRootFolder()
            
            # Try different property accessor methods
            if root_folder:
                # Method 1: Try to get PR_SMTP_ADDRESS property
                try:
                    property_accessor = root_folder.PropertyAccessor
                    smtp_property = "http://schemas.microsoft.com/mapi/proptag/0x39FE001E"
                    smtp_address = property_accessor.GetProperty(smtp_property)
                    if smtp_address and '@' in smtp_address:
                        return smtp_address
                except:
                    pass
                
                # Method 2: Try to get EmailAddress property
                if hasattr(root_folder, 'EmailAddress'):
                    email = root_folder.EmailAddress
                    if email and '@' in email:
                        return email
                
                # Method 3: Try store name if it contains @
                if hasattr(store, 'DisplayName'):
                    display_name = store.DisplayName
                    if '@' in display_name and '.' in display_name:
                        return display_name
            
            return None
        except Exception as e:
            return None
    
    def _get_email_from_store_property(self, store):
        """Try to get email directly from store properties."""
        try:
            # Try various property accessor methods for the store
            property_accessor = store.PropertyAccessor
            
            # Common property tags for email addresses
            property_tags = [
                "http://schemas.microsoft.com/mapi/proptag/0x39FE001E",  # PR_SMTP_ADDRESS
                "http://schemas.microsoft.com/mapi/proptag/0x0C1F001F",  # PR_SENDER_EMAIL
                "http://schemas.microsoft.com/mapi/proptag/0x0C1A001F",  # PR_SENDER_NAME
                "http://schemas.microsoft.com/mapi/proptag/0x3001001E",  # PR_DISPLAY_NAME
            ]
            
            for tag in property_tags:
                try:
                    value = property_accessor.GetProperty(tag)
                    if value and '@' in str(value):
                        return value
                except:
                    continue
            
            return None
        except:
            return None
    
    def _get_email_from_address_entry(self, store):
        """Get email from address entry associated with the store."""
        try:
            # Get the store's entry ID
            store_id = store.StoreID
            
            # Try to get address entry from Global Address List
            gal = self.namespace.AddressLists.Item("Global Address List")
            if gal:
                for entry in gal.AddressEntries:
                    if entry.Name and entry.Name.lower() == store.DisplayName.lower():
                        if entry.Type == "SMTP":
                            return entry.Address
                        elif entry.Type == "EX":
                            try:
                                exchange_user = entry.GetExchangeUser()
                                if exchange_user and hasattr(exchange_user, 'PrimarySmtpAddress'):
                                    return exchange_user.PrimarySmtpAddress
                            except:
                                pass
            return None
        except:
            return None
    
    def discover_shared_mailboxes(self):
        """Discover all shared mailboxes and extract their actual email addresses."""
        print("\n" + "="*60)
        print("DISCOVERING SHARED MAILBOXES")
        print("="*60)
        
        try:
            stores = self.namespace.Stores
            print(f"\nTotal stores found: {stores.Count}")
            
            # Get current user's primary email to filter out personal stores
            current_user_email = self._get_current_user_email()
            processed_names = set()  # To avoid duplicates
            
            for i in range(1, stores.Count + 1):
                store = stores.Item(i)
                store_name = store.DisplayName
                
                # Skip if it's the personal mailbox
                if current_user_email and current_user_email in store_name:
                    print(f"\n  Skipping personal store: {store_name}")
                    continue
                
                # Skip if we've processed this name before (avoid duplicates)
                if store_name in processed_names:
                    continue
                
                print(f"\n  Processing store: {store_name}")
                
                # Try multiple methods to get the actual email address
                actual_email = None
                
                # Method 1: Try to get from store properties
                print(f"    Attempting to find actual email address...")
                actual_email = self._get_email_from_store_property(store)
                if actual_email:
                    print(f"    ✓ Found via store properties: {actual_email}")
                
                # Method 2: Try from folder properties
                if not actual_email:
                    actual_email = self._get_email_from_folder(store)
                    if actual_email:
                        print(f"    ✓ Found via folder properties: {actual_email}")
                
                # Method 3: Try via recipient resolution
                if not actual_email:
                    actual_email = self._get_email_from_recipient(store_name)
                    if actual_email:
                        print(f"    ✓ Found via recipient resolution: {actual_email}")
                
                # Method 4: Try from address entry
                if not actual_email:
                    actual_email = self._get_email_from_address_entry(store)
                    if actual_email:
                        print(f"    ✓ Found via address entry: {actual_email}")
                
                # Method 5: Try to create a mail and check the sending account
                if not actual_email:
                    try:
                        mail = self.outlook.CreateItem(0)
                        # Try to set the send using account
                        for acc in self.namespace.Accounts:
                            if store_name in acc.DisplayName:
                                actual_email = acc.SmtpAddress
                                print(f"    ✓ Found via sending account: {actual_email}")
                                break
                    except:
                        pass
                
                # If still no email found, try to construct from store name
                if not actual_email:
                    # Check if store_name itself looks like an email
                    if '@' in store_name and '.' in store_name:
                        actual_email = store_name
                        print(f"    ℹ Using store name as email: {actual_email}")
                    else:
                        # For shared mailboxes, try to get from address lists
                        actual_email = self._search_gal_for_email(store_name)
                        if actual_email:
                            print(f"    ✓ Found via GAL search: {actual_email}")
                        else:
                            # Last resort: try to append domain
                            actual_email = f"{store_name}@asl.com.hk"
                            print(f"    ⚠ Could not determine email, using: {actual_email}")
                
                mailbox_info = {
                    'display_name': store_name,
                    'email': actual_email,
                    'type': 'shared',
                    'store_index': i
                }
                
                self.shared_mailboxes.append(mailbox_info)
                self.all_email_addresses.append(mailbox_info)
                processed_names.add(store_name)
                
                print(f"    Final email: {actual_email}")
                        
        except Exception as e:
            print(f"[ERROR] Discovering shared mailboxes: {e}")
            import traceback
            print(traceback.format_exc())
    
    def _search_gal_for_email(self, display_name):
        """Search Global Address List for the mailbox's email address."""
        try:
            gal = self.namespace.AddressLists.Item("Global Address List")
            if gal:
                # Search for exact match first
                for entry in gal.AddressEntries:
                    if entry.Name and entry.Name.lower() == display_name.lower():
                        if entry.Type == "SMTP":
                            return entry.Address
                        elif entry.Type == "EX":
                            try:
                                exchange_user = entry.GetExchangeUser()
                                if exchange_user and hasattr(exchange_user, 'PrimarySmtpAddress'):
                                    return exchange_user.PrimarySmtpAddress
                            except:
                                pass
                
                # Search for partial match
                for entry in gal.AddressEntries:
                    if entry.Name and display_name.lower() in entry.Name.lower():
                        if entry.Type == "SMTP":
                            return entry.Address
                        elif entry.Type == "EX":
                            try:
                                exchange_user = entry.GetExchangeUser()
                                if exchange_user and hasattr(exchange_user, 'PrimarySmtpAddress'):
                                    return exchange_user.PrimarySmtpAddress
                            except:
                                pass
            return None
        except:
            return None
    
    def _get_current_user_email(self):
        """Get current user's primary email address."""
        try:
            current_user = self.namespace.CurrentUser
            # Try to get from accounts first
            if self.personal_accounts:
                return self.personal_accounts[0]['email']
            
            # Try from AddressEntry
            if hasattr(current_user, 'AddressEntry'):
                address_entry = current_user.AddressEntry
                if address_entry.Type == "EX":
                    try:
                        exchange_user = address_entry.GetExchangeUser()
                        if exchange_user and hasattr(exchange_user, 'PrimarySmtpAddress'):
                            return exchange_user.PrimarySmtpAddress
                    except:
                        pass
                elif address_entry.Type == "SMTP":
                    return address_entry.Address
            
            return None
        except:
            return None
      
    def run_discovery(self):
        """Run the complete discovery process."""
        if not self.connect_outlook():
            return False
        
        self.discover_personal_accounts()
        self.discover_shared_mailboxes()
        
        return True

def main():
    """Main function to run the discovery tool."""
    try:
        print("="*60)
        print("OUTLOOK EMAIL DISCOVERY TOOL")
        print("Dynamic Discovery for Any PC")
        print("="*60)
        
        discoverer = OutlookAccountDiscovery()
        discoverer.run_discovery()
        
        print("\n" + "="*60)
        print("DISCOVERY COMPLETE")
        print("="*60)
        print("\nTips:")
        print("1. Check 'outlook_config.py' for auto-generated configuration")
        print("2. Use the discovered email addresses in your email sender")
        print("3. For shared mailboxes, use the display name exactly as shown")
        print("4. The actual email addresses of shared mailboxes are now extracted")
        
    except Exception as e:
        print(f"\n[FATAL ERROR] {e}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    main()



    # def get_all_email_summary(self):
    #     """Return summary of all discovered email addresses."""
    #     print("\n" + "="*60)
    #     print("COMPLETE SUMMARY OF ALL EMAIL ADDRESSES")
    #     print("="*60)
        
    #     print("\n[Personal Email Addresses]")
    #     if self.personal_accounts:
    #         for acc in self.personal_accounts:
    #             print(f"  • {acc['display_name']} - {acc['email']}")
    #     else:
    #         print("  • None found")
        
    #     print("\n[Shared Mailboxes]")
    #     if self.shared_mailboxes:
    #         for mailbox in self.shared_mailboxes:
    #             print(f"  • {mailbox['display_name']} - {mailbox['email']}")
    #     else:
    #         print("  • None found")
        
    #     print(f"\n[Total Email Sources Found: {len(self.all_email_addresses)}]")
    
    # def generate_config_recommendations(self):
    #     """Generate configuration recommendations based on discovered mailboxes."""
    #     print("\n" + "="*60)
    #     print("CONFIGURATION RECOMMENDATIONS")
    #     print("="*60)
        
    #     if self.personal_accounts:
    #         print("\n[Personal Account]")
    #         print(f"  SENDER_EMAIL = \"{self.personal_accounts[0]['email']}\"")
    #         print(f"  Or use for testing: {self.personal_accounts[0]['email']}")
        
    #     # Filter out personal account from shared mailboxes list
    #     real_shared_mailboxes = [mb for mb in self.shared_mailboxes 
    #                              if mb['display_name'] not in [acc['display_name'] for acc in self.personal_accounts]]
        
    #     if real_shared_mailboxes:
    #         print("\n[Shared Mailboxes Available]")
    #         for i, mailbox in enumerate(real_shared_mailboxes, 1):
    #             print(f"  {i}. Display Name: {mailbox['display_name']}")
    #             print(f"     Email: {mailbox['email']}")
    #             if i == 1:  # Suggest first shared mailbox as default
    #                 print(f"     (Suggested for SHARED_MAILBOX_DISPLAY)")
        
    #     print("\n[Example Configuration]")
    #     print("class Config:")
    #     print("    def __init__(self):")
    #     if real_shared_mailboxes:
    #         print(f"        self.SHARED_MAILBOX_DISPLAY = \"{real_shared_mailboxes[0]['display_name']}\"")
    #         print(f"        self.SENDER_EMAIL = \"{real_shared_mailboxes[0]['email']}\"")
    #     elif self.personal_accounts:
    #         print(f"        self.SHARED_MAILBOX_DISPLAY = \"{self.personal_accounts[0]['display_name']}\"")
    #         print(f"        self.SENDER_EMAIL = \"{self.personal_accounts[0]['email']}\"")
    #     else:
    #         print(f"        self.SHARED_MAILBOX_DISPLAY = \"ASL_HK_SOC_OPER\"  # Update as needed")
    #         print(f"        self.SENDER_EMAIL = \"soc_oper@asl.com.hk\"  # Update as needed")
    
    # def export_to_config_format(self, filename="outlook_config.py"):
    #     """Export discovered mailboxes to a config file."""
    #     try:
    #         with open(filename, 'w', encoding='utf-8') as f:
    #             f.write("# Auto-generated Outlook Configuration\n")
    #             f.write("# Generated by Outlook Account Discovery Tool\n\n")
                
    #             f.write("class AutoConfig:\n")
    #             f.write("    \"\"\"Auto-discovered Outlook configuration.\"\"\"\n")
    #             f.write("    def __init__(self):\n")
                
    #             # Personal accounts
    #             f.write("        # Personal Email Accounts\n")
    #             f.write("        self.PERSONAL_ACCOUNTS = [\n")
    #             for acc in self.personal_accounts:
    #                 f.write(f"            {{'display_name': '{acc['display_name']}', 'email': '{acc['email']}'}},\n")
    #             f.write("        ]\n\n")
                
    #             # Shared mailboxes (filter out personal)
    #             real_shared = [mb for mb in self.shared_mailboxes 
    #                           if mb['display_name'] not in [acc['display_name'] for acc in self.personal_accounts]]
                
    #             f.write("        # Shared Mailboxes\n")
    #             f.write("        self.SHARED_MAILBOXES = [\n")
    #             for mailbox in real_shared:
    #                 f.write(f"            {{'display_name': '{mailbox['display_name']}', 'email': '{mailbox['email']}'}},\n")
    #             f.write("        ]\n\n")
                
    #             # Default selections
    #             if self.personal_accounts:
    #                 f.write(f"        # Default personal account\n")
    #                 f.write(f"        self.DEFAULT_PERSONAL_EMAIL = '{self.personal_accounts[0]['email']}'\n")
                
    #             if real_shared:
    #                 f.write(f"        # Default shared mailbox\n")
    #                 f.write(f"        self.DEFAULT_SHARED_MAILBOX_DISPLAY = '{real_shared[0]['display_name']}'\n")
    #                 f.write(f"        self.DEFAULT_SHARED_EMAIL = '{real_shared[0]['email']}'\n")
    #             elif self.personal_accounts:
    #                 f.write(f"        # Default to personal account if no shared mailboxes\n")
    #                 f.write(f"        self.DEFAULT_SHARED_MAILBOX_DISPLAY = '{self.personal_accounts[0]['display_name']}'\n")
    #                 f.write(f"        self.DEFAULT_SHARED_EMAIL = '{self.personal_accounts[0]['email']}'\n")
                
    #         print(f"\n[EXPORT] Configuration exported to {filename}")
    #         return True
    #     except Exception as e:
    #         print(f"[ERROR] Exporting configuration: {e}")
    #         return False






