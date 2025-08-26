from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi import Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Any, Dict, Union, List, Optional
import pandas as pd
import datetime
import logging
import re

# on s'outille du logger d'uvicorn pour mieux tracer les comportements dans la console
logger = logging.getLogger("uvicorn.error")

# on charge le dataset sous forme d'un dataframe
df = pd.read_csv("questions.csv")
logger.info(f"Dataframe chargé contenant {df.shape[0]} lignes et {df.shape[1]} colonnes")

# gestion simple de la sécurité (pas de wallet : identifiant à vérifier depuis un dictionnaire)
dict_credentials = {
  "alice": "wonderland",
  "bob": "builder",
  "clementine": "mandarine"
}
security = HTTPBasic()

# ---------------------------------------------------------------------------
# OpenAPI / tags
# ---------------------------------------------------------------------------
tags_metadata = [
    {
        "name": "Admin",
        "description": "Section de vérification du service.",
    },
    {
        "name": "QCMs",
        "description": "Section de gestion des QCMs.",
    },
]

app = FastAPI(
    title="Exam FastAPI API",
    description=(
        "API permettant de gérer des QCM"
    ),
    version="1.0.0",
    openapi_tags=tags_metadata,
)


# ---------------------------------------------------------------------------
# Modèles (avec description des champs intégrée)
# ---------------------------------------------------------------------------
class ErrorResponse(BaseModel):
    type: str = Field(..., description="type d'erreur métier")
    message: Optional[str] = Field(..., description="contenu précisant l'erreur le cas échéant")
    date: str = Field(..., description="2025-08-26 14:08:19.431291")


class QuizRequest(BaseModel):
    test_type: str = Field(..., description="Type de test souhaité")
    categories: List[str] = Field(..., description="Liste des catégories de questions souhaitées")
    nb_questions: int = Field(..., description="Nombre de questions à inclure dans le QCM")


class QuizItem(BaseModel):
    question: str = Field(..., description="Contenu formulé de la question")
    subject: str = Field(..., description="Sujet ou thème de la question")
    correct: List[str] = Field(..., description="Ensemble des réponses correctes")
    use: str = Field(..., description="Type de test souhaité")
    responseA: str = Field(..., description="Contenu formulé de la réponse A")
    responseB: str = Field(..., description="Contenu formulé de la réponse B")
    responseC: str = Field(..., description="Contenu formulé de la réponse C")
    responseD: Optional[str] = Field(..., description="Contenu formulé de la réponse D")


class QuestionRequest(BaseModel):
    admin_username: str = Field(..., description="username admin")
    admin_password: str = Field(..., description="password admin")
    question: str = Field(..., description="Contenu formulé de la question")
    subject: str = Field(..., description="Sujet ou thème de la question")
    correct: List[str] = Field(..., description="Ensemble des réponses correctes")
    use: str = Field(..., description="Type de test souhaité")
    responseA: str = Field(..., description="Contenu formulé de la réponse A")
    responseB: str = Field(..., description="Contenu formulé de la réponse B")
    responseC: str = Field(..., description="Contenu formulé de la réponse C")
    responseD: Optional[str] = Field(..., description="Contenu formulé de la réponse D")


# ---------------------------------------------------------------------------
# Exception métier personalisée + son handler
# ---------------------------------------------------------------------------
class CustomException(Exception):
    def __init__(self,
                 type: str,
                 date: str,
                 message: str):
        self.type = type
        self.date = date
        self.message = message


@app.exception_handler(CustomException)
def CustomExceptionHandler(
    _request: Request,  # non utilisé
    exception: CustomException
):
    return JSONResponse(
        status_code=418,
        content=ErrorResponse(
            type=exception.type,
            message=exception.message,
            date=exception.date,
        ).model_dump()
    )


# ---------------------------------------------------------------------------
# Documentation (globale) des réponses
# ---------------------------------------------------------------------------
# on type correctement le dictionnaire des réponses attendu par le décorateur
ResponsesDict = Dict[Union[int, str], Dict[str, Any]]
generic_responses: ResponsesDict = {
    200: {"description": "Enregistrement mis à jour avec succès"},
    400: {"description": "Erreur de valeur"},
    403: {"description": "Echec de l'authentification"},
    404: {"description": "Enregistrement non trouvé"},
    418: {
        "description": "Business error",
        "model": ErrorResponse,
        "content": {
            "application/json": {
                "example": {
                    "type": "Nombre de question demandé incorrect",
                    "message": "nb_questions=0",
                    "date": "2025-08-26 14:08:19.431291",
                }
            }
        },
    },    422: {"description": "Erreur de validation des données"},
}


# ---------------------------------------------------------------------------
# Fonctions utilitaires
# ---------------------------------------------------------------------------
def _series_to_jsonable(row: pd.Series) -> dict:
    """
    Conversion Series Pandas en dictionnaire compréhensible pour l'API
    """
    return {k: (None if pd.isna(v) else v) for k, v in row.items()}


def _check_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    """
    Verification des identifiants en base 64 native pour fastAPI (+ docs/redoc)
    """
    if credentials.username not in dict_credentials.keys():
        raise HTTPException(
            status_code=403,
            detail=f"Utilisateur [{credentials.username}] inconnu"
        )
    if dict_credentials[credentials.username] != credentials.password:
        raise HTTPException(
            status_code=403,
            detail=f"Mot de passe incorrect pour l'utilisateur [{credentials.username}]"
        )


def _validate_quiz_parameters(quiz_request: QuizRequest):
    if quiz_request.nb_questions <= 0:
        raise CustomException(
            type="Nombre de question demandé incorrect",
            message=f"quiz_request.nb_questions = {quiz_request.nb_questions}",
            date=str(datetime.datetime.now()),
        )
    if quiz_request.test_type not in list(df["use"].unique()):
        raise CustomException(
            type="Type de test demandé absent du catalogue",
            message=f"quiz_request.test_type = {quiz_request.test_type}",
            date=str(datetime.datetime.now()),
        )
    if not all(item in list(df["subject"].unique()) for item in quiz_request.categories):
        raise CustomException(
            type="Au moins une catégorie demandée absente du catalogue",
            message=f"quiz_request.categories = {quiz_request.categories}",
            date=str(datetime.datetime.now()),
        )


def _select_random_responses(quiz_request: QuizRequest):
    df_valid = df[(df["use"] == quiz_request.test_type)
                  & (df["subject"].isin(quiz_request.categories))]
    if df_valid.empty:
        raise CustomException(
            type="Aucune question trouvée",
            message=(
                f"Aucune correspondance pour test_type="
                f"{quiz_request.test_type}, "
                f"categories={quiz_request.categories}"
            ),
            date=str(datetime.datetime.now()),
        )
    n = quiz_request.nb_questions
    available = len(df_valid)
    if quiz_request.nb_questions > available:
        raise CustomException(
            type="Nombre de questions demandé trop grand",
            message=(
                f"nb_questions={n}, disponibles={available}"
            ),
            date=str(datetime.datetime.now()),
        )
    df_sampled = df_valid.sample(
        n=quiz_request.nb_questions, random_state=None
    )
    # Conversion DataFrame dans la structure attendue en sortie (List[QuizItem])
    items = [_row_to_quiz_item(row) for _, row in df_sampled.iterrows()]
    logger.info("sampled=%s / available=%s", len(items), available)
    return items


def _row_to_quiz_item(row: pd.Series) -> QuizItem:
    """
    Mapping des lignes pandas vers QuizItem, avec conversion des NaN pour reponse D
    """
    def _opt_str(v: Any) -> Optional[str]:
        return None if (v is None or (isinstance(v, float) and pd.isna(v))) else str(v)
    d_val = _opt_str(row.get("responseD"))
    return QuizItem(
        question=str(row.get("question")),
        subject=str(row.get("subject")),
        use=str(row.get("use")),
        correct=_parse_correct(row),
        responseA=row["responseA"],
        responseB=row["responseB"],
        responseC=row["responseC"],
        responseD=d_val,
    )


def _parse_correct(row: pd.Series) -> List[str]:
    """
    Traduction des réponses pour 'correct' (List[str])
    Accepte le format avec séparateur espace ou virgule
    Example: "A B C" -> ["reponseA", "reponseB", "reponseC"]
    Example: "A,B,C" -> ["reponseA", "reponseB", "reponseC"]
    """
    correct_val = row["correct"]
    if correct_val is None or pd.isna(correct_val):
        return []
    if isinstance(correct_val, str):
        letters = [
            part.strip()
            for part in re.split(r"[ ,]+", correct_val.strip())
            if part.strip()
        ]
    else:
        letters = [str(correct_val).strip()]
    mapping = {
        "A": row.get("responseA"),
        "B": row.get("responseB"),
        "C": row.get("responseC"),
        "D": row.get("responseD"),
    }
    # on ne retourne que les items qui ont une réponse
    return [
        str(mapping[letter])
        for letter in letters
        if letter in mapping and pd.notna(mapping[letter])
    ]


def _validate_question_parameters(question_request: QuestionRequest):
    proposed_responses = {
        "A": question_request.responseA,
        "B": question_request.responseB,
        "C": question_request.responseC,
        "D": question_request.responseD,
    }
    logger.info(f"{question_request.correct} <=> {list(proposed_responses.values())}")
    if not question_request.correct:
        raise CustomException(
            type="Aucune réponse correcte proposée dans les réponses",
            message=f"question_request.correct = {question_request.correct}",
            date=str(datetime.datetime.now()),
        )
    if not all(val in proposed_responses.values() for val in question_request.correct):
        raise CustomException(
            type="Réponse correcte non proposée dans les réponses",
            message=f"question_request.correct = {question_request.correct}",
            date=str(datetime.datetime.now()),
        )


def _store_question(question_request: QuestionRequest):
    try:
        responses_map = {
            question_request.responseA: "A",
            question_request.responseB: "B",
            question_request.responseC: "C",
            question_request.responseD: "D",
        }
        correct = []
        for response in question_request.correct:
            correct.append(responses_map[response])
        new_row = {
            "question": question_request.question,
            "subject": question_request.subject,
            "use": question_request.use,
            "correct": correct,
            "responseA": question_request.responseA,
            "responseB": question_request.responseB,
            "responseC": question_request.responseC,
            "responseD": question_request.responseD,
            "remark": "",
        }
        global df
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        logger.info(f"Question stored. index={len(df) - 1}")
    except Exception as exc:
        logger.exception("Error while storing question")
        raise HTTPException(
            status_code=500,
            detail="Erreur lors de la sauvegarde de la question",
        ) from exc


# ---------------------------------------------------------------------------
# Définition des Routes
# ---------------------------------------------------------------------------
@app.get(
    "/verify",
    tags=["Admin"],
    summary="Vérifier le service",
    description="Vérifie que l'API est fonctionnelle.",
    responses={},  # réponses par défaut (200 seulement ici)
)
def get_verify():
    return {
        "message": "L'API est fonctionnelle."
    }


@app.get(
    "/records/{recordid:int}",
    tags=["Admin"],
    summary="Afficher enregistrement par id",
    description="Affiche le contenu d'un enregistrement du dataframe par son recordid (index).",
    responses=generic_responses,
)
def get_record_by_recordid(recordid: int):
    try:
        row = df.iloc[recordid]
        return _series_to_jsonable(row)
    except IndexError as exc:
        raise HTTPException(status_code=404, detail="Ligne non trouvée") from exc


@app.post(
    "/generate_quiz",
    tags=["QCMs"],
    summary="Génèrer Quiz",
    description=(
        "Génère un QCM basé sur les paramètres fournis.\n"
        "Utilise l'authentification basique avec en-têtes HTTP."
    ),
    responses=generic_responses,
)
def post_generate_quiz(quiz_request: QuizRequest,
                       user: str = Depends(_check_credentials)):
    """
    METHOD :
        generation en POST d'un QCM avec paramètres dans le payload
    PAYLOAD : (Cf. QuizRequest)
        QuizRequest
    RESPONSE : (Cf. QuizItem)
        List[QuizItem]
    """
    logger.info(f"l'utilisateur [{user}] a accédé à la route post_generate_quiz")
    _validate_quiz_parameters(quiz_request)
    quiz_items = _select_random_responses(quiz_request)
    return quiz_items


@app.post(
    "/create_question",
    tags=["QCMs"],
    summary="Créer question",
    description=(
        "Crée une nouvelle question par un utilisateur admin.\n"
        "Pas d'authentification demandée."
    ),
    responses=generic_responses,
)
def post_create_question(question_request: QuestionRequest):
    """
    METHOD :
        generation en POST d'un QCM avec paramètres dans le payload
    PAYLOAD : (Cf. QuestionRequest)
        QuestionRequest
    RESPONSE :
        Dict[str]
    """
    logger.info(f"l'utilisateur [{question_request.admin_username}] "
                "a accédé à la route post_create_question")
    _validate_question_parameters(question_request)
    _store_question(question_request)
    return {"message": "Question créée avec succès."}
