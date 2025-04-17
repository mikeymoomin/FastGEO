# SEO & LLM Optimizer for FastHTML

This library helps you make your website more discoverable by search engines (SEO) and AI systems (LLM EO) while using FastHTML.

## What does it do?

It adds special machine-readable data to your website that is invisible to visitors but helps:
- Search engines better understand your content (better rankings)
- AI systems better understand your content (better responses)

## Components Overview

### 1. LLMBlock - The Building Block

Wraps any HTML element and adds hidden context for AI systems.

```python
# Example: Add context to an image
image = LLMBlock(
    Img(src="cat.jpg", alt="A cat"),  # Your regular HTML element
    ctx="A playful tabby cat sitting on a windowsill",  # Hidden context for AI
    role="image-description"
)
```

### 2. SemanticArticle - For Blog Posts/Articles

Creates properly structured articles that search engines love.

```python
# Example: Create an article
article = SemanticArticle(
    title="How to Train Your Dragon",
    sections=[
        {"heading": "Introduction", "content": "Dragons are awesome..."},
        {"heading": "Training Steps", "content": "First, gain trust..."}
    ],
    metadata={"author": "John Doe", "datePublished": "2025-01-23"}
)
```

### 3. FAQOptimizer - For Q&A Pages

Creates FAQ pages that can show up as rich snippets in Google.

```python
# Example: Create FAQ section
faq = FAQOptimizer([
    ("What is Python?", "Python is a programming language..."),
    ("Is it hard to learn?", "No, Python is beginner-friendly...")
])
```

### 4. TechnicalTermOptimizer - For Technical Content

Highlights technical terms and creates a glossary.

```python
# Example: Add technical terms and definition
html_content = "<p>We use machine learning for predictions.</p>"
glossary = {
    "machine learning": "AI that learns from data",
    "predictions": "Forecasting future outcomes"
}
optimized = TechnicalTermOptimizer(html_content, glossary)
```

### 5. ContentChunker - For Long Content

Breaks long content into manageable pieces for AI systems.

```python
# Example: Chunk a long article
chunker = ContentChunker(
    html_content,
    max_tokens=500,  # Each chunk will be ~500 tokens
    overlap=50       # Chunks will share 50 tokens for context
)
```

### 6. CitationOptimizer - For Academic/Research Content

Handles citations and creates reference lists.

```python
# Example: Add citations to content
citations = [
    {
        "id": 1,
        "authors": ["Jane Smith"],
        "title": "AI Research",
        "publisher": "Science Journal",
        "date": "2025"
    }
]
optimizer = CitationOptimizer(html_content, citations)
```

## Installation

1. Install dependencies:
```bash
pip install fasthtml beautifulsoup4
```

2. Copy the library to your project

## Quick Start

```python
from seo_llm_optimizer import LLMBlock, SemanticArticle, FAQOptimizer

# Optimize a simple element
button = LLMBlock(
    Button("Click me"),
    ctx="Button for submitting the contact form"
)

# Create an SEO-optimized article
article = SemanticArticle(
    title="My First Article",
    sections=[{"heading": "Introduction", "content": "This is my article..."}]
)

# Add FAQs to your page
faq = FAQOptimizer([
    ("How do I start?", "First, install the library..."),
    ("Is it free?", "Yes, it's open source...")
])
```

## Best Practices

1. Keep context descriptions short and accurate
2. Use proper headings and semantic HTML
3. Don't overuse technical terms
4. Test your markup with Google's Rich Results test
5. Keep chunks at reasonable sizes (300-800 tokens)

## Need Help?

- Read the code comments for more details
- Check schema.org for markup specifications
- Test your results with Google Search Console