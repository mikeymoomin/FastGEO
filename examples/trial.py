import os, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT)

from fasthtml.common import *
from src.fasthtml_geo import *
from html import escape    

hdrs = [
    Meta(charset='UTF-8'),
    Meta(name='viewport', content='width=device-width, initial-scale=1.0'),
    Link(rel='stylesheet', href='styles.css'),
]

app, rt = fast_app(hdrs=hdrs, live=True)

def _html(o):
    "Serialise an FT object (or raw string) to HTML."
    return o if isinstance(o, str) else to_xml(o)

def crawler_demo(title, raw_component, helper_component, code):
    "Little utility that renders the three viewpoints."
    before = to_xml(raw_component)            # what crawlers saw *before*
    after  = to_xml(helper_component)         # what they see *after*
    
    # Extract text from the title if it's a FastHTML element
    title_text = title if isinstance(title, str) else title.children[0] if hasattr(title, 'children') else str(title)
    
    return Main(
        Button(hx_get="/", hx_target="#landing-page-content", hx_push_url="true", cls="back-button")("← Back to Home"),
        title,
        
        # VS Code style code display
        H2("Code Entered"),
        Div(
            Pre(
                Code(NotStr(code)),
                cls="code-container"
            )
        ),
      
        H2("Rendered page"),
        Div(
            # Browser header
            Div(
                Div(
                    Div(cls="browser-dot red"),
                    Div(cls="browser-dot yellow"),
                    Div(cls="browser-dot green"),
                    cls="browser-dots"
                ),
                Div(
                    Input(type="text", value="https://example.com/page", readonly=True),
                    cls="browser-address"
                ),
                cls="browser-header"
            ),
            # Browser content
            Div(
                helper_component,
                cls="browser-content"
            ),
            cls="website-display"
        ),
        
        H2("Crawler HTML – BEFORE helper"),
        Pre(Code(NotStr(escape(before)))),        # plain markup
        
        H2("Crawler HTML – AFTER helper"),
        Pre(Code(NotStr(escape(after)))),         # enriched markup
        
        cls="demo",
        id="landing-page-content"
    )


def chunk_demo(title, raw_component, helper_component, code):
    """Utility to render raw page, chunk highlight, and crawler views"""
    # Ensure raw_component is serialized if it's not already a string
    before_html = raw_component if isinstance(raw_component, str) else to_xml(raw_component)
    after_html  = to_xml(helper_component) # helper_component.__ft__() returns FT object

    # Extract text from the title if it's a FastHTML element
    title_text = title if isinstance(title, str) else title.children[0] if hasattr(title, 'children') and title.children else str(title)

    return Main(
        Button(hx_get="/", hx_target="#landing-page-content", hx_push_url="true", cls="back-button")("← Back to Home"),
        H1(title_text), # Use H1 for consistency

        H2("Code Entered"),
        Div(
            Pre(
                Code(NotStr(code)), # Use NotStr here for pre-formatted code
                cls="code-container"
            )
        ),

        H2("Rendered Page (Original)"),
        Div(
            # Browser mock header
            Div(
                Div(
                    Div(cls="browser-dot red"),
                    Div(cls="browser-dot yellow"),
                    Div(cls="browser-dot green"),
                    cls="browser-dots"
                ),
                Div(
                    Input(type="text", value="https://example.com/page", readonly=True),
                    cls="browser-address-chunk"
                ),
                cls="browser-header-chunk"
            ),
            # Show the unmodified content as it would normally render
            Div(
                # Render the original component directly (FastHTML handles tuples/lists)
                raw_component,
                cls="browser-content-chunk"
            ),
            cls="website-display"
        ),

        H2("Chunk Visualization"),
        Div(
            # Show the chunked content with highlighting/borders (add CSS for .chunked-view .content-chunk)
            helper_component, # Renders the output of ContentChunker.__ft__()
            cls="browser-content" # Re-use class for consistent padding/style
        ),

        H2("Crawler HTML – BEFORE helper"),
        Pre(Code(escape(before_html))), # Escape the raw HTML string

        H2("Crawler HTML – AFTER helper"),
        Pre(Code(escape(after_html))),  # Escape the processed HTML string

        cls="demo",
        id="landing-page-content"
    )

@rt("/")
def home():
    home_main_content = Main(id="landing-page-content")(    # HTMX-enabled nav links
        # Hero Section
        Div(
            H1("fasthtml_geo"),
            P("Generative Engine Optimization for FastHTML Applications"),
            cls="hero"
        ),
        
        # Main Navigation
        Div(
            H2("Explore GEO Components"),
            Ul(
                Li(
                    A(hx_get="/llm", hx_target="#landing-page-content", hx_push_url="true")(
                        H3("LLMBlock"),
                        P("Attach context and metadata to any FastHTML element for better LLM understanding")
                    )
                ),
                Li(
                    A(hx_get="/article", hx_target="#landing-page-content", hx_push_url="true")(
                        H3("SemanticArticle"),
                        P("Structured articles with proper schema markup for enhanced discoverability")
                    )
                ),
                Li(
                    A(hx_get="/faq", hx_target="#landing-page-content", hx_push_url="true")(
                        H3("FAQOptimizer"),
                        P("Convert FAQs to schema.org format for better search engine visibility")
                    )
                ),
                Li(
                    A(hx_get="/glossary", hx_target="#landing-page-content", hx_push_url="true")(
                        H3("TechnicalTermOptimizer"),
                        P("Highlight and define technical terms with semantic markup and glossaries")
                    )
                ),
                Li(
                    A(hx_get="/chunk", hx_target="#landing-page-content", hx_push_url="true")(
                        H3("ContentChunker"),
                        P("Split content into optimized chunks for better LLM processing")
                    )
                ),
                Li(
                    A(hx_get="/cite", hx_target="#landing-page-content", hx_push_url="true")(
                        H3("CitationOptimizer"),
                        P("Transform citations into semantic markup for academic and reference content")
                    )
                ),
            ),
            cls="main-nav"
        ),
        
        # Footer
        Div(
            P("Built with fasthtml_geo – Optimize your FastHTML applications for generative engines"),
            cls="footer"
        )
    )
    return Body(home_main_content)

# 1) LLMBlock ────────────────────────────────────────────────────────────────
@rt("/llm")
def llmblock():
    raw     = P("Hello World!")   
    helper  = LLMBlock(
        raw,
        ctx="Friendly greeting in page header"
    )
    heading = H1("LLMBlock")

    code = 'LLMBlock((P"Hello World"), "Friendly greeting in page header")'

    return crawler_demo(heading, raw, helper, code)

# 2) SemanticArticle ────────────────────────────────────────────────────────
@rt("/article")
def article():
    sections = [
        {"heading": "Introduction", "content": P("Generative engines…"),                "level": 2},
        {"heading": "Why GEO?",     "content": P("LLMs rank semantics, not keywords."), "level": 2},
    ]

    raw_article = Article(
        H1("GEO in a Nutshell"),
        H2("Introduction"),
        Div(P("Generative engines…"),                itemprop="articleBody"),
        H2("Why GEO?"),
        Div(P("LLMs rank semantics, not keywords."), itemprop="articleBody"),
        itemscope=True, itemtype="https://schema.org/Article",
    )

    helper = SemanticArticle(
        title="GEO in a Nutshell",
        sections=sections,
        metadata={"author":"Jane Dev","datePublished":"2025‑04‑17"},
    )
    heading = H1("SemanticArticle")

    code = """
    sections = [
        {"heading": "Introduction", "content": P("Generative engines…"),                "level": 2},
        {"heading": "Why GEO?",     "content": P("LLMs rank semantics, not keywords."), "level": 2},
    ]

    SemanticArticle(
            title = "GEO in a Nutshell",
            sections = sections,
            metadata={"author":"Jane Dev","datePublished":"2025‑04‑17"},
    )"""

    return crawler_demo(heading, raw_article, helper, code)

# 3) FAQOptimizer ───────────────────────────────────────────────────────────
@rt("/faq")
def faq():
    qa = [
        ("What is GEO?",         "Optimising pages so LLM‑driven search surfaces them."),
        ("Does GEO replace SEO?","No – they complement each other."),
    ]
    raw_faq = Section(
        *[Div(H3(q), P(a), cls="faq-item") for q,a in qa],
        cls="faq",
    )
    helper = FAQOptimizer(qa_pairs=qa)

    heading = H1("FAQOptimizer")

    code = """
        qa = [
            ("What is GEO?",         "Optimising pages so LLM‑driven search surfaces them."),
            ("Does GEO replace SEO?","No – they complement each other."),

        FAQOptimizer(qa_pairs=qa)
    """

    return crawler_demo(heading , raw_faq, helper, code)

# 4) TechnicalTermOptimizer ─────────────────────────────────────────────────
@rt("/glossary")
def glossary():
    html  = P("Transformers rely on self‑attention for sequence modelling.")
    terms = {
        "transformer":   "Neural network architecture based on attention.",
        "self‑attention":"Mechanism where each token attends to all others.",
    }
    raw     = html                                     # plain string baseline
    helper  = TechnicalTermOptimizer(html, glossary=terms)
    heading = H1("TechnicalTermOptimizer")

    code = """
    html  = "P(Transformers rely on self‑attention for sequence modelling.)"
    terms = {
        "transformer":   "Neural network architecture based on attention.",
        "self‑attention":"Mechanism where each token attends to all others.",
    }
    TechnicalTermOptimizer(html=html, glossary=terms)
"""

    return crawler_demo(heading, raw, helper, code)

# 5) ContentChunker ────────────────────────────────────────────────────────
def chunk_demo(title, raw_component, helper_component, code):
    """Utility to render raw page, chunk highlight, and crawler views"""
    # Ensure raw_component is serialized if it's not already a string
    before_html = raw_component if isinstance(raw_component, str) else to_xml(raw_component)
    after_html  = to_xml(helper_component) # helper_component.__ft__() returns FT object

    # Extract text from the title if it's a FastHTML element
    title_text = title if isinstance(title, str) else title.children[0] if hasattr(title, 'children') and title.children else str(title)

    return Main(
        Button(hx_get="/", hx_target="#landing-page-content", hx_push_url="true", cls="back-button")("← Back to Home"),
        H1(title_text), # Use H1 for consistency

        H2("Code Entered"),
        Div(
            Pre(
                Code(NotStr(code)), # Use NotStr here for pre-formatted code
                cls="code-container"
            )
        ),

        H2("Rendered Page (Original)"),
        Div(
            # Browser mock header
            Div(
                Div(
                    Div(cls="browser-dot red"),
                    Div(cls="browser-dot yellow"),
                    Div(cls="browser-dot green"),
                    cls="browser-dots"
                ),
                Div(
                    Input(type="text", value="https://example.com/page", readonly=True),
                    cls="browser-address"
                ),
                cls="browser-header"
            ),
            # Show the unmodified content as it would normally render
            Div(
                # Render the original component directly (FastHTML handles tuples/lists)
                raw_component,
                cls="browser-content"
            ),
            cls="website-display"
        ),

        H2("Chunk Visualization"),
        Div(
            # Show the chunked content with highlighting/borders (add CSS for .chunked-view .content-chunk)
            helper_component, # Renders the output of ContentChunker.__ft__()
            cls="browser-content" # Re-use class for consistent padding/style
        ),

        H2("Crawler HTML – BEFORE helper"),
        Pre(Code(escape(before_html))), # Escape the raw HTML string

        H2("Crawler HTML – AFTER helper"),
        Pre(Code(escape(after_html))),  # Escape the processed HTML string

        cls="demo",
        id="landing-page-content"
    )

# ... (home, llmblock, article, faq, glossary routes) ...

# --- Updated /chunk route ---
@rt("/chunk")
def chunk_route(): # Renamed function slightly to avoid conflict with built-in 'get'
    # A big blob of HTML content defined using FastHTML components
    body_components = Group( # Wrap in Group or similar if multiple top-level elements
        P("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Fusce Mollis."),
        P("Vivamus vitae ligula in elit porttitor egestas. Nam ut eleifend dui."),
        P("Praesent fermentum, urna ac sollicitudin sodales, enim nisl bibendum orci, vel eleifend."),
        P("Nulla facilisi. Donec euismod, nisl eget consectetur sagittis, velit massa."),
        H3("A Subheading"),
        P("Curabitur a orci vitae lectus volutpat tincidunt. Aliquam erat volutpat."),
        Ul(Li("First item."), Li("Second long item that might push token limits."), Li("Third item.")),
        P("Final paragraph after the list.")
    )

    # Apply the ContentChunker helper to the HTML string
    # max_tokens controls approximate chunk size; overlap ensures smooth transitions
    helper = ContentChunker(body_components, max_tokens=30, overlap=1) # Reduced max_tokens for demo

    # Page heading
    heading = "ContentChunker" # Just the text for the H1

    code = f"""
# Original FastHTML components (example)
body_components = Group(
    P("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Fusce Mollis."),
    P("Vivamus vitae ligula in elit porttitor egestas. Nam ut eleifend dui."),
    P("Praesent fermentum, urna ac sollicitudin sodales, enim nisl bibendum orci, vel eleifend."),
    P("Nulla facilisi. Donec euismod, nisl eget consectetur sagittis, velit massa."),
    H3("A Subheading"),
    P("Curabitur a orci vitae lectus volutpat tincidunt. Aliquam erat volutpat."),
    Ul(Li("First item."), Li("Second long item that might push token limits."), Li("Third item.")),
    P("Final paragraph after the list.")
)

# Convert to HTML string
raw_html_string = to_xml(body_components)

# Apply chunker
helper = ContentChunker(raw_html_string, max_tokens=30, overlap=1)
"""

    # Render using the updated chunk_demo
    # Pass the *original components* for rendering, and the helper instance
    return chunk_demo(heading, body_components, helper, code)

# 6) CitationOptimizer ─────────────────────────────────────────────────────
@rt("/cite")
def cite():
    # 1) Your raw citation metadata (full list)
    cites = [{
        "id": 1,
        "title": "Attention Is All You Need",
        "authors": ["Vaswani, A.", "et al."],
        "publisher": "NeurIPS",
        "date": "2017",
        "url": "https://arxiv.org/abs/1706.03762",
    },
    {
        "id": 2,
        "title": "Another Great Paper",
        "authors": ["Author B", "et al."],
        "publisher": "Journal X",
        "date": "2020",
        "url": "https://example.com/paper2",
    }]

    # 2) Build your FT component and invoke the CitationOptimizer directly
    #    passing the HTML element, the specific citation ID, and the full list.
    body    = P("Deep learning has revolutionised NLP")
    # The function call is now: CitationOptimizer(HTML, citation_id, cite_list)
    helper  = CitationOptimizer(body, 1, cites) # <-- New signature here

    # 3) Show the exact same syntax in the demo panel
    code = """
cites = [{
    "id": 1,
    "title": "Attention Is All You Need",
    "authors": ["Vaswani, A.", "et al."],
    "publisher": "NeurIPS",
    "date": "2017",
    "url": "https://arxiv.org/abs/1706.03762",
},
{
    "id": 2,
    "title": "Another Great Paper",
    "authors": ["Author B", "et al."],
    "publisher": "Journal X",
    "date": "2020",
    "url": "https://example.com/paper2",
}]

# Direct call with the new signature
CitationOptimizer(P("Deep learning has revolutionised NLP"), 1, cites)
"""

    heading = H1("CitationOptimizer")
    return crawler_demo(heading, body, helper, code)

serve()
