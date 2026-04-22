# Embeddings

Text embeddings are numerical representations of text that enable measuring semantic similarity. This guide introduces embeddings, their applications, and how to use embedding models for tasks like search, recommendations, and anomaly detection.

## Before implementing embeddings

When selecting an embeddings provider, there are several factors you can consider depending on your needs and preferences:

- **Dataset size & domain specificity**: size of the model training dataset and its relevance to the domain you want to embed. Larger or more domain-specific data generally produces better in-domain embeddings
- **Inference performance**: embedding lookup speed and end-to-end latency. This is a particularly important consideration for large scale production deployments
- **Customization**: options for continued training on private data, or specialization of models for very specific domains. This can improve performance on unique vocabularies

## How to get embeddings with Anthropic

Anthropic does not offer its own embedding model. One embeddings provider that has a wide variety of options and capabilities encompassing all of the above considerations is Voyage AI.

Voyage AI makes state-of-the-art embedding models and offers customized models for specific industry domains such as finance and healthcare, or bespoke fine-tuned models for individual customers.

The rest of this guide is for Voyage AI, but you should assess a variety of embeddings vendors to find the best fit for your specific use case.

## Available Models

Voyage recommends using the following text embedding models:

| Model | Context Length | Embedding Dimension | Description |
|---|---|---|---|
| voyage-3-large | 32,000 | 1024 (default), 256, 512, 2048 | The best general-purpose and multilingual retrieval quality. |
| voyage-3.5 | 32,000 | 1024 (default), 256, 512, 2048 | Optimized for general-purpose and multilingual retrieval quality. |
| voyage-3.5-lite | 32,000 | 1024 (default), 256, 512, 2048 | Optimized for latency and cost. |
| voyage-code-3 | 32,000 | 1024 (default), 256, 512, 2048 | Optimized for code retrieval. |
| voyage-finance-2 | 32,000 | 1024 | Optimized for finance retrieval and RAG. |
| voyage-law-2 | 16,000 | 1024 | Optimized for legal and long-context retrieval and RAG. |

Additionally, the following multimodal embedding models are recommended:

| Model | Context Length | Embedding Dimension | Description |
|---|---|---|---|
| voyage-multimodal-3 | 32000 | 1024 | Rich multimodal embedding model that can vectorize interleaved text and content-rich images. |

## Getting started with Voyage AI

To access Voyage embeddings:

1. Sign up on Voyage AI's website
2. Obtain an API key
3. Set the API key as an environment variable for convenience:

```
export VOYAGE_API_KEY="<your secret key>"
```

### Voyage Python library

The voyageai package can be installed using the following command:

```
pip install -U voyageai
```

Then, you can create a client object and start using it to embed your texts:

```python
import voyageai

vo = voyageai.Client()
# This will automatically use the environment variable VOYAGE_API_KEY.
# Alternatively, you can use vo = voyageai.Client(api_key="<your secret key>")

texts = ["Sample text 1", "Sample text 2"]

result = vo.embed(texts, model="voyage-3.5", input_type="document")
print(result.embeddings[0])
print(result.embeddings[1])
```

result.embeddings will be a list of two embedding vectors, each containing 1024 floating-point numbers.

### Voyage HTTP API

You can also get embeddings by requesting Voyage HTTP API:

```shell
curl https://api.voyageai.com/v1/embeddings \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $VOYAGE_API_KEY" \
  -d '{
    "input": ["Sample text 1", "Sample text 2"],
    "model": "voyage-3.5"
  }'
```

### AWS Marketplace

Voyage embeddings are available on AWS Marketplace. Instructions for accessing Voyage on AWS are available in the Voyage AWS Marketplace documentation.

## Quickstart example

Suppose you have a small corpus of six documents to retrieve from:

```python
documents = [
    "The Mediterranean diet emphasizes fish, olive oil, and vegetables, believed to reduce chronic diseases.",
    "Photosynthesis in plants converts light energy into glucose and produces essential oxygen.",
    "20th-century innovations, from radios to smartphones, centered on electronic advancements.",
    "Rivers provide water, irrigation, and habitat for aquatic species, vital for ecosystems.",
    "Apple's conference call to discuss fourth fiscal quarter results and business updates is scheduled for Thursday, November 2, 2023 at 2:00 p.m. PT / 5:00 p.m. ET.",
    "Shakespeare's works, like 'Hamlet' and 'A Midsummer Night's Dream,' endure in literature.",
]
```

First, use Voyage to convert each document into an embedding vector:

```python
import voyageai

vo = voyageai.Client()

# Embed the documents
doc_embds = vo.embed(documents, model="voyage-3.5", input_type="document").embeddings
```

Given an example query, convert it into an embedding and conduct a nearest neighbor search:

```python
import numpy as np

query = "When is Apple's conference call scheduled?"

# Embed the query
query_embd = vo.embed([query], model="voyage-3.5", input_type="query").embeddings[0]

# Compute the similarity
# Voyage embeddings are normalized to length 1, therefore dot-product
# and cosine similarity are the same.
similarities = np.dot(doc_embds, query_embd)
retrieved_id = np.argmax(similarities)
print(documents[retrieved_id])
```

Note that input_type="document" and input_type="query" are used for embedding the document and query, respectively.

## Pricing

Visit Voyage's pricing page for the most up to date pricing details.
