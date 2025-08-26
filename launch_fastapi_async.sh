uvicorn fastapi_async:api \
  --reload \
  --reload-exclude "**/*.py" \
  --reload-include "fastapi_async.py"