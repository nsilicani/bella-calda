from app.database import engine, Base
from app.models import user, order, driver

Base.metadata.create_all(bind=engine)
