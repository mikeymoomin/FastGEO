# schema.py
import json
from typing import Any, Dict, Optional

def generate_schema_markup(schema_type: Optional[str], 
                          context: Optional[str],
                          props: Optional[Dict[str, Any]] = None) -> str:
    """
    Generate schema.org JSON-LD markup.
    
    Args:
        schema_type: Schema.org type (e.g., 'Article', 'Product')
        context: Additional context for LLMs
        props: Additional schema.org properties
    
    Returns:
        JSON-LD script tag with schema.org markup
    """
    if not schema_type:
        return ""
    
    schema = {
        "@context": "https://schema.org",
        "@type": schema_type
    }
    
    # Add description from context if provided
    if context:
        schema["description"] = context
    
    # Add additional properties
    if props:
        schema.update(props) 
    
    # Convert to JSON
    schema_json = json.dumps(schema, indent=2)
    
    # Wrap in script tag
    return f'<script type="application/ld+json">{schema_json}</script>'
