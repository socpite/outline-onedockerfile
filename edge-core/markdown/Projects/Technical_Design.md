# Technical Design

# Search Rewrite — Technical Design

## 🧱 System Overview

The rewritten search stack will consist of:

* **Indexer Service** (Go): Listens to Kafka events and syncs with ElasticSearch.
* **Query Router** (Node): Parses search queries and forwards to appropriate ranking engine.
* **Ranking Layer** (Python): Modular scorer pipeline, pluggable feature transforms.

## 🔌 Architecture Diagram

```mermaidjs
graph TD
  A[Kafka Event Stream] --> B[Indexer Service - Go]
  B --> C[ElasticSearch v8]

  D[Client Query] --> E[Query Router - Node.js]
  E --> F[Ranking Layer - Python]

  subgraph Ranking Pipeline
    F1[Feature Extractor]
    F2[Business Rule Scorer]
    F3[Modular Scorers: Recency & Popularity]
    F4[Final Rank Composer]
    F --> F1 --> F2 --> F3 --> F4
  end

  F4 --> G[Search Results Returned]
```

## 🔧 Components

### Indexer

* Built in Go
* Kafka consumer
* ElasticSearch v8 optimized writes

### Ranking Layer

* Pluggable scorers (e.g., recency, popularity, match quality)
* Simple DSL for business rule overrides
* Integration tests + offline scoring eval suite

## 🧪 Testing Strategy

* Unit & integration tests per component
* Load test comparison vs legacy system
* Shadow traffic analysis

## 🛡 Risks & Mitigations

* **Risk**: A/B test degrades search CTR 
* **Mitigation**: Gradual rollout + kill switch

  \
* **Risk**: Latency regression on mobile 
* **Mitigation**: Precompute hot queries + edge caching