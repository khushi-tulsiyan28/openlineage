## MLOps API Gateway – Postman Quick Guide

Base URL: `http://localhost:8081`

Notes
- Replace `<ACCESS_TOKEN>` with a valid Microsoft Entra ID access token you obtained during OAuth login.
- All responses are JSON. Headers are case-insensitive.

### 1) Health
- Method: GET
- URL: `/health`
- Headers: none

Example curl:
```bash
curl -s http://localhost:8081/health
```

### 2) Start OAuth (browser-based)
- Method: GET
- URL: `/oauth/authorize?redirect=1`
- Headers: none
- What happens: You will be redirected to Microsoft sign-in; after login you’ll land on `/oauth/callback` which returns a JSON list of experiments you’re allowed to see.

Example (open in browser):
```text
http://localhost:8081/oauth/authorize?redirect=1
```

### 3) Who am I + allowed experiments
- Method: GET
- URL: `/oauth/me`
- Headers:
  - `Authorization: Bearer <ACCESS_TOKEN>`

Example curl:
```bash
curl -s \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  http://localhost:8081/oauth/me
```

### 4) List my allowed MLflow experiments (simple)
- Method: GET
- URL: `/mlflow`
- Headers:
  - `Authorization: Bearer <ACCESS_TOKEN>`

Example curl:
```bash
curl -s \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  http://localhost:8081/mlflow
```

### 5) MLflow experiments (UI-internal API – optional)
- Method: GET
- URL (UI calls this): `/mlflow/ajax-api/2.0/mlflow/experiments/search?max_results=25&order_by=last_update_time+DESC`
- Headers:
  - `Authorization: Bearer <ACCESS_TOKEN>`

Example curl:
```bash
curl -s \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  "http://localhost:8081/mlflow/ajax-api/2.0/mlflow/experiments/search?max_results=25&order_by=last_update_time+DESC"
```

### 6) Token exchange (advanced, usually not needed directly)
- Method: GET
- URL: `/oauth/token?code=<AUTH_CODE>&redirect_uri=http://localhost:8081/oauth/callback`
- Headers: none

Example curl:
```bash
curl -s \
  "http://localhost:8081/oauth/token?code=<AUTH_CODE>&redirect_uri=http://localhost:8081/oauth/callback"
```

---

### Postman Setup Tips
- Create a Postman environment with variable `baseUrl = http://localhost:8081` and `accessToken = <ACCESS_TOKEN>`.
- In each request, set `{{baseUrl}}` in the URL and add header `Authorization: Bearer {{accessToken}}` where required.
- To get `<ACCESS_TOKEN>`, run the OAuth flow in the browser using `/oauth/authorize?redirect=1`; the gateway also sets a cookie for browser calls, but Postman must send the token in the Authorization header.

### Expected Responses
- `/health`: `{ "status": "healthy", ... }`
- `/oauth/me`: `{ user: { ... }, experiments: [...], next_page_token: null }`
- `/mlflow`: `{ experiments: [...], next_page_token: null }`


### Group-Based Access Control
- The gateway now supports user- and group-based permissions. A user's allowed experiments are the union of:
  - Experiments mapped to their email, and
  - Experiments mapped to any Entra ID groups present in their token's `groups` claim.

- Policy file location: `nginx-gateway/policy/experiment_access.json`

- Supported schema:
```json
{
  "users": {
    "user@example.com": { "experiments": ["1", "2"] }
  },
  "groups": {
    "<group-object-id>": { "experiments": ["2", "3"] }
  }
}
```

- Notes
  - Email keys are matched case-insensitively.
  - Group keys are Entra ID group object IDs as strings.
  - If tokens contain `hasgroups` instead of `groups` (overage), the gateway cannot resolve groups automatically. Ensure the app registration issues the `groups` claim or extend the gateway to call Microsoft Graph.

- Verify groups in your token via:
```bash
curl -s -H "Authorization: Bearer <ACCESS_TOKEN>" http://localhost:8081/oauth/me | jq '.user.groups'
```


