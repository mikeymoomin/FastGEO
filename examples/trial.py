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
        H2("Rendered page"),
        helper_component,                     # browser view

        H2("Crawler HTML – BEFORE helper"),
        Pre(Code(NotStr(escape(before)))),     # plain markup

        H2("Crawler HTML – AFTER helper"),
        Pre(Code(NotStr(escape(after)))),      # enriched markup
        cls="demo",
        id="landing-page-content"
    )

@rt("/")
def home():
    home_main_content = Main(id="landing-page-content")(  # HTMX-enabled nav links
        H1("fasthtml_geo playground"),
        Ul(
            Li(A(hx_get="/llm", hx_target="#landing-page-content", hx_push_url="true")("LLMBlock")),
            Li(A(hx_get="/article", hx_target="#landing-page-content", hx_push_url="true")("SemanticArticle")),
            Li(A(hx_get="/faq", hx_target="#landing-page-content", hx_push_url="true")("FAQOptimizer")),
            Li(A(hx_get="/glossary", hx_target="#landing-page-content", hx_push_url="true")("TechnicalTermOptimizer")),
            Li(A(hx_get="/chunk", hx_target="#landing-page-content", hx_push_url="true")("ContentChunker")),
            Li(A(hx_get="/cite", hx_target="#landing-page-content", hx_push_url="true")("CitationOptimizer")),
        ),
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
        metadata={"author":"Jane Dev","datePublished":"2025‑04‑17"},
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
def chunk():
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

    raw_html = "".join(f"<p><strong>{h}.</strong> {txt}</p>" for h,txt in sections)
    helper = ContentChunker(raw_html, max_tokens=80, overlap=12)
    heading = H1("ContentChunker")
    return crawler_demo(heading, raw_html, helper)

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
