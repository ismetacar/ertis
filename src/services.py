from src.generics.repository import ErtisGenericRepository


def init_services(app, settings):
    app.generic_service = ErtisGenericRepository(app.db)

    from src.custom_api.tokens import init_api
    init_api(app, settings)

    from src.custom_api.me import init_api
    init_api(app, settings)

    from src.custom_api.site_map import init_api
    init_api(app, settings)

    from src.custom_api.healtcheck import init_api
    init_api(app, settings)

    from src.custom_api.change_password import init_api
    init_api(app, settings)
