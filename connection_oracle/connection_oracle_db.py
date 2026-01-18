import oracledb
from dotenv import dotenv_values
from sqlalchemy import create_engine

config = dotenv_values("../.env")

USERNAME = config.get("USERNAME")
PASSWORD = config.get("PASSWORD")
HOST = config.get("HOST")
PORT = config.get("PORT")
DATABASE = config.get("DATABASE")

connection = oracledb.connect(
    user=USERNAME,
    password=PASSWORD,
    host=HOST,
    port=PORT,
    service_name=DATABASE
)

dsn = f"oracle+oracledb://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/?service_name={DATABASE}"
engine = create_engine(dsn)
