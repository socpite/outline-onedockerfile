# Guide — Local Dev Setup

## 🛠 Requirements

* Node.js 20.x
* Python 3.11
* Docker + Docker Compose
* Redis, Postgres (local)

## 🚧 Setup Steps

```bash
git clone git@github.com:org/repo.git
cd repo
make bootstrap
make dev
```

## 🔌 Services

* `localhost:3000` — Frontend
* `localhost:4000` — GraphQL API
* `localhost:9200` — Elastic
* `localhost:5432` — Postgres (dev DB)

## 🧪 Testing

```bash
make test    # all unit tests
make lint    # eslint + black
```

## 🧙 Common Issues

| Error | Fix |
|----|----|
| Port already in use | `lsof -i :3000` then `kill -9 PID` |
| DB connection failed | Check `.env` and restart Postgres |