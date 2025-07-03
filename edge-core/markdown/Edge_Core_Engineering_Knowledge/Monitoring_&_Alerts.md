# Monitoring & Alerts

## 📊 Observability Stack

* **Datadog**: metrics + logs
* **PagerDuty**: alerting
* **Sentry**: FE & BE errors
* **Prometheus + Grafana** (infra-level metrics)

## 🔔 Alert Categories

* P0: full system outage, customer impact
* P1: latency regression, background job stuck
* P2: retryable errors, non-critical jobs

## 🔍 Dashboards to Watch

* `/dash/eng/search-performance`
* `/dash/jobs/ingestion-errors`
* `/dash/frontend/core-metrics`

## 🔧 How to Tune Alerts


1. Go to Datadog
2. Open alert
3. Adjust threshold or evaluation window
4. Add @team-search-core for routing