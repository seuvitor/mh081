DB_FILE = "mh081.db"
DB_URI = "sqlite:///" + DB_FILE

from sqlalchemy import MetaData
metadata = MetaData(DB_URI)
