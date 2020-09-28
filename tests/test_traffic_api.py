#!/usr/bin/env python

import datetime
import os
import sys
import unittest
import responses
import codecs
import herepy

class TrafficApiTest(unittest.TestCase):

    def setUp(self):
        api = herepy.TrafficApi('api_key')
        self._api = api


    def test_initiation(self):
        self.assertIsInstance(self._api, herepy.TrafficApi)
        self.assertEqual(self._api._api_key, 'api_key')


    @responses.activate
    def test_incidents_in_bounding_box_success(self):
        with codecs.open('testdata/models/traffic_incidents_bounding_box.json', mode='r', encoding='utf-8') as f:
            expectedResponse = f.read()
        responses.add(responses.GET, 'https://traffic.ls.hereapi.com/traffic/6.0/incidents.json',
                  expectedResponse, status=200)
        response = self._api.incidents_in_bounding_box(top_left=[52.5311, 13.3644], bottom_right=[52.5114, 13.4035],
                            criticality=[herepy.here_enum.IncidentsCriticality.minor, herepy.here_enum.IncidentsCriticality.major, herepy.here_enum.IncidentsCriticality.critical])
        self.assertTrue(response)
        self.assertIsInstance(response, herepy.TrafficIncidentResponse)


    @responses.activate
    def test_incidents_in_bounding_box_fails(self):
        with codecs.open('testdata/models/traffic_incidents_error.json', mode='r', encoding='utf-8') as f:
            expectedResponse = f.read()
        responses.add(responses.GET, 'https://traffic.ls.hereapi.com/traffic/6.0/incidents.json',
                  expectedResponse, status=200)
        with self.assertRaises(herepy.UnauthorizedError):
            self._api.incidents_in_bounding_box(top_left=[52.5311, 13.3644], bottom_right=[52.5114, 13.4035],
                    criticality=[herepy.here_enum.IncidentsCriticality.minor])