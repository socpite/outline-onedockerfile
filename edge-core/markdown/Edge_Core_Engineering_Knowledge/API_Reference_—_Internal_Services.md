# API Reference — Internal Services

## 🔗 GraphQL API

### Query: `search(query: String): [Result]`

* **Input**: String
* **Output**: Title, Snippet, URL
* **Auth**: Required

### Mutation: `createFeatureFlag`

* Fields: name, enabled, targetUserIds

## 🌐 Internal REST APIs

### `GET /notifications/:userId`

* Auth via JWT
* Returns: array of message payloads

### `POST /indexer/rebuild`

* Use for backfill jobs
* Rate-limited via token bucket