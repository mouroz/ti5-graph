def normalize_string(name):
    """Normalize a column name by removing whitespace and replacing special characters (excluding hyphen and comma) with underscores"""
    name = str(name).strip().lower()  # Convert to string, strip whitespace, and lowercase
    name = re.sub(r'[^\w\s/,-]', '_', name)  # Replace non-word/non-space/non-hyphen/non-comma chars with _
    name = re.sub(r'\s+', '_', name)      # Replace spaces with _
    name = re.sub(r'_+', '_', name)        # Collapse multiple _ into one
    name = name.strip('_')  # Remove any _ at the start or end of the string

    return name