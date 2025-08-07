from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URI = 'mysql+mysqlclient://root:Azeemmysql@1237@localhost:3306/tododb'
engine = create_engine(SQLALCHEMY_DATABASE_URI)

Session = sessionmaker(bind=engine, autocommit=False,autoflush=False)
Base = declarative_base()