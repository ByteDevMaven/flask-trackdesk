from app.invoices.services.invoice_pdf_service import PdfTemplateLayout

FERRE_LAGOS_LAYOUT = PdfTemplateLayout(
    template_name="Factura Ferre-lagos.pdf",
    # Uses default coordinates which were extracted from the original Ferre-Lagos hardcoded template
)
