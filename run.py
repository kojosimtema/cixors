from api import create_app
from api.main.config.config import config_dict

app = create_app(config=config_dict['prod'])
# app = create_app()

if __name__ == '__main__':
    app.run()