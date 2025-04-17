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

app,rt = fast_app(hdrs=hdrs, live=True)

def _html(o):
    "Serialise an FT object (or raw string) to HTML."
    return o if isinstance(o, str) else to_xml(o)

def crawler_demo(title, raw_component, helper_component):
    "Little utility that renders the three viewpoints."
    before = to_xml(raw_component)            # what crawlers saw *before*
    after  = to_xml(helper_component)         # what they see *after*

    return Titled(
        title,
        H2("Rendered page"),
        helper_component,                     # browser view

        H2("Crawler HTML – BEFORE helper"),
        Pre(Code(NotStr(escape(before)))),     # plain markup

        H2("Crawler HTML – AFTER helper"),
        Pre(Code(NotStr(escape(after)))),      # enriched markup
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
def llmblock():
    raw     = P("Hello World!")               # the visible element
    helper  = LLMBlock(
        raw,
        ctx="Friendly greeting in page header"
    )
    return crawler_demo("LLMBlock", raw, helper)


# 2) SemanticArticle ────────────────────────────────────────────────────────
@rt("/article")
def article():
    sections = [
        {"heading": "Introduction", "content": P("Generative engines…"),                "level": 2},
        {"heading": "Why GEO?",     "content": P("LLMs rank semantics, not keywords."), "level": 2},
    ]

    # baseline page without helper
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
        metadata={"author":"Jane Dev","datePublished":"2025‑04‑17"},
    )
    return crawler_demo("SemanticArticle", raw_article, helper)

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
    return crawler_demo("FAQOptimizer", raw_faq, helper)

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
    return crawler_demo("TechnicalTermOptimizer", raw, helper)

# 5) ContentChunker ────────────────────────────────────────────────────────
@rt("/chunk")
def chunk():
    # Eight thematic paragraphs (~55 tokens each)
    sections = [
        ("Background" , "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
                         "Phasellus vehicula viverra dolor, vitae facilisis sapien."),
        ("Problem"    , "Fusce in massa non justo interdum scelerisque. Integer at sem "
                         "quis ex malesuada laoreet."),
        ("Data"       , "Curabitur imperdiet fermentum sem, in sollicitudin purus rhoncus "
                         "sit amet. Pellentesque placerat."),
        ("Approach"   , "Morbi sed urna eget odio vulputate dictum. Donec tincidunt "
                         "augue et leo faucibus."),
        ("Training"   , "Aenean dignissim orci vitae nibh congue, ac tristique dolor "
                         "pharetra. Maecenas accumsan."),
        ("Evaluation" , "Praesent a massa id metus auctor rhoncus eget vel leo. Vivamus "
                         "venenatis sapien vel."),
        ("Results"    , "Duis quis tellus a nulla aliquet pharetra. Nullam faucibus, "
                         "urna vitae cursus dictum."),
        ("Conclusion" , "Sed tristique sapien sit amet mauris viverra, vel condimentum "
                         "dolor placerat. Ut gravida."),
    ]

    # Build raw HTML (no helper) – one <p> per section
    raw_html = "".join(f"<p><strong>{h}.</strong> {txt}</p>" for h,txt in sections)

    # Wrap with helper:  max_tokens small to force splitting, overlap for context
    helper = ContentChunker(raw_html, max_tokens=80, overlap=12)

    return crawler_demo("ContentChunker", raw_html, helper)

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
    return crawler_demo("CitationOptimizer", raw, helper)

serve()




