from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///commands.db')
engine.raw_connection().connection.text_factory = str
session = sessionmaker(bind=engine)()
