import errno
import json
import os

from . import CONFIG_PATH


def load_config_data():
    """
    Load configuration data from json file in settings folder.

    :return: dict
    """

    if not os.path.exists(CONFIG_PATH):
        """
        Raise error if config_data is not found.

        To remedy this error, copy sample_config_data.json to config_data.json and fill out required data.
        """
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), CONFIG_PATH)
    else:
        with open(CONFIG_PATH, 'r') as config_file:
            config_data = json.load(config_file)
    return config_data
