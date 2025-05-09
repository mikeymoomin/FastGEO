"""fasthtml_geo 
====================================
This library provides helpers for structuring and enhancing HTML content,
particularly with an eye towards search engine optimization (SEO) and
providing context for large language models (LLMs).

It follows the FastHTML extension pattern using dataclasses with a `__ft__`
method to generate HTML, often including embedded JSON-LD for semantic
markup. Raw HTML is wrapped with `NotStr` to prevent FastHTML from escaping it.
"""

from __future__ import annotations

import json, math
from dataclasses import dataclass
from datetime import datetime
from collections import Counter
from typing import Any, Union, List, Dict, Tuple, ClassVar

from bs4 import BeautifulSoup, Tag
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
    """
    **LLMBlock**

    Wraps a visible HTML element (created by FastHTML or raw HTML) and
    attaches hidden context specifically intended for Large Language Models
    (LLMs) via an embedded JSON-LD `<script>` tag.

    This is useful for providing nuances, summaries, alternative descriptions
    (like enhanced alt-text), or other non-visual information about a
    specific part of the content.

    **Parameters:**

    * **`element`** (`Any`):
        The FastHTML component or raw HTML string that you want to provide
        context for. This is the visible part of the output.
    * **`ctx`** (`str`):
        A string containing the human-authored context for the LLM. This
        should be concise, accurate, and guide the LLM's understanding
        or processing of the associated `element`.
    * **`role`** (`str`, optional, default="summary"):
        A free-text label indicating the *type* of context being provided
        (e.g., "summary", "altText", "qa", "explanation"). This helps potential
        tools or renderers interpret and use the `ctx` appropriately.
    * **`schema_type`** (`str | None`, optional, default=`None`):
        Specifies the schema.org `@type` for the JSON-LD block. If `None`,
        it defaults to "WebPageElement", suitable for wrapping arbitrary
        HTML blocks. You might specify other types if the element represents
        something more specific (e.g., "ImageObject" for an image).

    **Returns:**

    A FastHTML `Group` containing the original `element` followed immediately
    by a `<script type="application/ld+json">` tag with the embedded context.
    The JSON-LD includes the provided context (`llmContext`), role, schema type,
    and a timestamp (`dateCreated`).
    """
    element: Any         
    ctx: str
    role: str = "summary"
    schema_type: str | None = None

    def __ft__(self):
        json_ld = {
            "@context": "https://schema.org",
            "@type": self.schema_type or "WebPageElement",
            "role": self.role,
            "dateCreated": datetime.utcnow().isoformat(timespec="seconds") + "Z",
            "llmContext": self.ctx.strip(),
        }
        return Group(
            self.element,
            NotStr(_script(json_ld)),
        )

# ---------------------------------------------------------------------------
# higher‑level helpers
# ---------------------------------------------------------------------------

@dataclass
class SemanticArticle:
    """
    **SemanticArticle**

    Structures content as a schema.org `Article`, generating appropriate HTML
    elements (`<h1>`, `<article>`, `<div>` for sections) and embedding
    the corresponding schema.org JSON-LD metadata in a `<script>` tag.

    This helps search engines and other systems understand the structure and
    topic of your content, potentially improving its visibility and
    interpretation.

    **Parameters:**

    * **`title`** (`str`):
        The main headline or title of the article. Used for the `<h1>` tag
        and the `headline` property in the JSON-LD.
    * **`sections`** (`List[Dict[str, Any]]`):
        A list of dictionaries, where each dictionary represents a section of
        the article. Each dictionary should contain:
        * `"heading"` (`str`): The title of the section. Used for a heading
            tag (`<h2>` by default, adjustable with `"level"`). Also used in
            the `articleSection` list in the JSON-LD.
        * `"content"` (`Any`): The FastHTML component(s) or raw HTML for
            the content of the section. Wrapped in a `<div>` with `itemprop="articleBody"`.
        * `"level"` (`int`, optional, default=2): The heading level for the
            section heading (e.g., 2 for `<h2>`, 3 for `<h3>`, etc.).
    * **`metadata`** (`Dict[str, Any] | None`, optional, default=`None`):
        An optional dictionary of additional schema.org properties to include
        in the Article JSON-LD (e.g., `author`, `datePublished`, `image`, etc.).
        These will be merged into the main schema dictionary.

    **Returns:**

    A FastHTML `NotStr` containing the rendered HTML structure of the article
    (`<h1>`, `<article>` with sections) immediately followed by the
    schema.org Article JSON-LD `<script>` tag.
    """
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
        html_body = to_xml(container)
        return NotStr(_script(schema) + html_body)


@dataclass
class FAQOptimizer:
    """
    **FAQOptimizer**

    Structures a list of Question and Answer pairs, generating HTML for
    display and embedding schema.org `FAQPage` JSON-LD metadata.

    This is highly recommended for pages containing Frequently Asked Questions
    as it helps search engines display your Q&A content directly in search results
    (e.g., as rich snippets or FAQ schema).

    **Parameters:**

    * **`qa_pairs`** (`List[Tuple[str, str]]`):
        A list of tuples, where each tuple contains two strings: the question
        and its corresponding answer. Example: `[("What is FastHTML?", "A Python web framework."), ...]`.

    **Returns:**

    A FastHTML `NotStr` containing HTML (`<section>`, `<div>`, `<h3>`)
    representing the Q&A pairs, immediately followed by the schema.org
    `FAQPage` JSON-LD `<script>` tag.
    """
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
    """
    **TechnicalTermOptimizer**

    Takes existing HTML content and a glossary of technical terms with their
    definitions. It processes the HTML to:

    1.  Wrap occurrences of glossary terms with a `<span>` element containing
        the class `technical-term` and a `data-definition` attribute holding
        the term's definition. This allows front-end scripts to easily
        create tooltips or popovers for definitions.
    2.  Embed schema.org `DefinedTermSet` JSON-LD containing the glossary.
        This helps search engines understand the specific terms and
        definitions used on the page.

    Note that this class operates on the rendered HTML string of the input
    `element` using BeautifulSoup, rather than modifying the FastHTML
    component tree directly.

    **Parameters:**

    * **`element`** (`Any`):
        The FastHTML component or raw HTML string whose content you want to
        process for technical terms.
    * **`glossary`** (`Dict[str, str]`):
        A dictionary mapping technical terms (strings) to their definitions
        (strings). Occurrences of the dictionary *keys* within the text nodes
        of the `element` will be wrapped.

    **Returns:**

    A FastHTML `NotStr` containing the modified HTML with terms wrapped in
    `<span>` tags and the schema.org `DefinedTermSet` JSON-LD `<script>` tag
    appended.
    """
    element: Any  
    glossary: Dict[str, str]  

    def __ft__(self):
        html_body = to_xml(self.element)
        soup = BeautifulSoup(html_body, "html.parser")

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

        schema = {
            "@context": "https://schema.org",
            "@type": "DefinedTermSet",
            "definedTerm": [
                {"@type": "DefinedTerm", "name": t, "description": d}
                for t, d in self.glossary.items()
            ],
        }

        return NotStr(_script(schema) + str(soup))


@dataclass
class ContentChunker:
    """
    **ContentChunker**

    Breaks down a block of HTML content into smaller `<div>` "chunks" based on
    an estimated token limit. Each chunk is wrapped in a `<div>` with classes
    `content-chunk` and `optimized-content chunked-view`, and a `data-chunk-id`.

    This is useful for processing large articles or documents for tasks like
    summarization, analysis, or question answering using LLMs, where input size
    limits are a concern. It attempts to chunk based on logical block elements
    like paragraphs and headings.

    **Parameters:**

    * **`html`** (`str`):
        The input HTML content as a string that needs to be chunked.
    * **`max_tokens`** (`int`, optional, default=500):
        The maximum estimated number of tokens allowed per chunk. Token
        estimation is a simple word count (`len(text.split())`). This is an
        approximation and may not precisely match LLM tokenizers.
    * **`overlap`** (`int`, optional, default=50):
        The number of *elements* (paragraphs, list items, etc.) from the end
        of one chunk to include at the beginning of the next. This helps retain
        context across chunk boundaries. Note: This is element count, not token count overlap.

    **Returns:**

    A FastHTML `Div` containing nested `Div` elements, where each inner `Div`
    represents a content chunk. Each chunk `Div` includes CSS classes
    `content-chunk optimized-content chunked-view` and a `data-chunk-id`
    attribute. The HTML content within each chunk is included as a `NotStr`.
    """
    html: str
    max_tokens: int = 500
    overlap: int = 50

    def __ft__(self):
        raw_html_string = to_xml(self.html)
        soup = BeautifulSoup(raw_html_string, "html.parser")
        blocks = soup.find_all(["p", "li", "h1", "h2", "h3", "h4", "h5", "h6", "blockquote"])
        def est(text: str) -> int:
            return max(1, len(text.split()))
        chunks = []  
        cur: List[Tuple[str, int]] = []
        tok = 0 
        for b in blocks:
            block_html = str(b)
            block_text = b.get_text(strip=True)
            if not block_text: continue

            t = est(block_text)

            if tok + t > self.max_tokens and cur:
                chunks.append([item[0] for item in cur]) 

                overlap_elements = cur[-self.overlap:]
                tok = sum(item[1] for item in overlap_elements)
                cur = overlap_elements
                if not cur: tok = 0
                
            cur.append((block_html, t))
            tok += t

        if cur:
            chunks.append([item[0] for item in cur])

        divs = [
            Div(NotStr("".join(c)), cls="content-chunk", **{"data-chunk-id": str(i)})
            for i, c in enumerate(chunks) if c
        ]
        return Div(*divs, cls="optimized-content chunked-view")

@dataclass
class CitationOptimizer:
    """
    Inserts a sequential <cite>[n]</cite> for a single citation,
    and accumulates its metadata for the final bibliography.
    """
    element: Any                       
    citation_id: Any                   
    cite_list: List[Dict[str, Any]]  

    _order_map: ClassVar[Dict[str, int]] = {}
    _processed: ClassVar[List[Dict[str, Any]]] = []
    _counter: ClassVar[int] = 0

    def __post_init__(self):
        matches = [c for c in self.cite_list if c["id"] == self.citation_id]
        if not matches:
            raise ValueError(f"Citation ID {self.citation_id!r} not found")
        self.citation = matches[0]

    def __ft__(self):
        html_body = to_xml(self.element)
        soup = BeautifulSoup(html_body, "html.parser")

        cid = str(self.citation["id"])
        marker = soup.find("span", class_="citation-marker", attrs={"data-citation-id": cid})
        if not marker:
            parent = soup.find("p") or (soup.body or soup)
            marker = BeautifulSoup(
                f'<span class="citation-marker" data-citation-id="{cid}"></span>',
                "html.parser"
            ).span
            parent.append(marker)

        if cid not in type(self)._order_map:
            type(self)._counter += 1
            type(self)._order_map[cid] = type(self)._counter
            type(self)._processed.append(self.citation)

        seq = type(self)._order_map[cid]
        cite_tag = soup.new_tag("cite", id=f"cite-{cid}")
        cite_tag.string = f"[{seq}]"
        marker.replace_with(cite_tag)

        return NotStr(str(soup))


@dataclass
class CitationBibliography:
    """
    Once you’ve in‑lined all of your citations with CitationInline,
    add this at the very end to render ONE References section + JSON‑LD.
    """
    cite_list: List[Dict[str, Any]]    

    def __ft__(self):
        items = []
        for cited in CitationOptimizer._processed:
            auth = ", ".join(cited.get("authors", []))
            title = cited["title"]
            pub = cited.get("publisher", "")
            date = cited.get("date", "")
            url = cited.get("url", "")
            text = f'{auth}. "{title}". {pub} {date}'
            li = Li(text, A(url, href=url) if url else None)
            items.append(li)

        refs_section = Section(
            H2("References"),
            Ol(*items),
            id="references", cls="references"
        )
        schema = {
            "@context": "https://schema.org",
            "@type": "ScholarlyArticle",
            "citation": [
                {
                    "@type": "CreativeWork",
                    "name": c["title"],
                    "author": c.get("authors", []),
                    "publisher": c.get("publisher"),
                    "datePublished": c.get("date"),
                    "url": c.get("url")
                }
                for c in CitationOptimizer._processed
            ],
        }

        return NotStr(
            to_xml(refs_section)
            + _script(schema)
        )
    

# ---------------------------------------------------------------------------
# diagnostic util
# ---------------------------------------------------------------------------

def information_density(text: str) -> float:
    tokens = text.split(); total=len(tokens); counts=Counter(tokens)
    return -sum((c/total)*math.log2(c/total) for c in counts.values())
