from fastapi import FastAPI
from typing import Optional
from pydantic import BaseModel
from fastapi import Header

api = FastAPI()


class Item(BaseModel):
    itemid: int
    description: str
    owner: Optional[str] = None


@api.get('/')
def get_index(argument1):
    return {
        'data': argument1
    }


@api.post('/item')
def post_item(item: Item):
    return item


@api.get('/typed')
def get_typed(argument1: int):
    return {
        'data': argument1 + 1
    }


@api.get('/addition')
def get_addition(a: int, b: Optional[int] = None):
    if b:
        result = a + b
    else:
        result = a + 1
    return {
        'addition_result': result
    }


@api.get('/item/{itemid}')
def get_item_default(itemid):
    return {
        'route': 'dynamic',
        'itemid': itemid,
        'source': 'string'
    }


@api.get('/item/{itemid:float}')
def get_item_float(itemid):
    return {
        'route': 'dynamic',
        'itemid': itemid,
        'source': 'float'
    }


@api.get('/item/{itemid}/description/{language}')
def get_item_language(itemid, language):
    if language == 'fr':
        return {
            'itemid': itemid,
            'description': 'un objet',
            'language': 'fr'
        }
    else:
        return {
            'itemid': itemid,
            'description': 'an object',
            'language': 'en'
        }


@api.get('/headers')
def get_headers(user_agent=Header(None)):
    return {
        'User-Agent': user_agent
    }
