uvicorn api.users:api \
  --reload \
  --reload-exclude "**/*.py" \
  --reload-include "api/*.py"