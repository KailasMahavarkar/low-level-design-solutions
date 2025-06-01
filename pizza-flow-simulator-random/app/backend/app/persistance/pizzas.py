from typing import List
from sqlmodel import select
from models.pizzas import Pizza, PizzaStatus
from .database import get_db

def load_persisted_pizza(pizza_id: str) -> Pizza:
    ''' Load a persisted pizza '''
    with get_db() as db:
        return db.get(Pizza, pizza_id)

def persist_pizza(pizza: Pizza) -> Pizza:
    ''' Persist a pizza '''
    with get_db() as db:
        db.add(pizza)
        db.commit()
        db.refresh(pizza)
    return pizza

async def list_persisted_pizzas(limit: int = None, offset: int = 0, status: List[PizzaStatus] = None) -> List[Pizza]:
    ''' List persisted pizzas '''
    with get_db() as db:
        return db.exec(select(Pizza).offset(offset).limit(limit)).all()
