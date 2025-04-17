from fasthtml.common import *
from src.fasthtml_geo import *

app,rt = fast_app()

def crawler_demo(title, raw_component, helper_component):
    """
    raw_component      : an FT element (P, Div, …) *before* GEO helper
    helper_component   : the same content wrapped by a fasthtml_geo helper
    """
    before_html = str(raw_component)        # what the crawler sees now
    after_html  = str(helper_component)     # what the crawler will see

    return Div(
        A("⇠ Back", href="/", cls="secondary"),
        H1(title),

        H2("Rendered page"),
        helper_component,  

        H2("Crawler HTML – BEFORE helper"),
        Pre(Code(NotStr(before_html))),

        H2("Crawler HTML – AFTER helper"),
        Pre(Code(NotStr(after_html))),

        cls="demo",
    )

@rt("/")
def home():
    return Titled(
        "fasthtml_geo playground",
        Ul(
            Li(A(href="/llm")("LLMBlock")),
            Li(A(href="/article")("SemanticArticle")),
            Li(A(href="/faq")("FAQOptimizer")),
            Li(A(href="/glossary")("TechnicalTermOptimizer")),
            Li(A(href="/chunk")("ContentChunker")),
            Li(A(href="/cite")("CitationOptimizer")),
        ),
    )

# 1) LLMBlock ────────────────────────────────────────────────────────────────
@rt("/llm")
def llm():
    raw   = P("Hello World!")
    helper = LLMBlock(raw, ctx="Friendly greeting in page header")
    return crawler_demo("LLMBlock", raw, helper)


# 2) SemanticArticle ────────────────────────────────────────────────────────
@rt("/article")
def article():
    sections = [
        {"heading": "Introduction", "content": P("Generative engines…"), "level": 2},
        {"heading": "Why GEO?", "content": P("LLMs rank semantics, not keywords."), "level": 2},
    ]
    return SemanticArticle(
        title="GEO in a Nutshell",
        sections=sections,
        metadata={"author": "Jane Dev", "datePublished": "2025-04-17"},
    )

# 3) FAQOptimizer ───────────────────────────────────────────────────────────
@rt("/faq")
def faq():
    qa = [
        ("What is GEO?", "Optimising pages so LLM‑driven search surfaces them."),
        ("Does GEO replace SEO?", "No – they complement each other."),
    ]
    return FAQOptimizer(qa_pairs=qa)

# 4) TechnicalTermOptimizer ─────────────────────────────────────────────────
@rt("/glossary")
def glossary():
    html = "<p>Transformers rely on self‑attention for sequence modelling.</p>"
    terms = {
        "transformer": "Neural network architecture based on attention.",
        "self‑attention": "Mechanism where each token attends to all others.",
    }
    return TechnicalTermOptimizer(html=html, glossary=terms)

# 5) ContentChunker ────────────────────────────────────────────────────────
@rt("/chunk")
def chunk():
    lorem = "Lorem ipsum dolor sit amet, " * 120  # ~ 600 tokens
    html = f"<p>{lorem}</p>"
    return ContentChunker(html, max_tokens=120, overlap=20)

# 6) CitationOptimizer ─────────────────────────────────────────────────────
@rt("/cite")
def cite():
    body = (
        "<p>Deep learning has revolutionised NLP"
        '<span class="citation-marker" data-citation-id="1"></span>.</p>'
    )
    cites = [
        {
            "id": 1,
            "title": "Attention Is All You Need",
            "authors": ["Vaswani, A.", "et al."],
            "publisher": "NeurIPS",
            "date": "2017",
            "url": "https://arxiv.org/abs/1706.03762",
        }
    ]
    return CitationOptimizer(body, citations=cites)

serve()




