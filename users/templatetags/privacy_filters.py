import re
from django import template

register = template.Library()


@register.filter(name='postcode_area')
def postcode_area(value):
    """
    Redact a UK postcode to its outward code only.
    e.g. "B63 3TH" → "B63", "SW1A 1AA" → "SW1A", "M1 1AA" → "M1"
    If the value doesn't look like a postcode, returns the value as-is.
    """
    if not value:
        return value
    value = str(value).strip()
    # UK postcode pattern: outward code = 2-4 chars, inward code = 3 chars
    match = re.match(r'^([A-Z]{1,2}\d[A-Z\d]?)\s*\d[A-Z]{2}$', value, re.IGNORECASE)
    if match:
        return match.group(1).upper()
    # If it doesn't match a full postcode, return as-is (might already be partial)
    return value
