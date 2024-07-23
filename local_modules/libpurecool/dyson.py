"""Dyson Pure Cool Link library."""

# pylint: disable=too-many-public-methods,too-many-instance-attributes

import json
import logging
from pathlib import Path
from uuid import uuid4

import requests

from libpurecool.dyson_360_eye import Dyson360Eye
from libpurecool.dyson_pure_cool import DysonPureCool
from libpurecool.dyson_pure_cool_link import DysonPureCoolLink
from libpurecool.dyson_pure_hotcool import DysonPureHotCool
from libpurecool.dyson_pure_hotcool_link import DysonPureHotCoolLink
from libpurecool.exceptions import DysonNotLoggedInException
from libpurecool.utils import (
    is_360_eye_device,
    is_dyson_pure_cool_device,
    is_heating_device,
    is_heating_device_v2,
)

_LOGGER = logging.getLogger(__name__)

DYSON_API_URL = "appapi.cp.dyson.com"
DYSON_API_URL_CN = "appapi.cp.dyson.cn"
DYSON_API_USER_AGENT = f"android_client_{uuid4()}"

DYSON_VERSION_PATH = "v1/provisioningservice/application/Android/version"
DYSON_USERSTATUS_PATH = "v3/userregistration/email/userstatus"
DYSON_AUTH_CHALLENGE_PATH = "v3/userregistration/email/auth"
DYSON_VERIFY_PATH = "v3/userregistration/email/verify"
DYSON_DEVICES_PATH = "v2/provisioningservice/manifest"


class DysonAccount:
    """Dyson account."""

    def __init__(self, email, password, country):
        """Create a new Dyson account.

        :param email: User email
        :param password: User password
        :param country: 2 characters language code
        """
        self._email = email
        self._password = password
        self._country = country
        self._cached_credentials = False
        self._challenge_id = None
        self._token_type = None
        self._token = None
        self._account = None
        self._user_agent = DYSON_API_USER_AGENT
        if country == "CN":
            self._dyson_api_host = DYSON_API_URL_CN
        else:
            self._dyson_api_host = DYSON_API_URL

    def process_http_response(self, response):
        if response.status_code == 429:
            raise DysonNotLoggedInException(f'API request failure. Probably rate limited. Please try later. ({response.status_code}, {response.reason})')
        if response.status_code == 401:
            if self._cached_credentials:
                raise DysonNotLoggedInException(f'API request failure. Cached credentials might be expired. ({response.status_code}, {response.reason})')
            else:
                raise DysonNotLoggedInException(f'API request failure. Invalid credentials or IP blocked. ({response.status_code}, {response.reason})')
        if response.status_code != 200:
            raise DysonNotLoggedInException(f'API request failure. Reason unknown. ({response.status_code}, {response.reason}')
        return response.text

    def version(self):
        """Retrieve Dyson API version."""
        r = requests.get(f'https://{self._dyson_api_host}/{DYSON_VERSION_PATH}?country={self._country}',
                         headers={'User-Agent': self._user_agent})
        self.process_http_response(r)
        return r.text

    def userstatus(self):
        """Get status of API user."""
        r = requests.post(f'https://{self._dyson_api_host}/{DYSON_USERSTATUS_PATH}?country={self._country}',
                          headers={'User-Agent': self._user_agent},
                          json={'Email': self._email})
        self.process_http_response(r)
        return json.loads(r.text)

    def _get_challenge(self):
        """Get API authentication token."""
        r = requests.post(f'https://{self._dyson_api_host}/{DYSON_AUTH_CHALLENGE_PATH}?country={self._country}',
                          headers={'User-Agent': self._user_agent},
                          json={'Email': self._email})
        self.process_http_response(r)
        return json.loads(r.text)['challengeId']

    def login(self):
        """Login to the Dyson API and retrieve auth token."""
        cache_dir = Path.home() / '.cache'
        Path(cache_dir).mkdir(exist_ok=True)
        if Path(cache_dir / 'dyson_api_authorization').exists():
            self._cached_credentials = True
        else:
            self._cached_credentials = False
            self._challenge_id = self._get_challenge()
            otp_code = input("Enter OTP code sent to your email address: ")
            r = requests.post(f'https://{self._dyson_api_host}/{DYSON_VERIFY_PATH}?country={self._country}',
                              headers={'User-Agent': self._user_agent},
                              json={'Email': self._email,
                                    'Password': self._password,
                                    'challengeId': self._challenge_id,
                                    'otpCode': otp_code})
            self.process_http_response(r)
            Path(cache_dir / 'dyson_api_authorization').write_text(r.text)
        auth_data = json.loads(Path(cache_dir / 'dyson_api_authorization').read_text())
        self._account = auth_data['account']
        self._token = auth_data['token']
        self._token_type = auth_data['tokenType']

    def devices(self):
        """Return all devices linked to the account."""
        if self._token is None:
            raise DysonNotLoggedInException("Not logged in to Dyson Web Services.")
        r = requests.get(f'https://{self._dyson_api_host}/{DYSON_DEVICES_PATH}?country={self._country}',
                         headers={'User-Agent': self._user_agent,
                                  'Authorization': f'{self._token_type} {self._token}'})
        self.process_http_response(r)
        devices = []
        for device in r.json():
            if is_360_eye_device(device):
                dyson_device = Dyson360Eye(device)
            elif is_heating_device(device):
                dyson_device = DysonPureHotCoolLink(device)
            else:
                dyson_device = DysonPureCoolLink(device)
            devices.append(dyson_device)

        for device_v2 in r.json():
            if is_dyson_pure_cool_device(device_v2):
                devices.append(DysonPureCool(device_v2))
            elif is_heating_device_v2(device_v2):
                devices.append(DysonPureHotCool(device_v2))

        return devices


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    d = DysonAccount("sven@rexkramer.de", "wgzvwquXHBTWEtwsfQwNy8pC", "DE")
    # print(d.version())
    # print(d.userstatus())
    d.login()


    def on_message(msg):
        print(msg)

    for i in d.devices():
        i.connect("dyson.rexkramer.de")
        # i.turn_off()
        # print(i.serial)
        # print(i.credentials)
        # i.disable_oscillation()
        # i.enable_oscillation()
        i.add_message_listener(on_message)
        from time import sleep
        sleep(60)
        i.disconnect()
