# Runbook — Deployment Pipeline

## 🚀 Overview

All services deploy through GitHub Actions + ECS. PR merges to `main` trigger the pipeline.

## 🔁 Flow


1. Lint & Unit Tests
2. Docker Build
3. Deploy to `staging`
4. E2E tests
5. Deploy to `production` on manual approval

## 🛑 Rollback Steps

* Use GitHub UI ➝ Revert PR ➝ Redeploy
* Or use `deploy-cli rollback --service xyz --to v1234`

## 🧩 Environments

* `dev` → fast, CI-bypassed
* `staging` → mirrors prod infra
* `prod` → gated behind approvals

## 🧙 Tips

* Use `DEPLOY_ENV=staging make deploy` for manual triggers
* Keep rollback notes pinned to the deployment Slack channel