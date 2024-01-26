import databases
import sqlalchemy
import pandas as pd

class DataProvider:
    def __init__(self):
        self.metadata = sqlalchemy.MetaData()
        self.database_url = "sqlite:///test.db"
        self.btc4h_table = sqlalchemy.Table(
            "btc4h",
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
            self.database_url, connect_args={"check_same_thread": False}
        )

        self.metadata.create_all(self.engine)
        self.database = databases.Database(
            self.database_url, force_rollback=False
        )
        self.database.connect()

    async def get_data(self, start: str, end: str):

        query = self.btc4h_table.select().where(
            self.btc4h_table.c.date.between(start, end)
        )
        print(query)
        results = await self.database.fetch_all(query)

        pd.DataFrame(results)
