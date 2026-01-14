"""Utility functions for data conversion and cleaning"""

def clean_number(value):
    """Convert Swedish number format to float (handles , as decimal separator and spaces)"""
    if not value or value == '-' or value == '':
        return None
    try:
        # Remove spaces (thousand separators)
        value = value.replace(' ', '')
        # Replace comma with dot (decimal separator)
        value = value.replace(',', '.')
        # Remove % if present
        value = value.replace('%', '')
        return float(value)
    except (ValueError, AttributeError):
        return None

def clean_integer(value):
    """Convert to integer, handling Swedish formatting"""
    if not value or value == '-' or value == '':
        return None
    try:
        # Remove spaces
        value = value.replace(' ', '')
        # Remove any decimal part
        value = value.split(',')[0].split('.')[0]
        return int(value)
    except (ValueError, AttributeError):
        return None
