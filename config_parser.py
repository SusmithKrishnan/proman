import configparser
import os
config = configparser.ConfigParser()
CONFIG_DIR = os.path.expanduser("~/.config/proman")
DATA_DIR = os.path.expanduser("~/proman-data")
CONFIG_FILE_PATH = os.path.join(CONFIG_DIR, 'proman.conf')


def write_config(data_dir=DATA_DIR):

    config["MAIN"] = {
        "config_dir":CONFIG_DIR,
        "namespace": "default",
        "data_dir": data_dir
    }
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)

    with open(CONFIG_FILE_PATH, 'w') as conf:
        config.write(conf)
    return


def read_config():
    config.read(CONFIG_FILE_PATH)
    return config['MAIN']


def if_cfg_file_exists():
    return os.path.exists(CONFIG_FILE_PATH)

