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

from bs4 import BeautifulSoup 
from fasthtml.common import * 

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
    element: Any  # FT component or raw HTML
    glossary: Dict[str, str]  # term -> definition

    def __ft__(self):
        # Render the FT element or raw HTML to a string
        html_body = to_xml(self.element)
        soup = BeautifulSoup(html_body, "html.parser")

        # Wrap each term occurrence with a <span> and add data-definition
        for txt in soup.find_all(string=True):
            if txt.parent.name in {"script", "style"}:
                continue
            for term, desc in self.glossary.items():
                if term in txt:
                    span = Span(term, cls="technical-term", **{"data-definition": desc})
                    span_tag = BeautifulSoup(to_xml(span), "html.parser").span
                    before, _, after = txt.partition(term)
                    if before:
                        txt.insert_before(before)
                    txt.insert_before(span_tag)
                    if after:
                        txt.replace_with(after)
                    else:
                        txt.extract()

        # Generate JSON-LD for the glossary (no visible glossary rendered)
        schema = {
            "@context": "https://schema.org",
            "@type": "DefinedTermSet",
            "definedTerm": [
                {"@type": "DefinedTerm", "name": t, "description": d}
                for t, d in self.glossary.items()
            ],
        }

        # Return enriched HTML plus embedded JSON-LD only
        return NotStr(_script(schema) + str(soup))


@dataclass
class ContentChunker:
    html: str
    max_tokens: int = 500
    overlap: int = 50

    def __ft__(self):
        soup = BeautifulSoup(self.html, "html.parser")
        blocks = soup.find_all(["p", "li", "h1", "h2", "h3", "h4", "h5", "h6", "blockquote"])
        def est(text: str) -> int:
            return max(1, len(text.split()))
        chunks = []  
        cur: List[Tuple[str, int]] = []
        tok = 0 
        for b in blocks:
            block_html = str(b)
            block_text = b.get_text(strip=True)
            if not block_text: continue # Skip empty blocks

            t = est(block_text)

            # If adding the current block exceeds the limit, finalize the current chunk
            if tok + t > self.max_tokens and cur:
                chunks.append([item[0] for item in cur]) # Store HTML strings only

                # Calculate overlap: take the last `overlap` *elements*
                overlap_elements = cur[-self.overlap:]
                # Recalculate token count for the overlap elements
                tok = sum(item[1] for item in overlap_elements)
                # Start the new chunk with the overlapping elements
                cur = overlap_elements
                # Ensure we don't start with zero tokens if overlap exists
                if not cur: tok = 0
                
            # Add the current block to the current chunk list
            cur.append((block_html, t))
            tok += t

        # Add the last chunk if it has content
        if cur:
            chunks.append([item[0] for item in cur])

        # Create the final Div structure
        divs = [
            Div(NotStr("".join(c)), cls="content-chunk", **{"data-chunk-id": str(i)})
            for i, c in enumerate(chunks) if c # Ensure chunk is not empty
        ]
        return Div(*divs, cls="optimized-content chunked-view")

@dataclass
class CitationOptimizer:
    element: Any  # FT component or raw HTML
    citations: List[Dict[str, Any]]  # List of citation metadata dicts

    def __ft__(self):
        # Serialize the FT component (or raw HTML) to a string
        html_body = to_xml(self.element)
        soup = BeautifulSoup(html_body, "html.parser")
        # Determine insertion target (body if present)
        target = soup.body if soup.body else soup

        # Auto-insert span markers if the user did not provide any
        for c in self.citations:
            cid = str(c["id"])
            if not soup.find(
                "span", class_="citation-marker", attrs={"data-citation-id": cid}
            ):
                marker_html = f'<span class="citation-marker" data-citation-id="{cid}"></span>'
                marker_tag = BeautifulSoup(marker_html, "html.parser").span
                target.append(marker_tag)

        # Replace all markers with proper <cite> elements
        for c in self.citations:
            cid = str(c["id"])
            for m in soup.find_all(
                "span", class_="citation-marker", attrs={"data-citation-id": cid}
            ):
                cite_html = f"<cite id='cite-{cid}'>[{cid}]</cite>"
                cite_tag = BeautifulSoup(cite_html, "html.parser").cite
                m.replace_with(cite_tag)

        # Build the references list
        refs = [
            Li(
                f"{', '.join(c.get('authors', []))}. \"{c['title']}\". {c.get('publisher','')} {c.get('date','')}",
                A(c['url'], href=c['url']) if c.get('url') else None
            )
            for c in self.citations
        ]
        refs_section = to_xml(
            Section(
                H2("References"),
                Ol(*refs),
                id="references", cls="references"
            )
        )
        target.append(BeautifulSoup(refs_section, "html.parser"))

        # Generate JSON-LD
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
                    "url": c.get("url")
                }
                for c in self.citations
            ],
        }

        # Return the enriched HTML plus embedded schema
        return NotStr(_script(schema) + str(soup))

# ---------------------------------------------------------------------------
# diagnostic util
# ---------------------------------------------------------------------------

def information_density(text: str) -> float:
    tokens = text.split(); total=len(tokens); counts=Counter(tokens)
    return -sum((c/total)*math.log2(c/total) for c in counts.values())
