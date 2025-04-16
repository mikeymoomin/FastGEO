# enhancers.py
from fasthtml.common import *
from typing import Any, Dict, Optional, Union

def geo_enhance(component: Any, 
                semantic_type: Optional[str] = None, 
                context: Optional[str] = None,
                schema_props: Optional[Dict[str, Any]] = None,
                **kwargs) -> Any:
    """
    Enhance a FastHTML component with GEO capabilities.
    
    Args:
        component: The FastHTML component to enhance
        semantic_type: Schema.org type (e.g., 'Article', 'Product')
        context: Additional context for LLMs
        schema_props: Additional schema.org properties
        **kwargs: Additional attributes to add to the component
    
    Returns:
        Enhanced component with GEO capabilities
    """
    # Store original __ft__ method
    original_ft = getattr(component, '__ft__', lambda: component)
    
    # Generate schema.org markup
    schema_markup = generate_schema_markup(semantic_type, context, schema_props)
    
    # Define new __ft__ method
    def enhanced_ft():
        # Get original HTML
        original_html = original_ft()
        
        # Add semantic attributes
        enhanced_html = add_semantic_attributes(original_html, semantic_type, **kwargs)
        
        # Combine with schema markup
        if schema_markup:
            return schema_markup + enhanced_html
        return enhanced_html
    
    # Replace __ft__ method
    component.__ft__ = enhanced_ft
    
    return component

