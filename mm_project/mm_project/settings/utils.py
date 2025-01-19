from pathlib import Path
from typing import get_type_hints

import yaml
import os

from mm_project.log_utils import write_error_log


class ConfigFromDict:
    @classmethod
    def from_dict(cls, data):
        obj = cls()
        type_hints = get_type_hints(cls)

        for key, value in data.items():
            # Will raise KeyError if an unexpected key is in the config data
            expected_type = type_hints[key]

            if not isinstance(value, expected_type):
                raise TypeError(f'Incorrect type for type {key}: expected {expected_type}, got {type(value)}')

            setattr(obj, key, value)

        return obj


class HTTPSSettings(ConfigFromDict):
    session_cookie_secure: bool
    csrf_cookie_secure: bool
    secure_ssl_redirect: bool
    secure_browser_xss_filter: bool
    session_cookie_samesite: str

    secure_hsts_seconds: int
    secure_hsts_include_subdomains: bool
    secure_hsts_preload: bool

    secure_content_type_nosniff: bool
    x_frame_options: str

    csp_default_src: list
    csp_script_src: list
    csp_style_src: list
    csp_img_src: list
    csp_frame_src: list

    permissions_policy: dict

    secure_referrer_policy: str

class DBSettings(ConfigFromDict):
    name: str
    user: str
    password: str


class Config:
    secret_key: str
    debug: bool
    allowed_hosts: list[str, ...]
    csrf_trusted_origins: list[str, ...]
    admins: list[list[str, str]]

    db_settings: DBSettings
    https_settings: HTTPSSettings or None = None

    @classmethod
    def from_yaml(cls, file_path: Path):
        if not os.path.exists(file_path):
            write_error_log(title="Missing Config File", message="Please copy example_config.yml to config.yml and fill out the required parameters")
            return

        with open(file_path) as stream:
            data = yaml.safe_load(stream)

        obj = cls()

        try:
            obj.secret_key = data['secret_key']
            obj.debug = data['debug']
            obj.admins = data['admins']
            obj.allowed_hosts = data['allowed_hosts']
            obj.csrf_trusted_origins = data['csrf_trusted_origins']

            obj.db_settings = DBSettings.from_dict(data['db_settings'])

            if data.get('https_settings'):
                obj.https_settings = HTTPSSettings.from_dict(data['https_settings'])

            return obj

        except KeyError as e:
            write_error_log(title="Invalid Config File", message=f"Missing key in config.yml; {e} ")
            return


