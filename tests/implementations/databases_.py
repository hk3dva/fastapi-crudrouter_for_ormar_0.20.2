from typing import List

import databases
from sqlalchemy import MetaData, Table, Column, Integer, Float, String, create_engine

from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy_utils import drop_database, create_database, database_exists

from fastapi_crudrouter import DatabasesCRUDRouter
from tests import Potato, PotatoCreate, Carrot, CarrotCreate

DATABASE_URL = "sqlite:///./test.db"


def _setup_database():
    if database_exists(DATABASE_URL):
        drop_database(DATABASE_URL)

    create_database(DATABASE_URL)
    database = databases.Database(DATABASE_URL)
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

    return engine, database


def databases_implementation():
    engine, database = _setup_database()

    metadata = MetaData()
    potatoes = Table(
        "potatoes",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("thickness", Float),
        Column("mass", Float),
        Column("color", String),
        Column("type", String),
    )
    carrots = Table(
        "carrots",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("length", Float),
        Column("color", String),
    )
    metadata.create_all(bind=engine)

    app = FastAPI()

    @app.on_event("startup")
    async def startup():
        await database.connect()

    @app.on_event("shutdown")
    async def shutdown():
        await database.disconnect()

    potato_router = DatabasesCRUDRouter(database=database, table=potatoes, model=Potato, create_schema=PotatoCreate)
    carrot_router = DatabasesCRUDRouter(database=database, table=carrots, model=Carrot, create_schema=CarrotCreate)
    app.include_router(potato_router)
    app.include_router(carrot_router)

    return app


if __name__ == '__main__':
    import uvicorn
    app = databases_implementation()

    uvicorn.run(app)