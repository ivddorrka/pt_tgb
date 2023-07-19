import json

def load_config(file_path):
    with open(file_path, 'r') as file:
        config_data = json.load(file)
    return config_data

config_file_path = 'config.json'
config = load_config(config_file_path)

telegram_bot_token = config['telegram_bot_token']
admin_ids = config['admin_ids']
SQLALCHEMY_DATABASE_URI = config['SQLALCHEMY_DATABASE_URI']
SECRET_KEY = config["SECRET_KEY"]
