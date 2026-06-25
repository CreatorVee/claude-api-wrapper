# Build Brief: Claude API Wrapper → Production on AKS

You are Claude Code acting as an agent. Build this project stage by stage.
After each stage, stop and confirm it works before moving to the next.

## Project goal
A FastAPI app that wraps the Claude API, containerised with Docker, deployed
to Azure Kubernetes Service (AKS) via Terraform, with a GitHub Actions CI/CD
pipeline and the API key stored as a Kubernetes secret.

## Environment
- Ubuntu (Linux), user `veek07`
- Target project path: `/home/veek07/ai-skills/claude-api-wrapper`
- Existing DevOps skills available: Azure, AKS, Terraform, GitHub Actions, kubectl, Docker
- Claude API key will be provided via the environment variable `ANTHROPIC_API_KEY`

---

## STAGE 1 — FastAPI wrapper (ALREADY DONE)
Already built. Files:
- `app/main.py` — FastAPI app with `POST /ask` (question → Claude → answer) and `GET /health`
- `requirements.txt` — fastapi, uvicorn[standard], anthropic, pydantic

Verify it runs locally with:
```
uvicorn app.main:app --reload
```
and that http://127.0.0.1:8000/docs works. Then move on.

---

## STAGE 2 — Dockerise it
- Write a `Dockerfile` (use a slim Python base image, e.g. python:3.12-slim).
- Install requirements, copy the app, expose port 8000.
- Run with uvicorn on 0.0.0.0:8000 so it's reachable outside the container.
- Add a `.dockerignore` (exclude venv, __pycache__, .git, etc.).
- The API key must come in at runtime as an env var, NEVER baked into the image.
- Show me the commands to build and run locally:
  - `docker build -t claude-api-wrapper .`
  - `docker run -p 8000:8000 -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY claude-api-wrapper`
- Confirm the container responds before continuing.

---

## STAGE 3 — Deploy to AKS with Terraform
- Write Terraform to provision: a resource group, an Azure Container Registry (ACR),
  and an AKS cluster, with AKS allowed to pull from ACR.
- Keep Terraform in a `terraform/` folder. Use variables for names/region.
- Provide the steps to:
  - push the local image to ACR
  - `terraform init / plan / apply`
  - connect kubectl to the new cluster
- Write Kubernetes manifests in a `k8s/` folder:
  - a Deployment (use the ACR image, set a readiness/liveness probe on `/health`)
  - a Service of type LoadBalancer exposing port 80 → container 8000
- Confirm I can hit the public IP and get an answer from `/ask`.

---

## STAGE 4 — CI/CD + secrets
- Add a GitHub Actions workflow (`.github/workflows/deploy.yml`) that on push to main:
  - builds the Docker image
  - pushes it to ACR
  - deploys/updates the Kubernetes deployment
- Store the Claude API key as a Kubernetes secret (not in code, not in the image):
  - `kubectl create secret generic claude-secret --from-literal=ANTHROPIC_API_KEY=...`
  - reference it in the Deployment via `valueFrom.secretKeyRef`.
- Store Azure/ACR credentials as GitHub repository secrets, referenced in the workflow.
- Explain each piece briefly as you go so I understand it, not just copy it.

---

## How I want you to work
- One stage at a time. Don't jump ahead.
- After each stage: tell me how to test it, and wait for me to confirm.
- Explain new concepts in plain, simple language (short bullets or small tables).
- Never hard-code the API key anywhere.
- Keep the folder structure clean and standard.
