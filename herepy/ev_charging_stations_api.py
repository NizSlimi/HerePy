#!/usr/bin/env python

import sys
import json
import requests

from typing import List
from herepy.here_enum import EVStationConnectorTypes
from herepy.utils import Utils
from herepy.error import HEREError
from herepy.models import EVChargingStationsResponse


class EVChargingStationsApi():
    """A python interface into the HERE EV Charging Stations API"""

    def __init__(self,
                 app_id: str=None,
                 app_code: str=None,
                 timeout: int=None):
        """Returns a EVChargingStationsApi instance.
        Args:
          app_id (str):
            App Id taken from HERE Developer Portal.
          app_code (str):
            API Code taken from HERE Developer Portal.
          timeout (int):
            Timeout limit for requests.
        """

        self._app_id = app_id
        self._app_code = app_code
        if timeout:
            self._timeout = timeout
        else:
            self._timeout = 20
        self._base_url = 'https://ev-v2.cit.cc.api.here.com/ev/'


    def __get(self, base_url, data, response_cls):
        url = Utils.build_url(base_url, extra_params=data)
        response = requests.get(url, timeout=self._timeout)
        json_data = json.loads(response.content.decode('utf8'))
        if json_data.get('evStations') is not None:
            return response_cls.new_from_jsondict(json_data)
        else:
            raise error_from_ev_charging_service_error(json_data)


    def __connector_types_str(self, connector_types: List[EVStationConnectorTypes]):
        connector_types_str = ''
        for connector_type in connector_types:
            connector_types_str += str.format('{0},', connector_type._value_)
        connector_types_str = connector_types_str[:-1]
        return connector_types_str


    def get_stations_circular_search(self,
                                     latitude: float,
                                     longitude: float,
                                     radius: int,
                                     connectortypes: List[EVStationConnectorTypes]=None):
        if connectortypes:
            connector_types_str = self.__connector_types_str(connectortypes)
            data = {'app_id': self._app_id,
                    'app_code': self._app_code,
                    'prox': str.format('{0},{1},{2}', latitude, longitude, radius),
                    'connectortype': connector_types_str}
        else:
            data = {'app_id': self._app_id,
                    'app_code': self._app_code,
                    'prox': str.format('{0},{1},{2}', latitude, longitude, radius)}
        response = self.__get(self._base_url + 'stations.json', data, EVChargingStationsResponse)
        return response


class UnauthorizedError(HEREError):

    """Unauthorized Error Type.

    This error is returned if the specified token was invalid or no contract
    could be found for this token.
    """


# pylint: disable=R0911
def error_from_ev_charging_service_error(json_data: dict):
    """Return the correct subclass for ev charging errors"""

    if 'Type' in json_data:
        error_type = json_data['Type']
        message = json_data['Message']

        if error_type == 'Unauthorized':
            return UnauthorizedError(message)
    # pylint: disable=W0212
    return HEREError('Error occured on ' + sys._getframe(1).f_code.co_name)