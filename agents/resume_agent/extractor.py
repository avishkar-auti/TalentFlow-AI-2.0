"""
Resume Text & AST Extractor using PyMuPDF (fitz) and Layout Analysis.
Extracts structural blocks, font metadata, headers, and bullet points to construct a Resume AST.
"""
import re
import logging
from typing import Dict, Any, List, Optional
import fitz  # PyMuPDF

logger = logging.getLogger(__name__)

class ResumeASTExtractor:
    """Extracts raw text and structural layout AST from PDF/DOCX resume files."""

    @staticmethod
    def extract_text_and_ast(file_bytes: bytes) -> Dict[str, Any]:
        """
        Parses PDF file bytes and builds a structured AST representation of the resume layout.
        """
        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
        except Exception as e:
            logger.error(f"Failed to open PDF document: {e}")
            raise ValueError(f"Could not parse file bytes as valid PDF: {e}")

        total_pages = len(doc)
        full_text = ""
        blocks_ast: List[Dict[str, Any]] = []
        fonts_used: set = set()
        tables_detected: int = 0
        images_detected: int = 0
        has_scanned_text: bool = False

        for page_num in range(total_pages):
            page = doc[page_num]
            text = page.get_text()
            full_text += f"\n--- Page {page_num + 1} ---\n" + text

            # Extract detailed layout structure (AST blocks)
            text_page = page.get_text("dict")
            images_detected += len(page.get_images())

            for b in text_page.get("blocks", []):
                if b.get("type") == 0:  # Text block
                    lines_text = []
                    block_font_sizes = []
                    
                    for line in b.get("lines", []):
                        line_str = ""
                        for span in line.get("spans", []):
                            line_str += span.get("text", "")
                            font_name = span.get("font", "")
                            font_size = span.get("size", 10)
                            fonts_used.add(font_name)
                            block_font_sizes.append(font_size)
                        lines_text.append(line_str)

                    avg_font_size = sum(block_font_sizes) / max(len(block_font_sizes), 1)
                    block_content = "\n".join(lines_text).strip()
                    
                    if block_content:
                        # Identify heading vs body based on font size and formatting
                        is_heading = avg_font_size > 12.0 or bool(re.match(r'^(EXPERIENCE|EDUCATION|SKILLS|PROJECTS|WORK HISTORY|SUMMARY|CERTIFICATIONS|PUBLICATIONS)\b', block_content, re.I))
                        
                        blocks_ast.append({
                            "page": page_num + 1,
                            "type": "heading" if is_heading else "paragraph",
                            "avg_font_size": round(avg_font_size, 1),
                            "bbox": b.get("bbox"),
                            "content": block_content
                        })

        doc.close()

        # Check if text is extremely short (suggesting scanned image PDF)
        clean_text = full_text.strip()
        if len(clean_text) < 100 and images_detected > 0:
            has_scanned_text = True
            logger.warning("Resume PDF appears to be a scanned image with minimal selectable text.")

        return {
            "raw_text": clean_text,
            "total_pages": total_pages,
            "blocks_ast": blocks_ast,
            "fonts_used": list(fonts_used),
            "tables_detected": tables_detected,
            "images_detected": images_detected,
            "has_scanned_text": has_scanned_text
        }
