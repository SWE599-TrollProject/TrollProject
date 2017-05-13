import configparser
import os


def get_config(root_path):
    config = configparser.ConfigParser()
    config_path = os.path.join(root_path, 'config/config.ini')
    config.read(config_path)
    return config