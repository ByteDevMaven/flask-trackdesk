from .ferre_lagos import FERRE_LAGOS_LAYOUT

# A mapping of company_id to layout. 
# You can map multiple companies to the same layout, or give each their own.
# If a company isn't found, it falls back to a default layout.
LAYOUT_REGISTRY = {
    # 1: FERRE_LAGOS_LAYOUT,
    # Add other company IDs here
}

# The default layout used when a company doesn't have a specific mapping
DEFAULT_LAYOUT = FERRE_LAGOS_LAYOUT

def get_layout(company_id: int):
    """Retrieve the PdfTemplateLayout for the given company_id."""
    return LAYOUT_REGISTRY.get(company_id, DEFAULT_LAYOUT)
