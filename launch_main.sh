uvicorn main:api \
  --reload \
  --reload-exclude "**/*.py" \
  --reload-include "main.py"