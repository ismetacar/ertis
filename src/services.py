from src.generics.repository import ErtisGenericRepository


def init_services(app, settings):
    app.generic_service = ErtisGenericRepository(app.db)
