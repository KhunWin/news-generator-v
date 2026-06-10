import html as html_lib
import re, os, sys
from pathlib import Path
from bs4 import BeautifulSoup


class EmailFormatter:
    """Builds the HTML body preserving rich text formatting from editors."""

    def __init__(self, signature_file: str = "default_signature.html"):
        try:
            print("[EmailFormatter] Initialized")
            # self._base_path = self._get_base_path()

            self.default_signature_file = "default_signature.html"
            self.fdct_signature_file = "fdct_signature.html"
            # self.default_signature_path = self._base_path / "assets" / "default_signature.html"
            # self.fdct_signature_path = self._base_path / "assets" / "fdct_signature.html"
            self._default_signature_html = self._load_signature_from_file(self.default_signature_file)
            self._fdct_signature_html = self._load_signature_from_file(self.fdct_signature_file)
        except Exception as e:
            print(f"[EmailFormatter][ERROR in __init__] {e}")
            


    def _extract_body_content(self, html_string: str) -> str:
        """
        Extracts content from QTextEdit HTML, removing Qt-specific wrapper tags
        while preserving all formatting.
        """
        try:
            if not html_string or not html_string.strip():
                return ""
            
            soup = BeautifulSoup(html_string, 'html.parser')
            
            # Remove style and meta tags
            for tag in soup(['style', 'meta']):
                tag.decompose()
            
            # Try to find body content
            body = soup.find('body')
            if body:
                content = str(body)
                # Remove body tags but keep content
                content = re.sub(r'^<body[^>]*>', '', content)
                content = re.sub(r'</body>$', '', content)
                return content.strip()
            
            # If no body tag, return cleaned content
            return str(soup).strip()
            
        except Exception as e:
            print(f"[EmailFormatter][ERROR in _extract_body_content] {e}")
            return html_string

    def _format_text(self, html_content: str) -> str:
        """
        Processes HTML content from rich text editors.
        Preserves existing HTML formatting and cleans up Qt-specific tags.
        """
        try:
            if not html_content:
                return ""

            # Extract body content, removing Qt wrapper
            cleaned = self._extract_body_content(html_content)
            
            if not cleaned:
                return ""
            
             # SANITIZE CONTENT BEFORE PROCESSING ↓↓↓
            cleaned = self._sanitize_security_content(cleaned)
            
            # Clean up Qt-specific inline styles that might cause issues
            soup = BeautifulSoup(cleaned, 'html.parser')
            
            # Remove margin-top and margin-bottom from paragraphs for consistency
            for p in soup.find_all('p'):
                if p.get('style'):
                    style = p['style']
                    # Remove Qt's default margins
                    style = re.sub(r'margin-top:\s*\d+px;?', '', style)
                    style = re.sub(r'margin-bottom:\s*\d+px;?', '', style)
                    if style.strip():
                        p['style'] = style
                    else:
                        del p['style']

            # Remove any font-size and font-family from all elements to prevent override
            for tag in soup.find_all(True):
                if tag.get('style'):
                    style = tag['style']
                    # Remove font-size declarations
                    style = re.sub(r'font-size:\s*[^;]+;?', '', style)
                    # Remove font-family declarations
                    style = re.sub(r'font-family:\s*[^;]+;?', '', style)
                    # Clean up any remaining semicolons
                    style = re.sub(r';+', ';', style)
                    style = re.sub(r'^\s*;\s*', '', style)
                    style = re.sub(r';\s*$', '', style)
                    if style.strip():
                        tag['style'] = style
                    else:
                        del tag['style']
            
            return str(soup)
            # Wrap content in a div with consistent font styling
            # result = str(soup)
            # return f'<div style="font-family: Calibri, Arial, sans-serif; font-size: 12pt;">{result}</div>'
            
        except Exception as e:
            print(f"[EmailFormatter][ERROR in _format_text] {e}")
            return html_content or ""

 
    def build_html(self, data, cid1=None, cid2=None, sender_email=None):
        try:
            print("[EmailFormatter] Building HTML body...")

            severity_colors = {
                "Low": "#f1c40f",      # Yellow
                "Medium": "#e67e22",   # Orange
                "High": "#FF8585",     # Light red
                "Critical": "#f60000", # Pure bright red
            }
            color = severity_colors.get(data.get("severity", ""), "#333")

            img1_html = (
                f'<div style="margin:10px 0;">'
                f'<img src="cid:{cid1}" style="max-width:600px; border:1px solid #ddd;" />'
                f'</div>' if cid1 else ""
            )
            img2_html = (
                f'<div style="margin:10px 0;">'
                f'<img src="cid:{cid2}" style="max-width:600px; border:1px solid #ddd;" />'
                f'</div>' if cid2 else ""
            )

            # Process reference through _format_text to maintain consistent formatting
            ref_raw = data.get("reference", "")
            ref_html = ""

            if ref_raw:
                # Extract just the text content from the HTML
                ref_soup = BeautifulSoup(ref_raw, 'html.parser')
                # Get all text content and split into lines
                ref_text = ref_soup.get_text()
                
                # Split by newlines and filter out empty lines
                links = [line.strip() for line in ref_text.split('\n') if line.strip()]
                
                # Create formatted HTML with each link on a new line
                if links:
                    link_elements = []
                    for link in links:
                        # SANITIZE URLs IN REFERENCES ↓↓↓
                        sanitized_link = self._sanitize_security_content(link)

                        # Check if it looks like a URL
                        if link.startswith(('http://', 'https://')):
                            # link_elements.append(f'<div><a href="{html_lib.escape(link)}">{html_lib.escape(link)}</a></div>')
                            link_elements.append(f'<div><a href="{html_lib.escape(link)}">{html_lib.escape(sanitized_link)}</a></div>')

                        else:
                            # link_elements.append(f'<div>{html_lib.escape(link)}</div>')
                            link_elements.append(f'<div>{html_lib.escape(sanitized_link)}</div>')

                    
                    ref_html = f'<div style="margin-top:5px;">{"".join(link_elements)}</div>'

            # title_safe = html_lib.escape(data.get("title", ""))
            title_safe = self._sanitize_security_content(html_lib.escape(data.get("title", "")))

            severity_safe = html_lib.escape(data.get("severity", ""))
            industries_safe = html_lib.escape(", ".join(data.get("industries", [])) or "-")
            threats_safe = html_lib.escape(", ".join(data.get("threats", [])) or "-")
            systems_safe = html_lib.escape(", ".join(data.get("systems", [])) or "-")

            # Process rich text content - preserves HTML formatting
            
            # summary_html = self._sanitize_security_content(self._format_text(data.get("summary", "")))
            # content_html = self._sanitize_security_content(self._format_text(data.get("content", "")))
            # content2_html = self._sanitize_security_content(self._format_text(data.get("content2", "")))
            summary_html = self._format_text(data.get("summary", ""))
            content_html = self._format_text(data.get("content", ""))
            content2_html = self._format_text(data.get("content2", ""))
            recommendation_html = self._format_text(data.get("recommendation", ""))

            content2_block = (
                f"<div style='margin-top:10px;'>{content2_html}</div>"
                if content2_html.strip() else ""
            )
            # recommendation_block = (
            #     f"<h4>Recommendation:</h4><div>{recommendation_html}</div>"
            #     if recommendation_html.strip() else ""
            # )
            # Check recommendation mode
            recommendation_mode = data.get("recommendation_mode", "recommendation")
            recommendation_block = f"<div>{recommendation_html}</div>"
            if recommendation_mode == "recommendation" and recommendation_html.strip():
                recommendation_block = f"<h4>Recommendation:</h4><div>{recommendation_html}</div>"

            # Select signature based on sender email
            use_fdct = sender_email and sender_email.lower() == "cyberupdate@soc2.ctm.net"
            signature_html = self._fdct_signature_html if use_fdct else self._default_signature_html

            html = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; color: #222; }}
                    table {{ border-collapse: collapse; margin: 5px 0;  font-family: Calibri, Arial, sans-serif; 
                        font-size: 12pt;}}
                    h2{{ margin-top: 15px; margin-bottom: 8px;  font-family: Calibri, Arial, sans-serif;font-size: 24pt;}}
                    h3, h4 {{ margin-top: 15px; margin-bottom: 8px;  font-family: Calibri, Arial, sans-serif; 
                        font-size: 12pt;}}
                    p {{ margin: 5px 0; }}
                    ul {{ margin: 6px 0 6px 20px; padding: 0; }}
                    li {{ margin: 3px 0; }}
                    /* Preserve formatting from pasted content */
                    strong, b {{ font-weight: bold; }}
                    em, i {{ font-style: italic; }}
                    table.formatted {{ border: 1px solid #ddd; }}
                    table.formatted td, table.formatted th {{ 
                        border: 1px solid #ddd; 
                        padding: 8px;
                        font-family: Calibri, Arial, sans-serif; 
                        font-size: 12pt;
                    
                    }}
                </style>
            </head>
            <body>
                <div style="font-family: Calibri, Arial, sans-serif; font-size: 12pt;">
                    <p style="font-size:12pt; color:#222;">Dear all,</p>
                    <p style="font-size:12pt; color:#222;">Here is the latest security news, and for your reference.</p> <br>
                <h2><span style="text-decoration: underline;">{title_safe}</span></h2>
                <table style="border-collapse:collapse;">
                    <tr>
                    <td style="background-color:{color}; color:black"><b>Severity:</b></td>
                    <td style="background-color:{color}; color:black"><b>{severity_safe}</b></td>
                    </tr>
                    <tr><td><b>Impacted Industry:</b></td><td>{industries_safe}</td></tr>
                    <tr><td><b>Threat Intention/Reason:</b></td><td>{threats_safe}</td></tr>
                    <tr><td><b>Affected Systems:</b></td><td>{systems_safe}</td></tr>
                </table>
                <br>
                <br>
                <h4>Summary:</h4>
                <div>{summary_html}</div>
                
                {img1_html}
                <div>{content_html}</div>

                {img2_html}
                {content2_block}
                <br>
                <br>
                {recommendation_block}
                <br>
                <br>
                <div><b>Reference:</b></div>
                {ref_html}
                </div>

                <hr style="margin-top:20px;">
                {signature_html}

            </body>
            </html>
            """
            return html
        except Exception as e:
            print(f"[EmailFormatter][ERROR in build_html] {e}")
            return ""

  
    def _load_signature_from_file(self, file_path) -> str:
        """Load signature from HTML file."""
        try:
            # Convert to Path if it's a string
            if isinstance(file_path, str):
                file_path = Path(file_path)
            
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    signature = f.read()
                print(f"[EmailFormatter] Signature loaded from {file_path}")
                return signature
            else:
                print(f"[EmailFormatter] Warning: Signature file '{file_path}' not found, using default")
                return self._get_default_signature()
        except Exception as e:
            print(f"[EmailFormatter][ERROR loading signature from {file_path}] {e}")
            return self._get_default_signature()

    def _get_default_signature(self) -> str:
        """Return default signature as fallback."""
        return """
        <p style="font-size:12px; color:#777;">
          Best Regards, <br>
          Security Team <br>
          <hr>
        </p>
        """

    def _sanitize_security_content(self, content):

        try:
            if not content:
                return content
            
            # Defang @ symbol (e.g., user@domain.com → user[@]domain.com)
            content = re.sub(
                r'@',
                '[@]',
                content
            )
                       
            print("[EmailFormatter] Content sanitized for security")
            return content
            
        except Exception as e:
            print(f"[EmailFormatter][ERROR in _sanitize_security_content] {e}")
            return content

    # def _load_signature_from_file(self, filename: str) -> str:
    #     """Load signature from HTML file."""
    #     try:
    #         if Path(filename).exists():
    #             with open(filename, 'r', encoding='utf-8') as f:
    #                 signature = f.read()
    #             print(f"[EmailFormatter] Signature loaded from {filename}")
    #             return signature
    #         else:
    #             print(f"[EmailFormatter] Warning: Signature file '{filename}' not found, using default")
    #             return self._get_default_signature()
    #     except Exception as e:
    #         print(f"[EmailFormatter][ERROR loading signature from {filename}] {e}")
    #         return self._get_default_signature()
  

    # def _get_base_path(self) -> Path:
    #     """Get the base path for resources (works with PyInstaller)"""
    #     if getattr(sys, 'frozen', False):
    #         # Running as compiled EXE
    #         base_path = Path(sys._MEIPASS)
    #         print(f"[EmailFormatter] Running as EXE, using MEIPASS: {base_path}")
    #         return base_path
    #     else:
    #         # Running as script - get the directory containing this file
    #         base_path = Path(os.path.dirname(os.path.abspath(__file__)))
    #         print(f"[EmailFormatter] Running as script, using script directory: {base_path}")
    #         return base_path


    # def build_html(self, data, cid1=None, cid2=None, sender_email=None):
    #     try:
    #         print("[EmailFormatter] Building HTML body...")

    #         severity_colors = {
    #             "Low": "#f1c40f",      # Yellow
    #             "Medium": "#e67e22",   # Orange
    #             "High": "#FF8585",     # Light red
    #             "Critical": "#f60000", # Pure bright red
    #         }
    #         color = severity_colors.get(data.get("severity", ""), "#333")

    #         img1_html = (
    #             f'<div style="margin:10px 0;">'
    #             f'<img src="cid:{cid1}" style="max-width:600px; border:1px solid #ddd;" />'
    #             f'</div>' if cid1 else ""
    #         )
    #         img2_html = (
    #             f'<div style="margin:10px 0;">'
    #             f'<img src="cid:{cid2}" style="max-width:600px; border:1px solid #ddd;" />'
    #             f'</div>' if cid2 else ""
    #         )

    #         # Process reference through _format_text to maintain consistent formatting
    #         ref_raw = data.get("reference", "")
    #         ref_html = ""

    #         if ref_raw:
    #             # Extract just the text content from the HTML
    #             ref_soup = BeautifulSoup(ref_raw, 'html.parser')
    #             # Get all text content and split into lines
    #             ref_text = ref_soup.get_text()
                
    #             # Split by newlines and filter out empty lines
    #             links = [line.strip() for line in ref_text.split('\n') if line.strip()]
                
    #             # Create formatted HTML with each link on a new line
    #             if links:
    #                 link_elements = []
    #                 for link in links:
    #                     # Check if it looks like a URL
    #                     if link.startswith(('http://', 'https://')):
    #                         link_elements.append(f'<div><a href="{html_lib.escape(link)}">{html_lib.escape(link)}</a></div>')
    #                     else:
    #                         link_elements.append(f'<div>{html_lib.escape(link)}</div>')
                    
    #                 ref_html = f'<div style="margin-top:5px;">{"".join(link_elements)}</div>'

    #         title_safe = html_lib.escape(data.get("title", ""))
    #         severity_safe = html_lib.escape(data.get("severity", ""))
    #         industries_safe = html_lib.escape(", ".join(data.get("industries", [])) or "-")
    #         threats_safe = html_lib.escape(", ".join(data.get("threats", [])) or "-")
    #         systems_safe = html_lib.escape(", ".join(data.get("systems", [])) or "-")

    #         # Process rich text content - preserves HTML formatting
    #         summary_html = self._format_text(data.get("summary", ""))
    #         content_html = self._format_text(data.get("content", ""))
    #         content2_html = self._format_text(data.get("content2", ""))
    #         recommendation_html = self._format_text(data.get("recommendation", ""))
    #         # ref_html = self._format_text(data.get("reference", ""))

    #         content2_block = (
    #             f"<div style='margin-top:10px;'>{content2_html}</div>"
    #             if content2_html.strip() else ""
    #         )
    #         recommendation_block = (
    #             f"<h4>Recommendation:</h4><div>{recommendation_html}</div>"
    #             if recommendation_html.strip() else ""
    #         )
    #         # td {{ padding: 5px 5px; }}

    #           # Select signature based on is_fdct flag
    #         # signature_html = self._fdct_signature_html if is_fdct else self._default_signature_html
    #         use_fdct = sender_email and sender_email.lower() == "cyberupdate@soc2.ctm.net"
    #         signature_html = self._fdct_signature_html if use_fdct else self._default_signature_html

    #         html = f"""
    #         <html>
    #         <head>
    #             <style>
    #                 body {{ font-family: Arial, sans-serif; color: #222; }}
    #                 table {{ border-collapse: collapse; margin: 5px 0; }}
                    
    #                 h2, h3, h4 {{ margin-top: 15px; margin-bottom: 8px;}}
    #                 p {{ margin: 5px 0; }}
    #                 ul {{ margin: 6px 0 6px 20px; padding: 0; }}
    #                 li {{ margin: 3px 0; }}
    #                 /* Preserve formatting from pasted content */
    #                 strong, b {{ font-weight: bold; }}
    #                 em, i {{ font-style: italic; }}
    #                 table.formatted {{ border: 1px solid #ddd; }}
    #                 table.formatted td, table.formatted th {{ 
    #                     border: 1px solid #ddd; 
    #                     padding: 8px;
    #                     font-family: Calibri, Arial, sans-serif; 
    #                     font-size: 12pt;
                      
    #                 }}
    #             </style>
    #         </head>
    #         <body>
    #             <p style="font-size:14px; color:#222;">Dear all,</p>
    #             <p style="font-size:14px; color:#222;">Here is the latest security news, and for your reference.</p> <br>
    #           <h2><span style="text-decoration: underline;">{title_safe}</span></h2>
    #           <table style="border-collapse:collapse;">
    #             <tr>
    #               <td style="background-color:{color}; color:black"><b>Severity:</b></td>
    #               <td style="background-color:{color}; color:black"><b>{severity_safe}</b></td>
    #             </tr>
    #             <tr><td><b>Impacted Industry:</b></td><td>{industries_safe}</td></tr>
    #             <tr><td><b>Threat Intention/Reason:</b></td><td>{threats_safe}</td></tr>
    #             <tr><td><b>Affected Systems:</b></td><td>{systems_safe}</td></tr>
    #           </table>

    #           <h4>Summary:</h4>
    #           <div>{summary_html}</div>
              
    #           {img1_html}
    #           <div>{content_html}</div>

    #           {img2_html}
    #           {content2_block}
    #           {recommendation_block}
    #           <div><b>Reference:</b></div>
    #           {ref_html}

    #           <hr style="margin-top:20px;">
    #             {signature_html}

    #         </body>
    #         </html>
    #         """
    #         return html
    #     except Exception as e:
    #         print(f"[EmailFormatter][ERROR in build_html] {e}")
    #         return ""
   


