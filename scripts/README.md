# API Test Scripts

These scripts run quick smoke tests against the FastAPI app.

## Prereqs
- Stack running: `docker compose up --build`
- FastAPI reachable at `http://localhost:9000`
- `curl` available

## Bash (macOS/Linux/WSL)

```bash
chmod +x scripts/test-api.sh
./scripts/test-api.sh
```

Override base URL:

```bash
API_BASE=http://localhost:9000 ./scripts/test-api.sh
```

## Windows (CMD)

```bat
scripts\test-api.bat
```

Override base URL:

```bat
set API_BASE=http://localhost:9000
scripts\test-api.bat
```
