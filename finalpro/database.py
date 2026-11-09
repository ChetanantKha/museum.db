from sqlmodel import create_engine, SQLModel

engine = create_engine("sqlite:///database.db")

def init_db():
    SQLModel.metadata.create_all(engine)