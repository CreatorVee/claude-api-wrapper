# Claude API Wrapper

A small FastAPI app that wraps the Claude API. Send it a question, get an answer.

This is a 4-stage portfolio project, all stages complete:
1. FastAPI wrapper around Claude
2. Dockerise it
3. Deploy to AKS with Terraform
4. CI/CD (GitHub Actions) + Kubernetes secrets ← live, deploying on every push to `main`

---

## How to run it locally

### 1. Set up a virtual environment
```bash
cd claude-api-wrapper
python3 -m venv venv
source venv/bin/activate
```

### 2. Install the dependencies
```bash
pip install -r requirements.txt
```

### 3. Set your Claude API key
Get a key from https://console.anthropic.com, then:
```bash
export ANTHROPIC_API_KEY="your-key-here"
```
(Notice: the key lives in your shell, NOT in the code. This matters later.)

### 4. Start the app
```bash
uvicorn app.main:app --reload
```
You'll see it running on http://127.0.0.1:8000

### 5. Test it

**Option A — the auto-docs (easiest)**
Open http://127.0.0.1:8000/docs in your browser.
FastAPI gives you a clickable UI for free. Click `/ask`, hit "Try it out", type a question, run it.

**Option B — curl from the terminal**
```bash
curl -X POST http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Explain Kubernetes in one sentence."}'
```

You should get back:
```json
{"answer": "Kubernetes is a system that automatically..."}
```

---

## What each file does

| File | Role |
|------|------|
| `app/main.py` | The FastAPI app — the "door" to Claude |
| `requirements.txt` | The Python packages it needs |
| `README.md` | This file |

## The two endpoints

| Endpoint | What it does |
|----------|--------------|
| `GET /health` | Says "ok" — used later by Kubernetes to check the app is alive |
| `POST /ask` | Takes a question, asks Claude, returns the answer |

---

## Resuming after `terraform destroy`

If you tore down the Azure resources to save cost, here's the checklist to bring it all back up. Run from `claude-api-wrapper/`.

```bash
# 1. Recreate the resource group, ACR, and AKS cluster
cd terraform
terraform apply

# 2. Grant your own user push rights on the new ACR (role assignment was destroyed too)
az role assignment create \
  --assignee $(az ad signed-in-user show --query id -o tsv) \
  --role AcrPush \
  --scope $(terraform output -raw acr_login_server | xargs -I{} az acr show --name claudeapiwrapperacr --query id -o tsv)

# 3. Build and push the image to the new (empty) ACR
cd ..
az acr login --name claudeapiwrapperacr
docker build -t claudeapiwrapperacr.azurecr.io/claude-api-wrapper:latest .
docker push claudeapiwrapperacr.azurecr.io/claude-api-wrapper:latest

# 4. Connect kubectl to the new cluster (new credentials)
az aks get-credentials --resource-group claude-api-wrapper-rg --name claude-api-wrapper-aks --overwrite-existing

# 5. Recreate the secret (it doesn't survive cluster deletion)
export ANTHROPIC_API_KEY=sk-ant-...your-real-key...
kubectl create secret generic claude-secret --from-literal=ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY

# 6. Apply the manifests
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# 7. Wait for the new external IP, then test
kubectl get service claude-api-wrapper
curl http://<NEW-EXTERNAL-IP>/health
curl -X POST http://<NEW-EXTERNAL-IP>/ask -H "Content-Type: application/json" -d '{"question":"hello"}'
```

Note: the external IP will be different every time the LoadBalancer is recreated.

### Still outstanding (Stage 4 — CI/CD)
- Push this repo to GitHub
- Create an Azure service principal for GitHub Actions and add it + ACR/AKS names as GitHub repo secrets (see chat history or `.github/workflows/deploy.yml` for the exact secret names it expects: `AZURE_CREDENTIALS`, `ACR_NAME`, `ACR_LOGIN_SERVER`, `AKS_RESOURCE_GROUP`, `AKS_CLUSTER_NAME`)
- Push a commit to `main` and confirm the Actions workflow deploys successfully
