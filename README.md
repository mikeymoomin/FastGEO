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

#### Output:

```html
<img src="cat.jpg" alt="A cat"/>
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "WebPageElement",
  "role": "image-description",
  "dateCreated": "2025-01-23T12:00:00Z",
  "llmContext": "A playful tabby cat sitting on a windowsill"
}
</script>
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

#### Output:

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "How to Train Your Dragon",
  "articleSection": ["Introduction", "Training Steps"],
  "author": "John Doe",
  "datePublished": "2025-01-23"
}
</script>
<article itemscope itemtype="https://schema.org/Article">
  <h1 itemprop="headline">How to Train Your Dragon</h1>
  <div class="article-metadata">
    <meta itemprop="author" content="John Doe">
    <meta itemprop="datePublished" content="2025-01-23">
  </div>
  <section>
    <h2 itemprop="about">Introduction</h2>
    <div itemprop="articleBody">Dragons are awesome...</div>
  </section>
  <section>
    <h2 itemprop="about">Training Steps</h2>
    <div itemprop="articleBody">First, gain trust...</div>
  </section>
</article>
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

#### Output:


```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "What is Python?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Python is a programming language..."
      }
    },
    {
      "@type": "Question",
      "name": "Is it hard to learn?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "No, Python is beginner-friendly..."
      }
    }
  ]
}
</script>
<section class="faq">
  <div class="faq-item" id="faq-0">
    <h3 class="faq-question">What is Python?</h3>
    <div class="faq-answer">Python is a programming language...</div>
  </div>
  <div class="faq-item" id="faq-1">
    <h3 class="faq-question">Is it hard to learn?</h3>
    <div class="faq-answer">No, Python is beginner-friendly...</div>
  </div>
</section>
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

#### Output:
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "DefinedTermSet",
  "definedTerm": [
    {
      "@type": "DefinedTerm",
      "name": "machine learning",
      "description": "AI that learns from data"
    },
    {
      "@type": "DefinedTerm",
      "name": "predictions",
      "description": "Forecasting future outcomes"
    }
  ]
}
</script>
<p>We use <span class="technical-term" data-definition="AI that learns from data">machine learning</span> for <span class="technical-term" data-definition="Forecasting future outcomes">predictions</span>.</p>
<section id="glossary" class="technical-glossary">
  <h2>Technical Glossary</h2>
  <dl>
    <dt>machine learning</dt>
    <dd>AI that learns from data</dd>
    <dt>predictions</dt>
    <dd>Forecasting future outcomes</dd>
  </dl>
</section>
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

#### Output: 

```html
<div class="optimized-content">
  <div class="content-chunk" data-chunk-id="0">
    <p>This is the first paragraph.</p>
    <p>This is the second paragraph.</p>
  </div>
  <div class="content-chunk" data-chunk-id="1">
    <p>This is the second paragraph.</p>
    <p>This is the third paragraph.</p>
  </div>
  <div class="content-chunk" data-chunk-id="2">
    <p>This is the third paragraph.</p>
    <p>This is the fourth paragraph.</p>
  </div>
</div>
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

#### Output:

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "ScholarlyArticle",
  "citation": [
    {
      "@type": "CreativeWork",
      "name": "AI Research",
      "author": ["Jane Smith"],
      "publisher": "Science Journal",
      "datePublished": "2025",
      "url": "https://example.com/ai"
    }
  ]
}
</script>
<p>AI is transforming technology <cite id="cite-1" itemscope itemtype="https://schema.org/CreativeWork">[1]</cite>.</p>
<section id="references" class="references">
  <h2>References</h2>
  <ol>
    <li id="ref-1">Jane Smith. "AI Research". Science Journal 2025. <a href="https://example.com/ai">https://example.com/ai</a></li>
  </ol>
</section>
```

## Installation

1. Install dependencies:
```bash
pip install fasthtml beautifulsoup4
```

2. Copy the library to your project

## Quick Start

```python
from fasthtml_geo import LLMBlock, SemanticArticle, FAQOptimizer

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