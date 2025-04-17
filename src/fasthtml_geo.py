from __future__ import annotations

import json
import math
import typing as _t
from collections import Counter
from datetime import datetime

from bs4 import BeautifulSoup  # type: ignore – install "beautifulsoup4"
from fasthtml import Component  # FastHTML base class

__all__ = [
    "to_json",
    "LLMBlock",
    "SemanticArticle",
    "FAQOptimizer",
    "TechnicalTermOptimizer",
    "ContentChunker",
    "CitationOptimizer",
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def to_json(obj: _t.Any) -> str:
    """This function convernts Python str's to JSON Strings"""
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))

# ---------------------------------------------------------------------------
# Core block – the low‑level primitive everything else builds on
# ---------------------------------------------------------------------------


class LLMBlock(Component):
    """Wrap *any* FT element and attach additional LLM context via JSON‑LD.

    This function takes any HTML and allows the user to add machine readable context to it via JSON-LD

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

    def __init__(
        self,
        element: _t.Union[Component, str],
        *,
        ctx: str,
        role: str = "summary",
        schema_type: str | None = None,
    ) -> None:
        self.element = element
        self.ctx = ctx.strip()
        self.role = role
        self.schema_type = schema_type or "WebPageElement"

    # FastHTML calls `render()` to get HTML
    def render(self) -> str: 
        visible = str(self.element)
        json_ld = {
            "@context": "https://schema.org",
            "@type": self.schema_type,
            "role": self.role,
            "dateCreated": datetime.utcnow().isoformat(timespec="seconds") + "Z",
            "llmContext": self.ctx,
        }
        script = (
            '<script type="application/ld+json">' + to_json(json_ld) + "</script>"
        )
        return visible + script


# ---------------------------------------------------------------------------
# GEO‑specific higher‑level components
# ---------------------------------------------------------------------------


class SemanticArticle(Component):
    """Full article wrapper with headline, sections & metadata.
    
    Creates JSON-LD schema for Article type
    Builds HTML structure with semantic elements
    Adds metadata as meta tags
    Returns the complete article markup

    """

    def __init__(
        self,
        *,
        title: str,
        sections: list[dict[str, _t.Any]],
        metadata: dict[str, _t.Any] | None = None,
    ) -> None:
        self.title = title
        self.sections = sections
        self.metadata = metadata or {}

    def render(self) -> str:
        schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": self.title,
            "articleSection": [s["heading"] for s in self.sections],
            **self.metadata,
        }
        html_parts: list[str] = [
            '<article itemscope itemtype="https://schema.org/Article">',
            f"  <h1 itemprop=\"headline\">{self.title}</h1>",
        ]
        if self.metadata:
            html_parts.append("  <div class=\"article-metadata\">")
            for k, v in self.metadata.items():
                html_parts.append(f"    <meta itemprop=\"{k}\" content=\"{v}\">")
            html_parts.append("  </div>")
        for sec in self.sections:
            lvl = sec.get("level", 2)
            html_parts.append("  <section>")
            html_parts.append(
                f"    <h{lvl} itemprop=\"about\">{sec['heading']}</h{lvl}>"
            )
            html_parts.append("    <div itemprop=\"articleBody\">" + sec["content"] + "</div>")
            html_parts.append("  </section>")
        html_parts.append("</article>")
        return '<script type="application/ld+json">' + to_json(schema) + "</script>" + "\n" + "\n".join(html_parts)


class FAQOptimizer(Component):
    """Question‑answer blocks with FAQPage schema.
    
    Takes a list of Q&A pairs and:

    Creates FAQPage schema
    Renders each Q&A as a div structure
    Assigns IDs for easier reference
    
    """

    def __init__(self, qa: list[tuple[str, str]]) -> None:
        self.qa = qa

    def render(self) -> str:
        schema = {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": q,
                    "acceptedAnswer": {"@type": "Answer", "text": a},
                }
                for q, a in self.qa
            ],
        }
        html = ["<section class=\"faq\">"]
        for i, (q, a) in enumerate(self.qa):
            html.extend(
                [
                    f"  <div class=\"faq-item\" id=\"faq-{i}\">",
                    f"    <h3 class=\"faq-question\">{q}</h3>",
                    f"    <div class=\"faq-answer\">{a}</div>",
                    "  </div>",
                ]
            )
        html.append("</section>")
        return '<script type="application/ld+json">' + to_json(schema) + "</script>\n" + "\n".join(html)


class TechnicalTermOptimizer(Component):
    """Auto‑annotate domain terms and append a glossary block."""

    def __init__(self, html: str, glossary: dict[str, str]):
        self.html = html
        self.glossary = glossary

    def render(self) -> str:
        soup = BeautifulSoup(self.html, "html.parser")
        # annotate occurrences
        for txt in soup.find_all(string=True):
            if txt.parent.name in {"script", "style"}:
                continue
            for term, desc in self.glossary.items():
                if term in txt:
                    span = soup.new_tag("span", **{"class": "technical-term", "data-definition": desc})
                    span.string = term
                    parts = txt.split(term)
                    new_frag = soup.new_tag("span")
                    new_frag.append(parts[0])
                    new_frag.append(span)
                    new_frag.append(parts[1])
                    txt.replace_with(new_frag)
        # build glossary section
        sec = soup.new_tag("section", id="glossary", **{"class": "technical-glossary"})
        sec.append(soup.new_tag("h2", string="Technical Glossary"))
        dl = soup.new_tag("dl")
        for term, desc in self.glossary.items():
            dl.append(soup.new_tag("dt", string=term))
            dl.append(soup.new_tag("dd", string=desc))
        sec.append(dl)
        soup.body.append(sec)
        # schema
        schema = {
            "@context": "https://schema.org",
            "@type": "DefinedTermSet",
            "definedTerm": [
                {"@type": "DefinedTerm", "name": t, "description": d}
                for t, d in self.glossary.items()
            ],
        }
        return '<script type="application/ld+json">' + to_json(schema) + "</script>\n" + str(soup)


class ContentChunker(Component):
    """Insert chunk divs every *N* tokens to aid LLM retrieval.
    
    Chunks content for better LLM retrieval:

    Estimates tokens using character count (rough approximation)
    Groups content blocks into chunks based on token count
    Adds overlap between chunks for context preservation
    Wraps each chunk in a div with a unique ID

    """

    def __init__(self, html: str, *, max_tokens: int = 500, overlap: int = 50):
        self.html = html
        self.max_tokens = max_tokens
        self.overlap = overlap

    def _estimate_tokens(self, text: str) -> int:
        return max(1, len(text) // 4)  # crude but cheap

    def render(self) -> str:
        soup = BeautifulSoup(self.html, "html.parser")
        blocks = soup.find_all(["p", "li", "h1", "h2", "h3", "h4", "h5", "h6", "blockquote"])
        chunks: list[list[str]] = [[]]
        tok_count = 0
        for blk in blocks:
            t = self._estimate_tokens(blk.get_text("", strip=True))
            if tok_count + t > self.max_tokens and chunks[-1]:
                # overlap
                carry = " ".join(chunks[-1][-self.overlap :])
                chunks.append([carry])
                tok_count = self._estimate_tokens(carry)
            chunks[-1].append(str(blk))
            tok_count += t
        html_chunks = [
            f'<div class="content-chunk" data-chunk-id="{i}">' + "".join(c) + "</div>"
            for i, c in enumerate(chunks)
        ]
        return "<div class=\"optimized-content\">" + "".join(html_chunks) + "</div>"


class CitationOptimizer(Component):
    """Embed machine‑readable citations and in‑page reference list."""

    def __init__(self, html: str, citations: list[dict[str, _t.Any]]):
        self.html = html
        self.citations = citations

    def render(self) -> str:
        soup = BeautifulSoup(self.html, "html.parser")
        # replace <span class="citation-marker" data-citation-id="X"> with <cite>…</cite>
        for cite in self.citations:
            cid = cite["id"]
            for marker in soup.find_all("span", class_="citation-marker", attrs={"data-citation-id": str(cid)}):
                cite_tag = soup.new_tag("cite", id=f"cite-{cid}", itemscope="", itemtype="https://schema.org/CreativeWork")
                cite_tag.string = f"[{cid}]"
                marker.replace_with(cite_tag)
        # reference list
        ref_sec = soup.new_tag("section", id="references", **{"class": "references"})
        ref_sec.append(soup.new_tag("h2", string="References"))
        ol = soup.new_tag("ol")
        for c in self.citations:
            li = soup.new_tag("li", id=f"ref-{c['id']}")
            txt = ", ".join(c.get("authors", [])) + ". \"" + c.get("title", "") + "\". " + c.get("publisher", "")
            if "date" in c:
                txt += " " + c["date"] + ". "
            if url := c.get("url"):
                a = soup.new_tag("a", href=url)
                a.string = url
                li.append(txt)
                li.append(a)
            else:
                li.string = txt
            ol.append(li)
        ref_sec.append(ol)
        soup.body.append(ref_sec)
        # JSON‑LD
        schema = {
            "@context": "https://schema.org",
            "@type": "ScholarlyArticle",
            "citation": [
                {
                    "@type": "CreativeWork",
                    "name": c.get("title"),
                    "author": c.get("authors", []),
                    "publisher": c.get("publisher"),
                    "datePublished": c.get("date"),
                    "url": c.get("url"),
                }
                for c in self.citations
            ],
        }
        return '<script type="application/ld+json">' + to_json(schema) + "</script>\n" + str(soup)


# ---------------------------------------------------------------------------
# Simple information‑density helper (exposed for debugging)
# ---------------------------------------------------------------------------

def information_density(text: str) -> float:
    """Return Shannon entropy / token – diagnostic only."""
    tokens = text.split()
    total = len(tokens)
    counts = Counter(tokens)
    entropy = -sum((c / total) * math.log2(c / total) for c in counts.values())
    return entropy
