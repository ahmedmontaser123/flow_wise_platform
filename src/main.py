from helpers import get_settings
from models.db.connection_database import *
from models.db.flow_wise.schema import Base

print("Base metadata:", Base)


app_settings = get_settings()
print(app_settings.PGADMIN_DEFAULT_PASSWORD)
print(DATABASE_URL)