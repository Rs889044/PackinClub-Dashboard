"""
pdf_generator.py — Generate professional PDF invoices/quotations
================================================================
PackinClub-themed layout: dark green header, gold accents,
clean typography, proper spacing.

Returns PDF as bytes (in-memory) — no file saved to disk.
"""

import os
from fpdf import FPDF
from database import get_user_profile, get_line_items


def safe(text):
    """Sanitize text for Helvetica (Latin-1 only). Replace unsupported chars."""
    if not isinstance(text, str):
        text = str(text)
    replacements = {
        "\u2014": "-",   # em dash —
        "\u2013": "-",   # en dash –
        "\u2018": "'",   # left single quote '
        "\u2019": "'",   # right single quote '
        "\u201c": '"',   # left double quote "
        "\u201d": '"',   # right double quote "
        "\u2026": "...", # ellipsis …
        "\u20b9": "Rs.", # ₹ rupee sign
        "\u2022": "-",   # bullet •
        "\u00a0": " ",   # non-breaking space
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    # Fallback: strip any remaining non-latin1 chars
    text = text.encode("latin-1", errors="replace").decode("latin-1")
    return text


# ── PackinClub brand colours ──
DARK_GREEN  = (27, 58, 45)     # #1B3A2D
MID_GREEN   = (45, 74, 62)     # #2D4A3E
LIGHT_GREEN = (232, 240, 232)  # #E8F0E8
GOLD        = (197, 165, 90)   # #C5A55A
WHITE       = (255, 255, 255)
BLACK       = (30, 30, 30)
GRAY        = (120, 120, 120)
LIGHT_GRAY  = (245, 248, 245)
BORDER_GRAY = (210, 220, 210)


class InvoicePDF(FPDF):
    """Custom PDF class with PackinClub-themed header/footer."""

    def __init__(self, company_info, doc_type="Invoice", doc_number="", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.company = company_info or {}
        self.doc_type = doc_type
        self.doc_number = doc_number
        self.set_auto_page_break(auto=True, margin=28)

    # ──────────────────────────────────────
    # HEADER
    # ──────────────────────────────────────
    def header(self):
        banner_h = 32
        # Full-width dark green banner
        self.set_fill_color(*LIGHT_GRAY)
        self.rect(0, 0, 210, banner_h, "F")

        # Gold accent line at bottom of banner
        self.set_fill_color(*GOLD)
        self.rect(0, banner_h, 210, 1, "F")

        # ── Logo (left corner) ──
        logo = self.company.get("logo_path", "")
        if logo and os.path.isfile(logo):
            try:
                logo_h = 12
                logo_y = (banner_h - logo_h) / 2
                self.image(logo, 10, logo_y, h=logo_h)
            except Exception:
                pass

        # ── Company details (right-aligned) ──
        rx = 198  # right edge with margin

        # Company name
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(*DARK_GREEN)
        name = safe(self.company.get("company_name", "Your Company"))
        self.set_xy(80, 5)
        self.cell(rx - 80, 6, name, align="R")

        # Address
        self.set_font("Helvetica", "", 7.5)
        self.set_text_color(*DARK_GREEN)
        if self.company.get("address"):
            self.set_xy(80, 12)
            self.cell(rx - 80, 4, safe(self.company["address"]), align="R")

        # Contact line
        contact = []
        if self.company.get("phone"):
            contact.append(f"Ph: {self.company['phone']}")
        if self.company.get("email"):
            contact.append(self.company["email"])
        if self.company.get("website"):
            contact.append(self.company["website"])
        if contact:
            self.set_xy(80, 17)
            self.cell(rx - 80, 4, safe(" | ".join(contact)), align="R")

        # GST number
        if self.company.get("gst_number"):
            self.set_font("Helvetica", "", 7)
            self.set_text_color(*GOLD)
            self.set_xy(80, 22)
            self.cell(rx - 80, 4, safe(f"GSTIN: {self.company['gst_number']}"), align="R")

        self.set_y(banner_h + 5)

    # ──────────────────────────────────────
    # FOOTER
    # ──────────────────────────────────────
    def footer(self):
        self.set_y(-22)

        # Gold line
        self.set_fill_color(*GOLD)
        self.rect(10, self.get_y(), 190, 0.5, "F")

        # Footer text
        self.set_font("Helvetica", "", 6.5)
        self.set_text_color(*GRAY)
        self.set_y(-18)
        self.cell(95, 4, "Thank you for your business!", align="L")
        self.cell(95, 4, f"Page {self.page_no()}/{{nb}}", align="R")

        # Company name in footer
        self.set_y(-14)
        self.set_font("Helvetica", "I", 6)
        self.set_text_color(160, 170, 160)
        name = self.company.get("company_name", "")
        if name:
            self.cell(0, 4, safe(f"{name} - Generated digitally"), align="C")


def generate_invoice_pdf(invoice_data, doc_type="Invoice"):
    """
    Generate a professional PDF for an invoice or quotation.

    Returns:
        tuple: (pdf_bytes, filename) — raw PDF bytes and suggested filename.
    """
    company = get_user_profile() or {}
    ref_type = "invoice" if doc_type == "Invoice" else "quotation"
    items = get_line_items(ref_type, invoice_data["id"])

    number_key = "invoice_number" if doc_type == "Invoice" else "quotation_number"
    doc_number = invoice_data.get(number_key, "N/A")

    pdf = InvoicePDF(company, doc_type=doc_type, doc_number=doc_number)
    pdf.alias_nb_pages()
    pdf.add_page()

    # ── Document title + number in body ──
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(*DARK_GREEN)
    pdf.cell(100, 9, doc_type.upper(), align="L")

    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*GRAY)
    date_str = invoice_data.get("created_at", "")[:10]
    pdf.cell(90, 9, f"Date: {date_str}", align="R", ln=True)

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(100, 5, f"#{doc_number}", ln=True)
    pdf.ln(4)

    # ══════════════════════════════════════
    # BILL TO — Customer Info Box
    # ══════════════════════════════════════
    pdf.set_fill_color(*LIGHT_GREEN)
    box_y = pdf.get_y()
    pdf.rect(10, box_y, 190, 26, "F")

    # Left border accent
    pdf.set_fill_color(*MID_GREEN)
    pdf.rect(10, box_y, 2.5, 26, "F")

    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(*MID_GREEN)
    pdf.set_xy(16, box_y + 3)
    pdf.cell(40, 4, "BILL TO", ln=False)

    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(*BLACK)
    pdf.set_xy(16, box_y + 8)
    pdf.cell(100, 5, safe(invoice_data.get("customer_name", "-")))

    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(80, 80, 80)
    pdf.set_xy(16, box_y + 14)
    pdf.cell(100, 4, safe(invoice_data.get("customer_address", "") or ""))

    # Phone + State
    pdf.set_xy(16, box_y + 19)
    info = []
    if invoice_data.get("customer_phone"):
        info.append(f"Ph: {invoice_data['customer_phone']}")
    if invoice_data.get("customer_state"):
        info.append(invoice_data["customer_state"])
    pdf.cell(100, 4, safe(" | ".join(info)))

    pdf.set_y(box_y + 30)

    # ══════════════════════════════════════
    # ITEMS TABLE
    # ══════════════════════════════════════
    col_w = [12, 78, 28, 18, 28, 26]  # #, Product, Price, Qty, Subtotal, (pad)

    # Table header
    pdf.set_fill_color(*DARK_GREEN)
    pdf.set_text_color(*WHITE)
    pdf.set_font("Helvetica", "B", 8.5)
    headers = ["#", "Product / Description", "Unit Price", "Qty", "Amount"]
    for i, h in enumerate(headers):
        pdf.cell(col_w[i], 9, h, border=0, fill=True, align="C")
    pdf.cell(col_w[5], 9, "", border=0, fill=True)
    pdf.ln()

    # Table rows
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(*BLACK)

    for idx, item in enumerate(items, 1):
        is_alt = idx % 2 == 0
        if is_alt:
            pdf.set_fill_color(245, 248, 245)
        else:
            pdf.set_fill_color(255, 255, 255)

        row_y = pdf.get_y()

        pdf.cell(col_w[0], 8, str(idx), border=0, fill=True, align="C")
        pdf.cell(col_w[1], 8, safe(item.get("product_name", "")), border=0, fill=True, align="L")
        pdf.cell(col_w[2], 8, f"{item['price']:,.2f}", border=0, fill=True, align="R")
        pdf.cell(col_w[3], 8, str(item["quantity"]), border=0, fill=True, align="C")
        pdf.cell(col_w[4], 8, f"{item['subtotal']:,.2f}", border=0, fill=True, align="R")
        pdf.cell(col_w[5], 8, "", border=0, fill=True)
        pdf.ln()

        # Subtle row border
        pdf.set_draw_color(*BORDER_GRAY)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())

    pdf.ln(4)

    # ══════════════════════════════════════
    # TOTALS SECTION (right-aligned)
    # ══════════════════════════════════════
    totals_x = 118
    label_w = 42
    value_w = 40

    gst_rate = invoice_data.get("gst_rate", 18)

    # Subtotal
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(80, 80, 80)
    pdf.set_x(totals_x)
    pdf.cell(label_w, 7, "Subtotal", align="R")
    pdf.cell(value_w, 7, f"{invoice_data['total_amount']:,.2f}", align="R")
    pdf.ln()

    # GST
    pdf.set_x(totals_x)
    pdf.cell(label_w, 7, f"GST ({gst_rate}%)", align="R")
    pdf.cell(value_w, 7, f"{invoice_data['gst_amount']:,.2f}", align="R")
    pdf.ln()

    # Separator line
    pdf.set_draw_color(*MID_GREEN)
    pdf.set_line_width(0.4)
    pdf.line(totals_x, pdf.get_y(), totals_x + label_w + value_w, pdf.get_y())
    pdf.ln(2)

    # Grand Total
    pdf.set_fill_color(*DARK_GREEN)
    gt_y = pdf.get_y()
    pdf.rect(totals_x, gt_y, label_w + value_w, 10, "F")
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(*WHITE)
    pdf.set_xy(totals_x, gt_y + 1)
    pdf.cell(label_w, 8, "GRAND TOTAL", align="R")

    pdf.set_text_color(*GOLD)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(value_w, 8, f"{invoice_data['grand_total']:,.2f}", align="R")
    pdf.ln(16)

    # ── Amount in words (optional) ──
    pdf.set_line_width(0.2)

    # ══════════════════════════════════════
    # TERMS / NOTES SECTION
    # ══════════════════════════════════════
    pdf.ln(4)
    pdf.set_draw_color(*BORDER_GRAY)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 7.5)
    pdf.set_text_color(*MID_GREEN)
    pdf.cell(0, 4, "TERMS & CONDITIONS", ln=True)
    pdf.set_font("Helvetica", "", 7)
    pdf.set_text_color(*GRAY)
    pdf.cell(0, 3.5, "1. Payment is due within 30 days of the invoice date.", ln=True)
    pdf.cell(0, 3.5, "2. All products are 100% compostable and CPCB certified.", ln=True)
    pdf.cell(0, 3.5, "3. Goods once sold will not be taken back or exchanged.", ln=True)

    pdf.ln(6)

    # ── Bank details / Signature area ──
    sig_y = pdf.get_y()
    pdf.set_font("Helvetica", "B", 7.5)
    pdf.set_text_color(*MID_GREEN)
    pdf.set_xy(130, sig_y)
    pdf.cell(68, 4, "Authorized Signatory", align="C")
    pdf.set_xy(130, sig_y + 14)
    pdf.set_draw_color(*MID_GREEN)
    pdf.line(140, sig_y + 14, 195, sig_y + 14)
    pdf.set_font("Helvetica", "", 7)
    pdf.set_text_color(*GRAY)
    pdf.set_xy(130, sig_y + 16)
    company_name = company.get("company_name", "")
    pdf.cell(68, 4, safe(f"For {company_name}") if company_name else "", align="C")

    # ── Return as bytes (no file saved to disk) ──
    pdf_bytes = bytes(pdf.output())  # returns bytes when no filepath is given
    filename = f"{doc_type}_{doc_number}.pdf"
    return pdf_bytes, filename