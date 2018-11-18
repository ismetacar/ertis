import optparse

from confs.development import development_config
from confs.local import local_config
from confs.production import production_config
from src import create_app
from src.resources.security import ErtisSecurityManager

CONFIG_LOOKUP = {
    'local': local_config,
    'development': development_config,
    'production': production_config
}

parser = optparse.OptionParser()

parser.add_option("--config", default="local")


def config_settings():
    options, _ = parser.parse_args()
    return CONFIG_LOOKUP[options.config]


settings = config_settings()

app = create_app(settings)
app.security_manager = ErtisSecurityManager(app.db)

app.debug = settings['debug']
app.secret_key = settings['application_secret']
app.port = settings['port']
app.env = settings['environment']

if __name__ == '__main__':
    app.run(port=app.port)
