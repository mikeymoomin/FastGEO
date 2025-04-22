# fasthtml_geo

**Generative Engine Optimization for FastHTML Applications**

`fasthtml_geo` extends [FastHTML](https://github.com/fasthtml/fasthtml) with tools for optimizing your content for both traditional search engines and next-generation AI-powered search experiences (Generative Engine Optimization).

## What is GEO?

Generative Engine Optimization (GEO) is the practice of structuring web content to be better understood by Large Language Models (LLMs) that power modern search engines and AI assistants. While SEO focuses on keywords and technical elements, GEO emphasizes semantic structure, context, and machine-readable metadata.

This library bridges the gap between traditional SEO and emerging GEO requirements, helping you create content that's optimized for both humans and machines.

## Installation

```bash
pip install fasthtml-geo
```

## Key Components

### LLMBlock

Attaches hidden context to HTML elements specifically for LLMs to better understand your content.

```python
from fasthtml_geo import LLMBlock

# Basic usage
element = LLMBlock(
    P("Hello World!"), 
    "Friendly greeting in page header"
)
```

### SemanticArticle

Structures articles with proper schema.org markup for enhanced discoverability.

```python
from fasthtml_geo import SemanticArticle

sections = [
    {"heading": "Introduction", "content": P("Generative engines..."), "level": 2},
    {"heading": "Why GEO?", "content": P("LLMs rank semantics, not keywords."), "level": 2},
]

article = SemanticArticle(
    title="GEO in a Nutshell",
    sections=sections,
    metadata={"author": "Jane Dev", "datePublished": "2025-04-17"},
)
```

### FAQOptimizer

Transforms FAQ content into schema.org format for better search engine visibility and rich results.

```python
from fasthtml_geo import FAQOptimizer

qa_pairs = [
    ("What is GEO?", "Optimizing pages so LLM-driven search surfaces them."),
    ("Does GEO replace SEO?", "No – they complement each other."),
]

faq = FAQOptimizer(qa_pairs=qa_pairs)
```

### TechnicalTermOptimizer

Highlights and defines technical terms with semantic markup and glossaries.

```python
from fasthtml_geo import TechnicalTermOptimizer

content = P("Transformers rely on self-attention for sequence modeling.")
terms = {
    "transformer": "Neural network architecture based on attention.",
    "self-attention": "Mechanism where each token attends to all others.",
}

glossary = TechnicalTermOptimizer(content, glossary=terms)
```

### ContentChunker

Splits content into optimized chunks for better LLM processing, which can help with handling long-form content.

```python
from fasthtml_geo import ContentChunker

# Create some content
body_components = Group(
    P("Lorem ipsum dolor sit amet, consectetur adipiscing elit."),
    P("Vivamus vitae ligula in elit porttitor egestas."),
    H3("A Subheading"),
    Ul(Li("First item."), Li("Second item."), Li("Third item.")),
)

# Create chunks
chunked_content = ContentChunker(body_components, max_tokens=500, overlap=50)
```

### CitationOptimizer

Transforms citations into semantic markup for academic and reference content.

```python
from fasthtml_geo import CitationOptimizer, CitationBibliography

citations = [
    {
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
    }
]

# Add citation references in the text
content_with_citation = CitationOptimizer(
    P("Deep learning has revolutionized NLP."), 
    1, 
    citations
)

# Add bibliography at the end of your document
bibliography = CitationBibliography(citations)
```

## Demo Application

The library includes a demo application in `examples/trial.py` that showcases each component. Run it locally to see examples in action:

```bash
python examples/trial.py
```

This will start a local server with interactive examples of each component.

## Why Use fasthtml_geo?

- **Future-proof content**: Optimize for both traditional and AI-powered search engines
- **Enhanced content understanding**: Help LLMs better comprehend your content's structure and meaning
- **Rich metadata**: Provide context that improves how your content is processed and represented
- **Improved discoverability**: Make your content more findable in the age of generative search
- **SEO compatibility**: All optimizations maintain or enhance traditional SEO benefits

## Utility Functions

### information_density

Calculates the information density of a text, which can be useful for optimizing content:

```python
from fasthtml_geo import information_density

score = information_density("Your text here")
print(f"Information density score: {score}")
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.