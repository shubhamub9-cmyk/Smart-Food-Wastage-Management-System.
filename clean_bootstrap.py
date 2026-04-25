import os
import re

# Dictionary of class replacements
# Key: Regex pattern to match the class name
# Value: Replacement string
REPLACEMENTS = {
    r'\bcontainer\b': 'app-container',
    r'\bcard\b(?!-)': 'modern-card',
    r'\btable\b(?!-)': 'modern-table',
    r'\b(table-responsive|table-striped|table-hover|table-bordered)\b': '',
    r'\brow\b': 'grid-2',
    r'\bcol-md-\d+\b': '',
    r'\bcol-lg-\d+\b': '',
    r'\bcol-sm-\d+\b': '',
    r'\bcol-12\b': '',
    r'\bmb-3\b': 'mb-4',
    r'\bmt-3\b': 'mt-4',
    r'\bbg-light\b': '',
    r'\bbg-white\b': '',
    r'\bshadow-sm\b': '',
    r'\bshadow\b': '',
    r'\brounded\b': '',
    r'\bdisplay-4\b': '',
    r'\blead\b': '',
    r'\btext-white\b': '',
    r'\bbg-success\b': '',
    r'\bbg-primary\b': '',
    r'\bbg-warning\b': '',
    r'\bbg-danger\b': '',
    r'\bbg-info\b': '',
    r'\bbadge bg-success\b': 'badge badge-success',
    r'\bbadge bg-warning( text-dark)?\b': 'badge badge-warning',
    r'\bbadge bg-danger\b': 'badge badge-danger',
    r'\bbadge bg-secondary\b': 'badge',
    r'\bd-flex justify-content-between align-items-center\b': 'flex-between',
    r'\bd-flex justify-content-between\b': 'flex-between',
    r'\bd-flex align-items-center\b': 'flex-center',
    r'\btext-end\b': 'text-right',
    r'\bfloat-end\b': '',
    r'\bbtn-sm\b': 'btn-sm', # Leave as is, we have .btn-sm
    r'\bw-100\b': 'w-100',   # Leave as is
    r'\bgap-2\b': 'gap-2',
    r'\bgap-3\b': 'gap-4',
    r'\bgap-4\b': 'gap-4',
}

def clean_classes_in_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # Find all class="..." attributes
    def replace_class_attr(match):
        classes_str = match.group(1)
        classes = classes_str
        
        # Apply standard replacements
        for pattern, replacement in REPLACEMENTS.items():
            classes = re.sub(pattern, replacement, classes)
            
        # Clean up empty spaces and duplicate spaces
        classes = re.sub(r'\s+', ' ', classes).strip()
        
        if not classes:
            return '' # Remove empty class attribute entirely
        return f'class="{classes}"'

    content = re.sub(r'class="([^"]*)"', replace_class_attr, content)

    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated: {filepath}")

def main():
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    # Skip base.html as we already manually updated it
    skip_files = ['base.html']
    
    for root, dirs, files in os.walk(templates_dir):
        for file in files:
            if file.endswith('.html') and file not in skip_files:
                filepath = os.path.join(root, file)
                clean_classes_in_file(filepath)
                
if __name__ == "__main__":
    main()
