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

def crawler_demo(title, raw_component, helper_component):
    "Little utility that renders the three viewpoints."
    before = to_xml(raw_component)            # what crawlers saw *before*
    after  = to_xml(helper_component)         # what they see *after*
    
    return Main(
        Button(hx_get="/", hx_target="#landing-page-content", hx_push_url="true", cls="back-button")("← Back to Home"),
        title,
        
        # Website display with browser mock
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

def chunk_demo(title, raw_component, helper_component):
    """Utility to render raw page, chunk highlight, and crawler views"""
    before = to_xml(raw_component)
    after  = to_xml(helper_component)

    return Main(
        Button(hx_get="/", hx_target="#landing-page-content", hx_push_url="true", cls="back-button")("← Back to Home"),
        title,

        H2("Rendered page"),
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
                NotStr(raw_component),
                cls="browser-content"
            ),
            cls="website-display"
        ),

        H2("Chunkation of Paragraphs"),
        Div(
            # Show the chunked content with highlighting
            helper_component,
            cls="browser-content"
        ),

        H2("Crawler HTML – BEFORE helper"),
        Pre(Code(NotStr(escape(before)))),

        H2("Crawler HTML – AFTER helper"),
        Pre(Code(NotStr(escape(after)))),

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
    return crawler_demo(heading, raw, helper)

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
    return crawler_demo(heading, raw_article, helper)

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
    return crawler_demo(heading , raw_faq, helper)

# 4) TechnicalTermOptimizer ─────────────────────────────────────────────────
@rt("/glossary")
def glossary():
    html  = "<p>Transformers rely on self‑attention for sequence modelling.</p>"
    terms = {
        "transformer":   "Neural network architecture based on attention.",
        "self‑attention":"Mechanism where each token attends to all others.",
    }
    raw     = html                                     # plain string baseline
    helper  = TechnicalTermOptimizer(html=html, glossary=terms)
    heading = H1("TechnicalTermOptimizer")
    return crawler_demo(heading, raw, helper)

# 5) ContentChunker ────────────────────────────────────────────────────────
@rt("/chunk")
def get():
    # A big blob of HTML we'll chunk
    body = """
    <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit.</p>
    <p>Vivamus vitae ligula in elit porttitor egestas.</p>
    <p>Praesent fermentum, urna ac sollicitudin sodales, enim nisl bibendum orci.</p>
    <p>Nulla facilisi. Donec euismod, nisl eget consectetur sagittis.</p>
    <p>Curabitur a orci vitae lectus volutpat tincidunt.</p>
    """

    # Apply the ContentChunker helper
    # max_tokens controls approximate chunk size; overlap ensures smooth transitions
    helper = ContentChunker(html=body, max_tokens=50, overlap=1)

    # Page heading
    heading = H1("ContentChunker Demo")

    # Render a side-by-side view: raw HTML vs. chunked helper output
    return chunk_demo(heading, body, helper)

# 6) CitationOptimizer ─────────────────────────────────────────────────────
@rt("/cite")
def cite():
    body = (
        "<p>Deep learning has revolutionised NLP"
        '<span class="citation-marker" data-citation-id="1"></span>.</p>'
    )
    cites = [{
        "id":1,
        "title":"Attention Is All You Need",
        "authors":["Vaswani, A.", "et al."],
        "publisher":"NeurIPS",
        "date":"2017",
        "url":"https://arxiv.org/abs/1706.03762",
    }]
    raw    = body
    helper = CitationOptimizer(body, citations=cites)
    heading = H1("CitationOptimizer")
    return crawler_demo(heading, raw, helper)

serve()
