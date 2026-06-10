# csv_logger.py
import os
import csv
from datetime import datetime
from pathlib import Path
import time
import re
from html.parser import HTMLParser
from html import unescape


class HTMLTextExtractor(HTMLParser):
    """Extract plain text from HTML content, removing all tags and CSS."""
    
    def __init__(self):
        super().__init__()
        self.text_parts = []
        self.in_style = False
        self.in_script = False
    
    def handle_starttag(self, tag, attrs):
        """Handle opening tags."""
        if tag == 'style':
            self.in_style = True
        elif tag == 'script':
            self.in_script = True
        elif tag in ('br',):
            # Treat <br> as a space to avoid joining words
            self.text_parts.append(' ')
        elif tag in ('p', 'div', 'li'):
            # Add line break for block elements
            if self.text_parts and self.text_parts[-1] != '\n':
                self.text_parts.append('\n')
    
    def handle_endtag(self, tag):
        """Handle closing tags."""
        if tag == 'style':
            self.in_style = False
        elif tag == 'script':
            self.in_script = False
        elif tag in ('p', 'div', 'li'):
            # Add line break after block elements
            if self.text_parts and self.text_parts[-1] != '\n':
                self.text_parts.append('\n')
    
    def handle_data(self, data):
        """Collect text data from HTML, skip style and script content."""
        if self.in_style or self.in_script:
            return
        
        text = data.strip()
        if text:
            self.text_parts.append(text)
    
    def get_text(self):
        """Get extracted text with cleaned formatting."""
        # Join all parts
        result = ''.join(self.text_parts)
        
        # Normalize whitespace: replace multiple spaces with single space
        result = re.sub(r'[ \t]+', ' ', result)
        
        # Normalize line breaks: replace multiple newlines with single newline
        result = re.sub(r'\n\s*\n+', '\n', result)
        
        # Remove spaces around newlines
        result = re.sub(r' *\n *', '\n', result)
        
        return result.strip()


class EmailRecordLogger:
    """Logs email generation records to monthly CSV files."""
    
    def __init__(self, receivers_dir: str):
        """
        Initialize the logger.
        
        Args:
            receivers_dir: Directory containing receiver .txt files
        """
        self.receivers_dir = receivers_dir
        self.current_dir = os.getcwd()
    
    def _strip_html(self, html_content: str) -> str:
        """
        Strip ALL HTML tags, CSS, and extract only plain text.
        
        Args:
            html_content: HTML string to process
            
        Returns:
            Plain text with URLs separated by space (not line breaks for Excel compatibility)
        """
        if not html_content:
            return ''
        
        try:
            # Quick check if content contains HTML
            if not re.search(r'<[^>]+>', html_content):
                return html_content.strip()
            
            # Remove DOCTYPE declarations
            html_content = re.sub(r'<!DOCTYPE[^>]*>', '', html_content, flags=re.IGNORECASE)
            
            # Remove all <style> blocks entirely (including content)
            html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.IGNORECASE | re.DOTALL)
            
            # Remove all <script> blocks entirely (including content)
            html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.IGNORECASE | re.DOTALL)
            
            # Remove HTML comments
            html_content = re.sub(r'<!--.*?-->', '', html_content, flags=re.DOTALL)
            
            # Use parser to extract text
            parser = HTMLTextExtractor()
            parser.feed(html_content)
            text = parser.get_text()
            
            # HTML entity decode (e.g., &nbsp; -> space, &amp; -> &)
            text = unescape(text)
            
            # Excel has issues with newlines in CSV cells, so replace newlines with space
            # This keeps all URLs in one cell visible in Excel
            text = text.replace('\n', ' ')
            
            # Clean up multiple spaces
            text = re.sub(r' +', ' ', text)
            
            return text.strip()
            
        except Exception as e:
            print(f"[EmailRecordLogger][WARN] Error parsing HTML: {e}")
            # Fallback: aggressive regex strip
            text = html_content
            
            # Remove style blocks
            text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.IGNORECASE | re.DOTALL)
            
            # Remove script blocks  
            text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
            
            # Remove all HTML tags
            text = re.sub(r'<[^>]+>', ' ', text)
            
            # Decode HTML entities
            text = unescape(text)
            
            # Replace newlines with space for Excel compatibility
            text = text.replace('\n', ' ').replace('\r', ' ')
            
            # Clean up whitespace
            text = re.sub(r'\s+', ' ', text)
            
            return text.strip()
        
    def _get_month_year_filename(self) -> str:
        """Generate filename based on current month and year (e.g., 'May_26.csv')."""
        now = datetime.now()
        month_name = now.strftime("%B")  # Full month name (e.g., "May")
        year_short = now.strftime("%y")  # Two-digit year (e.g., "26")
        return f"{month_name}_{year_short}.csv"
    
    def _get_current_date_formatted(self) -> str:
        """Get current date in dd-mmm-yy format (e.g., '28-May-26')."""
        return datetime.now().strftime("%d-%b-%y")
    
    def _get_receiver_names(self) -> list:
        """Get all receiver names from .txt files in receivers directory."""
        try:
            if not os.path.exists(self.receivers_dir):
                print(f"[EmailRecordLogger][WARN] Receivers directory not found: {self.receivers_dir}")
                return []
            
            txt_files = [f.replace('.txt', '') for f in os.listdir(self.receivers_dir) 
                        if f.endswith('.txt')]
            txt_files.sort()  # Sort alphabetically for consistent column order
            return txt_files
        except Exception as e:
            print(f"[EmailRecordLogger][ERROR in _get_receiver_names] {e}")
            return []
    
    def _get_csv_headers(self) -> list:
        """Generate CSV headers including dynamic receiver columns."""
        base_headers = [
            "Date",
            "Title",
            "Reference",
            "Affected Systems",
            "Impacted Industry",
            "News Severity"
        ]
        receiver_names = self._get_receiver_names()
        return base_headers + receiver_names
    
    def _file_exists_and_valid(self, filepath: str) -> bool:
        """Check if CSV file exists and has valid headers."""
        if not os.path.exists(filepath):
            return False
        
        try:
            with open(filepath, 'r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                existing_headers = next(reader, None)
                expected_headers = self._get_csv_headers()
                
                if existing_headers != expected_headers:
                    print(f"[EmailRecordLogger][WARN] CSV headers mismatch.")
                    print(f"  Expected: {expected_headers}")
                    print(f"  Found: {existing_headers}")
                    return False
                return True
        except Exception as e:
            print(f"[EmailRecordLogger][ERROR checking file validity] {e}")
            return False
    
    def _create_new_csv(self, filepath: str):
        """Create a new CSV file with headers."""
        try:
            headers = self._get_csv_headers()
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
            print(f"[EmailRecordLogger] Created new CSV: {filepath}")
        except Exception as e:
            print(f"[EmailRecordLogger][ERROR creating CSV] {e}")
            raise
    
    def _write_with_retry(self, filepath: str, row: list, max_retries: int = 3) -> bool:
        """
        Attempt to write to CSV with retry logic to handle file locking issues.
        
        Args:
            filepath: Path to CSV file
            row: Data row to append
            max_retries: Maximum number of retry attempts
            
        Returns:
            bool: True if write successful, False otherwise
        """
        for attempt in range(max_retries):
            try:
                with open(filepath, 'a', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(row)
                    f.flush()
                    os.fsync(f.fileno())
                return True
            except PermissionError as e:
                if attempt < max_retries - 1:
                    print(f"[EmailRecordLogger][WARN] File locked, retry {attempt + 1}/{max_retries}...")
                    time.sleep(0.5)
                else:
                    print(f"[EmailRecordLogger][ERROR] File remains locked after {max_retries} attempts")
                    print(f"  Please close {os.path.basename(filepath)} if it's open in Excel or another program")
                    raise
            except Exception as e:
                print(f"[EmailRecordLogger][ERROR writing to CSV] {e}")
                raise
        return False
    
    def log_record(self, form_data: dict) -> bool:
        try:
            filename = self._get_month_year_filename()
            filepath = os.path.join(self.current_dir, filename)
            
            print(f"[EmailRecordLogger] Attempting to log to: {filepath}")
            
            if not self._file_exists_and_valid(filepath):
                print(f"[EmailRecordLogger] Creating new CSV file...")
                self._create_new_csv(filepath)
            
            # Prepare row data
            current_date = self._get_current_date_formatted()
            title = form_data.get('title', '')
            
            # Strip HTML completely from reference field
            reference_raw = form_data.get('reference', '')
            reference = self._strip_html(reference_raw)
            
            severity = form_data.get('severity', '')
            
            # Join list fields with semicolons
            systems = '; '.join(form_data.get('systems', []))
            industries = '; '.join(form_data.get('industries', []))
            
            # Build row
            row = [current_date, title, reference, systems, industries, severity]
            
            # Add receiver selections (Y/N)
            receiver_names = self._get_receiver_names()
            selected_receivers = form_data.get('selected_receivers', {})
            
            for receiver_name in receiver_names:
                is_selected = selected_receivers.get(receiver_name, False)
                row.append('Y' if is_selected else 'N')
            
            # Append to CSV with retry logic
            success = self._write_with_retry(filepath, row)
            
            if success:
                print(f"[EmailRecordLogger] Record logged successfully to {filename}")
            
            return success
            
        except Exception as e:
            print(f"[EmailRecordLogger][ERROR in log_record] {e}")
            return False
        

    def update_last_row_receivers(self, selected_receivers: dict, update_all_columns: bool = False, form_data: dict = None) -> bool:
        """
        Update the receiver columns of the last row in the current month's CSV.
        
        Args:
            selected_receivers: Dictionary of receiver selections {receiver_name: bool}
            update_all_columns: If True, update all columns; if False, only update receivers
            form_data: Full form data (required if update_all_columns is True)
            
        Returns:
            bool: True if update successful, False otherwise
        """
        try:
            filename = self._get_month_year_filename()
            filepath = os.path.join(self.current_dir, filename)
            
            if not os.path.exists(filepath):
                print(f"[EmailRecordLogger][ERROR] CSV file not found: {filepath}")
                return False
            
            # Read all rows
            with open(filepath, 'r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                rows = list(reader)
            
            if len(rows) < 2:  # Only header, no data rows
                print(f"[EmailRecordLogger][ERROR] No data rows to update")
                return False
            
            headers = rows[0]
            last_row = rows[-1]
            
            # Get receiver column indices
            receiver_names = self._get_receiver_names()
            base_columns_count = 6  # Date, Title, Reference, Affected Systems, Impacted Industry, News Severity
            
            if update_all_columns and form_data:
                # Update all columns including form fields
                current_date = self._get_current_date_formatted()
                title = form_data.get('title', '')
                
                # Strip HTML from reference
                reference_raw = form_data.get('reference', '')
                reference = self._strip_html(reference_raw)
                
                severity = form_data.get('severity', '')
                systems = '; '.join(form_data.get('systems', []))
                industries = '; '.join(form_data.get('industries', []))
                
                # Update base columns
                last_row[0] = current_date
                last_row[1] = title
                last_row[2] = reference
                last_row[3] = systems
                last_row[4] = industries
                last_row[5] = severity
                
                # When updating all columns, set receivers normally (Y/N for all)
                for i, receiver_name in enumerate(receiver_names):
                    col_index = base_columns_count + i
                    if col_index < len(last_row):
                        is_selected = selected_receivers.get(receiver_name, False)
                        last_row[col_index] = 'Y' if is_selected else 'N'
            else:
                # Only update receiver columns for SELECTED receivers
                # Leave unselected receivers unchanged
                for i, receiver_name in enumerate(receiver_names):
                    col_index = base_columns_count + i
                    if col_index < len(last_row):
                        is_selected = selected_receivers.get(receiver_name, False)
                        # Only update if this receiver is selected (checked in the UI)
                        if is_selected:
                            last_row[col_index] = 'Y'
                        # If not selected, leave the existing value unchanged
            
            # Write back to file with retry
            for attempt in range(3):
                try:
                    with open(filepath, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerows(rows)
                        f.flush()
                        os.fsync(f.fileno())
                    
                    print(f"[EmailRecordLogger] Last row updated successfully in {filename}")
                    return True
                    
                except PermissionError:
                    if attempt < 2:
                        print(f"[EmailRecordLogger][WARN] File locked, retry {attempt + 1}/3...")
                        time.sleep(0.5)
                    else:
                        print(f"[EmailRecordLogger][ERROR] File remains locked after 3 attempts")
                        print(f"  Please close {os.path.basename(filepath)} if it's open in Excel")
                        return False
                except Exception as e:
                    print(f"[EmailRecordLogger][ERROR updating CSV] {e}")
                    return False
            
            return False
            
        except Exception as e:
            print(f"[EmailRecordLogger][ERROR in update_last_row_receivers] {e}")
            return False



