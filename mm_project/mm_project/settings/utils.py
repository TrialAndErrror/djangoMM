import errno
import json
import os


def load_config_data(config_path):
    """
    Load configuration data from json file in settings folder.

    :return: dict
    """

    if not os.path.exists(config_path):
        """
        Raise error if config_data is not found.

        To remedy this error, copy sample_config_data.json to config_data.json and fill out required data.
        """
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), config_path)
    else:
        with open(config_path, 'r') as config_file:
            config_data = json.load(config_file)
    return config_data
