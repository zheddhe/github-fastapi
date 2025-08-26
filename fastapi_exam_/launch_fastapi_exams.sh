uvicorn main:app \
  --reload \
  --reload-exclude "**/*.py" \
  --reload-include "main.py"