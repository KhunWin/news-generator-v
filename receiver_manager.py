import os


class ReceiverManager:
    """Reads receiver email addresses from txt files (one group per file)."""
    def __init__(self, directory: str):
        try:
            print(f"[ReceiverManager] Init directory: {directory}")
            self.directory = directory
            os.makedirs(self.directory, exist_ok=True)
        except Exception as e:
            print(f"[ReceiverManager][ERROR in __init__] {e}")
      
    def load_group(self, group_name: str):
        """group_name='receiver_1' -> reads receiver_1.txt"""
        try:
            path = os.path.join(self.directory, f"{group_name}.txt")
            print(f"[ReceiverManager] Loading {path}")
            if not os.path.exists(path):
                print(f"[ReceiverManager][WARN] Missing file: {path}")
                return []

            with open(path, "r", encoding="utf-8") as f:
                raw = f.read()

            emails = []
            for chunk in raw.replace("\n", ",").split(","):
                e = chunk.strip().lower()  # Normalize to lowercase
                if e and '@' in e:  # Basic email validation
                    if e not in emails:  # Remove duplicates
                        emails.append(e)
            
            print(f"[ReceiverManager] {group_name}: loaded {len(emails)} unique emails")
            return emails
        except Exception as e:
            print(f"[ReceiverManager][ERROR in load_group] {e}")
            return []
        

        