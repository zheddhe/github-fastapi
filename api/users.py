from typing import Any, Dict, List, Optional, Union

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging

logger = logging.getLogger("uvicorn.error")

# ---------------------------------------------------------------------------
# In-memory "DB"
# ---------------------------------------------------------------------------
users_db: List[Dict[str, Union[int, str]]] = [
    {"user_id": 1, "name": "Alice", "subscription": "free tier"},
    {"user_id": 2, "name": "Bob", "subscription": "premium tier"},
    {"user_id": 3, "name": "Clementine", "subscription": "free tier"},
]


# ---------------------------------------------------------------------------
# OpenAPI / tags
# ---------------------------------------------------------------------------
tags_metadata = [
    {
        "name": "health",
        "description": "Endpoints de vérification du service.",
    },
    {
        "name": "users",
        "description": "CRUD de démonstration pour gérer des utilisateurs.",
    },
]

api = FastAPI(
    title="Users Demo API",
    description=(
        "API d'exemple illustrant la documentation OpenAPI, les codes d'erreur"
        " et les schémas Pydantic."
    ),
    version="1.0.0",
    openapi_tags=tags_metadata,
)

# ---------------------------------------------------------------------------
# Responses helpers (typage dict[int|str, dict[str, Any]])
# ---------------------------------------------------------------------------
ErrorResponses = Dict[Union[int, str], Dict[str, Any]]

responses: ErrorResponses = {
    200: {"description": "Utilisateur mis à jour avec succès"},
    404: {"description": "Utilisateur non trouvé"},
    422: {"description": "Erreur de validation des données"},
}


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
class User(BaseModel):
    user_id: Optional[int]
    name: str
    subscription: str


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@api.get(
    "/",
    tags=["health"],
    summary="Bienvenue",
    description="Renvoie un message de bienvenue.",
    responses={},  # 200 par défaut
)
def get_index():
    return {
        'greetings': 'welcome'
    }


@api.get(
    "/users",
    tags=["users"],
    summary="Lister les utilisateurs",
    description="Retourne la liste complète des utilisateurs.",
    response_model=List[User],
)
def get_users():
    return users_db


@api.get(
    "/users/{userid:int}",
    tags=["users"],
    summary="Récupérer un utilisateur",
    description="Retourne l'utilisateur correspondant à l'identifiant fourni."
                " (Rien si non trouvé)",
    response_model=Union[User, Dict],
    responses=responses,
)
def get_user(userid: int):
    try:
        user = list(filter(lambda x: x['user_id'] == userid, users_db))[0]
        return user
    except IndexError:
        logger.warning(f"Utilisateur {userid} introuvable")
        raise HTTPException(
            status_code=404,
            detail=f"Utilisateur {userid} introuvable"
        )


@api.get(
    "/users/{userid:int}/name",
    tags=["users"],
    summary="Récupérer le nom d'un utilisateur",
    description="Retourne uniquement le champ `name` de l'utilisateur."
                " (Rien si non trouvé)",
    response_model=Dict[str, str],
    responses=responses,
)
def get_user_name(userid: int):
    try:
        user = list(filter(lambda x: x['user_id'] == userid, users_db))[0]
        return {'name': user['name']}
    except IndexError:
        logger.warning(f"Utilisateur {userid} introuvable")
        raise HTTPException(
            status_code=404,
            detail=f"Utilisateur {userid} introuvable"
        )


@api.get(
    '/users/{userid:int}/subscription',
    tags=["users"],
    summary="Récupérer l'abonnement d'un utilisateur",
    description="Retourne uniquement le champ `subscription` de l'utilisateur.",
    response_model=Dict[str, str],
    responses=responses,
)
def get_user_suscription(userid: int):
    try:
        user = list(filter(lambda x: x['user_id'] == userid, users_db))[0]
        return {'subscription': user['subscription']}
    except IndexError:
        logger.warning(f"Utilisateur {userid} introuvable")
        raise HTTPException(
            status_code=404,
            detail=f"Utilisateur {userid} introuvable"
        )


@api.put(
    "/users",
    tags=["users"],
    summary="Créer un utilisateur",
    description=(
        "Crée un nouvel utilisateur. Renvoie l'objet créé."
    ),
    response_model=User,
    responses=responses,
)
def put_users(user: User):
    new_id = max(users_db, key=lambda x: x['user_id'])['user_id']
    new_user = {
        'user_id': new_id + 1,  # type: ignore
        'name': user.name,
        'subscription': user.subscription
    }
    users_db.append(new_user)
    return new_user


@api.post(
    "/users/{userid:int}",
    tags=["users"],
    summary="Mettre à jour un utilisateur",
    description="Met à jour `name` et `subscription` d'un utilisateur existant."
    "\nLes autres données sont ignorées",
    response_model=Union[User, Dict],
    responses=responses,
)
def post_users(user: User, userid: int):
    try:
        logger.info(f"Le user donné est {user} et le userid est {userid}")
        old_user = list(
            filter(lambda x: x['user_id'] == userid, users_db)
        )[0]
        logger.info(f"L'ancien user est {old_user}")
        users_db.remove(old_user)
        logger.info("L'ancien user est supprimé")

        old_user['name'] = user.name
        old_user['subscription'] = user.subscription

        users_db.append(old_user)
        return old_user

    except IndexError:
        logger.warning(f"Utilisateur {userid} introuvable")
        raise HTTPException(
            status_code=404,
            detail=f"Utilisateur {userid} introuvable"
        )


@api.delete(
    "/users/{userid:int}",
    tags=["users"],
    summary="Supprimer un utilisateur",
    description="Supprime un utilisateur existant.",
    response_model=Dict[str, Union[int, bool]],
    responses=responses,
)
def delete_users(userid: int):
    try:
        old_user = list(
            filter(lambda x: x['user_id'] == userid, users_db)
            )[0]

        users_db.remove(old_user)
        return {
            'userid': userid,
            'deleted': True
            }
    except IndexError:
        logger.warning(f"Utilisateur {userid} introuvable")
        raise HTTPException(
            status_code=404,
            detail=f"Utilisateur {userid} introuvable"
        )
