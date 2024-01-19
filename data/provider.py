import databases
import sqlalchemy
from abc import *


class Provider(ABC):

    @abstractmethod
    def get_data(self, start: str, end: str):
        pass


class DataProvider(Provider):
    def __init__(self):
        self.metadata = sqlalchemy.MetaData()
        self.database_url = "sqlite:///test.db"
        self.ohlcv_table = sqlalchemy.Table(
            "ohlcv",
            self.metadata,
            sqlalchemy.Column("id", sqlalchemy.Float, primary_key=True),
            sqlalchemy.Column("coin", sqlalchemy.String, unique=True),
            sqlalchemy.Column("open", sqlalchemy.Float),
            sqlalchemy.Column("high", sqlalchemy.Float),
            sqlalchemy.Column("low", sqlalchemy.Float),
            sqlalchemy.Column("close", sqlalchemy.Float),
            sqlalchemy.Column("volume", sqlalchemy.Float),
            sqlalchemy.Column("date", sqlalchemy.DateTime),
        )
        self.engine = sqlalchemy.create_engine(
           self.database_url , connect_args={"check_same_thread": False}
        )

        self.metadata.create_all(self.engine)
        database = databases.Database(
            self.database_url, force_rollback=False
        ).connect()


    def get_data(self, start: str, end: str):
          pass