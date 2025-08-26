### Tests unitaires /verify
curl -X GET 'http://127.0.0.1:8000/verify'
echo "### test verify fin"

### Tests unitaires /records/{recordid} [Optionel pour que je puisse vérifier le dataframe chargé plus facilement]
curl -X GET 'http://127.0.0.1:8000/records/1'
echo '### test records connu fin'

curl -X GET 'http://127.0.0.1:8000/records/1000'
echo '### test records inconnu fin'

curl -X GET 'http://127.0.0.1:8000/records/INCORRECT'
echo '### test records invalide fin'

curl -X GET 'http://127.0.0.1:8000/records/INCORRECT'
echo '### test records invalide fin'

### Tests unitaires /generate_quiz
curl -X 'POST' \
  'http://127.0.0.1:8000/generate_quiz' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "test_type": "Test de positionnement",
  "categories": [
    "BDD"
  ],
  "nb_questions": 1
}'
echo '### test generate_quiz pas de credentials fin'

curl -X 'POST' \
  'http://127.0.0.1:8000/generate_quiz' \
  -H 'accept: application/json' \
  -H 'Authorization: Basic dGVzdDo=' \
  -H 'Content-Type: application/json' \
  -d '{
  "test_type": "Test de positionnement",
  "categories": [
    "BDD"
  ],
  "nb_questions": 1
}'
echo '### test generate_quiz username inconnu fin'

curl -X 'POST' \
  'http://127.0.0.1:8000/generate_quiz' \
  -H 'accept: application/json' \
  -H 'Authorization: Basic dGVzdDo=' \
  -H 'Content-Type: application/json' \
  -d '{
  "test_type": "Test de positionnement",
  "categories": [
    "BDD"
  ],
  "nb_questions": 1
}'
echo '### test generate_quiz username inconnu fin'

curl -X 'POST' \
  'http://127.0.0.1:8000/generate_quiz' \
  -H 'accept: application/json' \
  -H 'Authorization: Basic YWxpY2U6' \
  -H 'Content-Type: application/json' \
  -d '{
  "test_type": "Test de positionnement",
  "categories": [
    "BDD"
  ],
  "nb_questions": 1
}'
echo '### test generate_quiz password invalide fin'

curl -X 'POST' \
  'http://127.0.0.1:8000/generate_quiz' \
  -H 'accept: application/json' \
  -H 'Authorization: Basic YWxpY2U6d29uZGVybGFuZA==' \
  -H 'Content-Type: application/json' \
  -d '{
  "test_type": "Test de positionnement",
  "categories": [
    "BDD"
  ],
  "nb_questions": 0
}'
echo '### test generate_quiz nombre de questions invalide fin'

curl -X 'POST' \
  'http://127.0.0.1:8000/generate_quiz' \
  -H 'accept: application/json' \
  -H 'Authorization: Basic YWxpY2U6d29uZGVybGFuZA==' \
  -H 'Content-Type: application/json' \
  -d '{
  "test_type": "Test de positionnement INCONNU",
  "categories": [
    "BDD"
  ],
  "nb_questions": 1
}'
echo '### test generate_quiz type de test incorrect fin'

curl -X 'POST' \
  'http://127.0.0.1:8000/generate_quiz' \
  -H 'accept: application/json' \
  -H 'Authorization: Basic YWxpY2U6d29uZGVybGFuZA==' \
  -H 'Content-Type: application/json' \
  -d '{
  "test_type": "Test de positionnement",
  "categories": [
    "BDD INCONNUE"
  ],
  "nb_questions": 1
}'
echo '### test generate_quiz categorie inconnue fin'

curl -X 'POST' \
  'http://127.0.0.1:8000/generate_quiz' \
  -H 'accept: application/json' \
  -H 'Authorization: Basic YWxpY2U6d29uZGVybGFuZA==' \
  -H 'Content-Type: application/json' \
  -d '{
  "test_type": "Test de positionnement",
  "categories": [
    "BDD"
  ],
  "nb_questions": 10
}'
echo '### test generate_quiz nombre de question demandé trop grand fin'

curl -X 'POST' \
  'http://127.0.0.1:8000/generate_quiz' \
  -H 'accept: application/json' \
  -H 'Authorization: Basic YWxpY2U6d29uZGVybGFuZA==' \
  -H 'Content-Type: application/json' \
  -d '{
  "test_type": "Test de positionnement",
  "categories": [
    "BDD"
  ],
  "nb_questions": 6
}'
echo '### test generate_quiz OK fin'

curl -X 'POST' \
  'http://127.0.0.1:8000/generate_quiz' \
  -H 'accept: application/json' \
  -H 'Authorization: Basic YWxpY2U6d29uZGVybGFuZA==' \
  -H 'Content-Type: application/json' \
  -d '{
  "test_type": "Test de positionnement",
  "categories": [
    "BDD"
  ],
  "nb_questions": 6
}'
echo '### test generate_quiz OK avec shuffle fin'