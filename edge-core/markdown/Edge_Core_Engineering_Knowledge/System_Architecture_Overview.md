# System Architecture Overview

## 🧱 Core Components

* **Frontend (Next.js)**: Serves dynamic UI, SSR for SEO
* **Backend API (Node + GraphQL)**: Orchestrates data between services
* **Search Stack (Elastic + Ranking Service)**: Handles user queries
* **Jobs & Pipelines (Airflow + Redis)**: For ingestion and batch processing
* **Data Warehouse (Snowflake)**: Analytics and metrics
* **Infra (AWS + Terraform)**: Infra-as-code, ECS, RDS, S3

## 🌐 Data Flow


1. User hits FE ➝ FE fetches data via GraphQL ➝ Backend pulls from services
2. Events sent to Kafka ➝ Processed by consumers ➝ Indexed or warehoused

## 🗺 Diagram

*(Insert Mermaid or Lucidchart here)*

## 🧪 Testing Strategy

* Unit tests (Jest, Pytest)
* Integration tests via CI
* Load testing with k6

## 🔐 Security

* Secrets via AWS Parameter Store
* OAuth2 for internal tools