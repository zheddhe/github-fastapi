# # GET at /
# curl -X GET -i http://127.0.0.1:8000/
# # GET at /
# curl -X GET -i http://127.0.0.1:8000/?argument1=hello%20world
# # GET at /typed
# curl -X GET -i http://127.0.0.1:8000/typed?argument1=1234
# curl -X GET -i http://127.0.0.1:8000/typed?argument1=hello
# # GET at /addition
# curl -X GET -i http://127.0.0.1:8000/addition?a=13\&b=4
# POST at /
# curl -X POST -i http://127.0.0.1:8000/
# # PUT at /
# curl -X PUT -i http://127.0.0.1:8000/
# # DELETE at /
# curl -X DELETE -i http://127.0.0.1:8000/
# # PATCH at /
# curl -X PATCH -i http://127.0.0.1:8000/
# # GET at /other
# curl -X GET -i http://127.0.0.1:8000/other

# curl -X 'POST' -i \
#   'http://127.0.0.1:8000/item'

# curl -X 'POST' -i \
#   'http://127.0.0.1:8000/item' \
#   -H 'Content-Type: application/json' \
#   -d '{
#   "itemid": 1234,
#   "description": "my object",
#   "owner": "Daniel"
# }'

# curl -X 'POST' -i \
#   'http://127.0.0.1:8000/item' \
#   -H 'Content-Type: application/json' \
#   -d '{
#   "itemid": 1234,
#   "description": "my object"
# }'

# curl -X 'POST' -i \
#   'http://127.0.0.1:8000/item' \
#   -H 'Content-Type: application/json' \
#   -d '{
#   "itemid": 12345
# }'

# curl -X 'POST' -i \
#   'http://127.0.0.1:8000/item' \
#   -H 'Content-Type: application/json' \
#   -d '{
#   "itemid": 12345,
#   "description": "my object",
#   "other": "something else"
# }'

curl -X GET -i http://127.0.0.1:8000/headers

curl -X GET \
     -H 'User-Agent: MyCustomClient/1.0' \
     -i http://127.0.0.1:8000/headers