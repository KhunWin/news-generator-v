import poplib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.parser import Parser

# Email configuration
POP_SERVER = "pop3.macau.ctm.net"
POP_PORT = 995
SMTP_SERVER = "smtpauth.macau.ctm.net"
SMTP_PORT = 587
SENDER_EMAIL = "cyberupdate@soc2.ctm.net"
SENDER_PASSWORD = "yZgfgFwUwV?#tW7"  # Replace with actual password

def send_email(subject, body, recipient):
    """Send an email using SMTP"""
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = recipient
        msg['Subject'] = subject
        
        # Attach body
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Upgrade to secure connection if supported
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        
        print(f"Email sent successfully to {recipient}")
        return True
    
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

def receive_emails():
    """Receive emails using POP3"""
    try:
        # Connect to POP3 server
        server = poplib.POP3(POP_SERVER, POP_PORT)
        server.user(SENDER_EMAIL)
        server.pass_(SENDER_PASSWORD)
        
        print(f"Connected to POP3 server. Mailbox has {len(server.list()[1])} messages")
        
        # Get list of emails
        messages = server.list()[1]
        
        for i, msg_info in enumerate(messages, 1):
            print(f"\n--- Message {i} ---")
            # Get raw email
            raw_email = b'\n'.join(server.retr(i)[1])
            
            # Parse email
            email_message = Parser().parsestr(raw_email.decode('utf-8', errors='ignore'))
            
            print(f"From: {email_message['From']}")
            print(f"Subject: {email_message['Subject']}")
            
            # Get body (simplified)
            if email_message.is_multipart():
                for part in email_message.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        print(f"Body preview: {body[:100]}...")
                        break
            else:
                body = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
                print(f"Body preview: {body[:100]}...")
        
        server.quit()
        return True
    
    except Exception as e:
        print(f"Failed to receive emails: {e}")
        return False

# Example usage
if __name__ == "__main__":
    # Send a dummy email
    dummy_subject = "Test Email from Python"
    dummy_body = """Dear User,

This is a test email sent from Python using SMTP.

Best regards,
Automated Script"""
    
    recipient = "winwin@asl.com.hk"  # Replace with actual recipient
    
    print("Sending email...")
    send_email(dummy_subject, dummy_body, recipient)
    
    print("\n" + "="*50)
    
    # Receive emails (POP3)
    print("Receiving emails...")
    receive_emails()