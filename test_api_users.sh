# # GET at /
# curl -X GET -i http://127.0.0.1:8000/
# # GET at /users/2/name
# curl -X GET -i http://127.0.0.1:8000/users/2/name

# PUT at /users/
curl -X PUT "http://127.0.0.1:8000/users" \
     -H "Content-Type: application/json" \
     -d '{"userid": 1, "name": "Alice", "subscription": "premium"}'

# POST at /users/
curl -X POST "http://127.0.0.1:8000/users/4" \
     -H "Content-Type: application/json" \
     -d '{"userid": 4, "name": "Sabine", "subscription": "modification contrat"}'

# POST at /users/
curl -X DELETE "http://127.0.0.1:8000/users/12"