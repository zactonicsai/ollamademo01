@echo off
setlocal enabledelayedexpansion

REM ======================================================
REM FastAPI Embedder API Smoke Tests (Windows CMD)
REM - Runs /seed, /query, /generate
REM - Saves responses to scripts\out\
REM - Shows sample expected responses
REM ======================================================

IF "%API_BASE%"=="" (
  set "API_BASE=http://localhost:9000"
)

set "OUTDIR=%~dp0out"
IF NOT EXIST "%OUTDIR%" mkdir "%OUTDIR%"

echo ======================================================
echo FastAPI Embedder API Smoke Tests
echo API_BASE = %API_BASE%
echo Output  = %OUTDIR%
echo ======================================================
echo.

echo ------------------------------
echo SAMPLE EXPECTED RESPONSES
echo ------------------------------
echo 1) /seed  (first run)   : {"seeded":true,"count":7}   (count may vary)
echo    /seed  (later runs)  : {"seeded":false,"count":7}
echo.
echo 2) /query : {"query":"...","matches":[{"id":"...","title":"...","score":0.7,"code":"..."}]}
echo.
echo 3) /generate : {"model":"qwen2.5-fastapi-python","code":"<python code only>"}
echo ------------------------------
echo.

REM ======================================================
REM 1) POST /seed
REM ======================================================
echo [1/3] POST /seed
echo URL: %API_BASE%/seed
curl -sS -X POST "%API_BASE%/seed" > "%OUTDIR%\seed.json"
type "%OUTDIR%\seed.json"
echo.

findstr /i /c:"seeded" "%OUTDIR%\seed.json" >nul
IF ERRORLEVEL 1 (
  echo ERROR: /seed response missing "seeded" field
  echo Saved: %OUTDIR%\seed.json
  exit /b 1
)
echo OK: /seed response looks valid
echo.

REM ======================================================
REM 2) POST /query
REM ======================================================
echo [2/3] POST /query  (semantic search)
echo URL: %API_BASE%/query

set "QUERY_PAYLOAD={ \"query\": \"typed fastapi post endpoint with pydantic request model\", \"n_results\": 3 }"
echo Request JSON: %QUERY_PAYLOAD%

curl -sS -X POST "%API_BASE%/query" ^
  -H "Content-Type: application/json" ^
  -d "%QUERY_PAYLOAD%" > "%OUTDIR%\query.json"

type "%OUTDIR%\query.json"
echo.

findstr /i /c:"matches" "%OUTDIR%\query.json" >nul
IF ERRORLEVEL 1 (
  echo ERROR: /query response missing "matches"
  echo Saved: %OUTDIR%\query.json
  exit /b 1
)
echo OK: /query response looks valid
echo.

REM ======================================================
REM 3) POST /generate
REM ======================================================
echo [3/3] POST /generate  (RAG on)
echo URL: %API_BASE%/generate

set "GEN_PAYLOAD={ \"prompt\": \"Create a FastAPI router with GET /health and POST /items using typed Pydantic models.\", \"use_context\": true, \"n_context\": 2 }"
echo Request JSON: %GEN_PAYLOAD%

curl -sS -X POST "%API_BASE%/generate" ^
  -H "Content-Type: application/json" ^
  -d "%GEN_PAYLOAD%" > "%OUTDIR%\generate.json"

type "%OUTDIR%\generate.json"
echo.

findstr /i /c:"model" "%OUTDIR%\generate.json" >nul
IF ERRORLEVEL 1 (
  echo ERROR: /generate response missing "model"
  echo Saved: %OUTDIR%\generate.json
  exit /b 1
)

findstr /i /c:"code" "%OUTDIR%\generate.json" >nul
IF ERRORLEVEL 1 (
  echo ERROR: /generate response missing "code"
  echo Saved: %OUTDIR%\generate.json
  exit /b 1
)

echo OK: /generate response looks valid
echo.

echo ======================================================
echo Done ✅  Responses saved to:
echo   %OUTDIR%\seed.json
echo   %OUTDIR%\query.json
echo   %OUTDIR%\generate.json
echo ======================================================

endlocal
