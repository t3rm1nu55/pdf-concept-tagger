#!/usr/bin/env python3
"""
Create Test PDF

Creates a simple test PDF for MVP testing.
"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import sys
from pathlib import Path

def create_test_pdf(output_path: str = "test.pdf"):
    """Create a simple test PDF with sample text."""
    try:
        c = canvas.Canvas(output_path, pagesize=letter)
        width, height = letter
        
        # Page 1
        c.drawString(100, height - 100, "Test Document for PDF Concept Tagger")
        c.drawString(100, height - 130, "This document contains test concepts:")
        c.drawString(100, height - 160, "GDPR - General Data Protection Regulation")
        c.drawString(100, height - 190, "Completion Date: 2024-06-30")
        c.drawString(100, height - 220, "Data Protection Requirements")
        c.drawString(100, height - 250, "Legal Framework Compliance")
        c.showPage()
        
        # Page 2
        c.drawString(100, height - 100, "Page 2")
        c.drawString(100, height - 130, "Additional concepts:")
        c.drawString(100, height - 160, "Project Management")
        c.drawString(100, height - 190, "Task Tracking")
        c.showPage()
        
        c.save()
        print(f"✅ Created test PDF: {output_path}")
        return True
    except ImportError:
        print("⚠️  reportlab not installed. Install with: pip install reportlab")
        print("   Or use any existing PDF file for testing")
        return False
    except Exception as e:
        print(f"❌ Error creating PDF: {e}")
        return False


if __name__ == "__main__":
    output = sys.argv[1] if len(sys.argv) > 1 else "test.pdf"
    create_test_pdf(output)
