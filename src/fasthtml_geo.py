"""fasthtml_geo – draft 3
====================================
Drop the brittle inheritance on FastHTML internals.  The documented
extension pattern is either:
  • a *function* that returns FastTags, or
  • a *dataclass* that implements `__ft__()` and returns FastTags.

This version converts every helper to a simple dataclass with `__ft__`.
We wrap raw HTML with `NotStr` so FastHTML will not escape it.
"""

from __future__ import annotations

import json, math
from dataclasses import dataclass
from datetime import datetime
from collections import Counter
from typing import Any, Union, List, Dict, Tuple

from bs4 import BeautifulSoup  # type: ignore
from fasthtml.common import *  # FastTags + NotStr, Div, etc.

__all__ = [
    "LLMBlock",
    "SemanticArticle",
    "FAQOptimizer",
    "TechnicalTermOptimizer",
    "ContentChunker",
    "CitationOptimizer",
    "information_density",
]

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _json(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))

def _script(j: Dict[str, Any]) -> str:
    return f'<script type="application/ld+json">{_json(j)}</script>'

# ---------------------------------------------------------------------------
# low‑level primitive
# ---------------------------------------------------------------------------

@dataclass
class LLMBlock:
    element: Any         # FT component or raw HTML
    ctx: str
    role: str = "summary"
    schema_type: str | None = None

    def __ft__(self):
        """Wrap *any* FT element and attach additional LLM context via JSON‑LD.

        Parameters
        ----------
        element : Component | str
            The visible FastHTML element. Can be an existing FT component or
            a raw HTML string.
        ctx : str
            Human‑authored context that should guide an LLM (e.g. tone,
            summary, hidden alt‑text). Keep it concise and *truthful.*
        role : str, default "summary"
            Free‑text label ("summary", "altText", "qa", …) – helps future
            renderers treat different context types differently.
        schema_type : str | None
            Optional schema.org @type to embed; if *None* we default to
            "WebPageElement".
    """
        json_ld = {
            "@context": "https://schema.org",
            "@type": self.schema_type or "WebPageElement",
            "role": self.role,
            "dateCreated": datetime.utcnow().isoformat(timespec="seconds") + "Z",
            "llmContext": self.ctx.strip(),
        }
        # Return a small fragment: <element> ... <script>JSON‑LD</script>
        return Group(
            self.element,
            NotStr(_script(json_ld)),
        )

# ---------------------------------------------------------------------------
# higher‑level helpers
# ---------------------------------------------------------------------------

@dataclass
class SemanticArticle:
    title: str
    sections: List[Dict[str, Any]]
    metadata: Dict[str, Any] | None = None

    def __ft__(self):
        schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": self.title,
            "articleSection": [s["heading"] for s in self.sections],
            **(self.metadata or {}),
        }
        art = [H1(self.title)]
        for sec in self.sections:
            lvl = sec.get("level", 2)
            art.append(H1(sec["heading"], level=lvl))
            art.append(Div(sec["content"], itemprop="articleBody"))
        container = Article(*art,
                            itemscope=True,
                            itemtype="https://schema.org/Article")
                            # Convert the FT tree to real markup
        html_body = to_xml(container)
        return NotStr(_script(schema) + html_body)


@dataclass
class FAQOptimizer:
    qa_pairs: List[Tuple[str, str]]

    def __ft__(self):
        schema = {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
                for q, a in self.qa_pairs
            ],
        }
        html = [Div(H3(q), Div(a, cls="faq-answer"), cls="faq-item") for q, a in self.qa_pairs]
        faq_section = Section(*html, cls="faq")
        return NotStr(_script(schema) + to_xml(faq_section))

@dataclass
class TechnicalTermOptimizer:
    html: str
    glossary: Dict[str, str]

    def __ft__(self):
        soup = BeautifulSoup(self.html, "html.parser")
        for txt in soup.find_all(string=True):
            if txt.parent.name in {"script", "style"}: continue
            for term, desc in self.glossary.items():
                if term in txt:
                    span = Span(term,
                    cls="technical-term",
                    **{"data-definition": desc})
                    span_tag = BeautifulSoup(to_xml(span), "html.parser").span
                    before, _, after = txt.partition(term)
                    if before: txt.insert_before(before)
                    txt.insert_before(span_tag)
                    if after:  txt.replace_with(after)
                    else:      txt.extract() 
        gloss = Section(H2("Technical Glossary"), *[Dl(Dt(t), Dd(d)) for t, d in self.glossary.items()], id="glossary", cls="technical-glossary")
        if soup.body:
            soup.body.append(BeautifulSoup(to_xml(gloss), "html.parser"))
        schema = {
            "@context": "https://schema.org",
            "@type": "DefinedTermSet",
            "definedTerm": [{"@type": "DefinedTerm", "name": t, "description": d} for t, d in self.glossary.items()],
        }
        return NotStr(_script(schema) + str(soup))

@dataclass
class ContentChunker:
    html: str
    max_tokens: int = 500
    overlap: int = 50

    def __ft__(self):
        soup = BeautifulSoup(self.html, "html.parser")
        blocks = soup.find_all(["p", "li", "h1", "h2", "h3", "h4", "h5", "h6", "blockquote"])
        def est(t:str)->int: return max(1, len(t)//4)
        chunks, cur, tok = [[]], [], 0
        for b in blocks:
            t = est(b.get_text())
            if tok+t>self.max_tokens and cur:
                chunks[-1]=cur; cur = cur[-self.overlap:]; tok=sum(est(BeautifulSoup(c,'html.parser').get_text()) for c in cur); chunks.append([])
            cur.append(str(b)); tok += t
        chunks[-1]=cur if cur else chunks[-1]
        divs = [Div(NotStr("".join(c)), cls="content-chunk", **{"data-chunk-id": str(i)}) for i,c in enumerate(chunks)]
        return Div(*divs, cls="optimized-content")

@dataclass
class CitationOptimizer:
    html: str
    citations: List[Dict[str, Any]]

    def __ft__(self):
        soup = BeautifulSoup(self.html, "html.parser")
        for c in self.citations:
            cid = str(c["id"])
            for m in soup.find_all("span",
                                   class_="citation-marker",
                                   attrs={"data-citation-id": cid}):
                cite_html = f"<cite id='cite-{cid}'>[{cid}]</cite>"
                cite_tag  = BeautifulSoup(cite_html, "html.parser").cite
                m.replace_with(cite_tag)
        refs = [Li(f"{', '.join(c.get('authors', []))}. \"{c['title']}\". {c.get('publisher','')} {c.get('date','')} ", A(c['url'], href=c['url']) if c.get('url') else "") for c in self.citations]
        refs_html = to_xml(
            Section(H2("References"),
                Ol(*refs),
                    id="references", cls="references"))

                # BeautifulSoup may not have <body> if the fragment is just a div/p
        target = soup.body if soup.body else soup
        target.append(BeautifulSoup(refs_html, "html.parser"))
        schema = {
            "@context": "https://schema.org",
            "@type": "ScholarlyArticle",
            "citation": [
                {"@type": "CreativeWork", "name": c.get("title"), "author": c.get("authors", []), "publisher": c.get("publisher"), "datePublished": c.get("date"), "url": c.get("url")}
                for c in self.citations
            ],
        }
        return NotStr(_script(schema) + str(soup))

# ---------------------------------------------------------------------------
# diagnostic util
# ---------------------------------------------------------------------------

def information_density(text: str) -> float:
    tokens = text.split(); total=len(tokens); counts=Counter(tokens)
    return -sum((c/total)*math.log2(c/total) for c in counts.values())
