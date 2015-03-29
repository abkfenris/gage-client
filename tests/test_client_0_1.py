import unittest
import json
import responses
import requests
from itsdangerous import JSONWebSignatureSerializer, BadSignature
from datetime import datetime as dt

from gage_client import Client
from gage_client.client import Client_0_1, AuthenticationError

password = 'password'
url_stub = 'http://riverflo.ws/api/0.1/'
gage_id = 5
s = JSONWebSignatureSerializer(password)
url = url_stub + 'gages/' + str(gage_id) + '/sample'
bad_password = 'badpassword'


def client_0_1_response_callback(request):
    print request.body
    try:
        payload = s.loads(request.body)
    except BadSignature:
        print 'Bad Signature'
        return (401, {}, json.dumps({'error': 'unauthorized',
                                     'message': 'bad signature'}))
    print payload
    samples = payload['samples']
    output = []
    count = 0
    print samples
    return (200, {}, json.dumps(resp_body))


class Client_0_1TestCase(unittest.TestCase):

    def setUp(self):
        responses.reset()
        self.client = Client(url, gage_id, password)

    def testVersion(self):
        self.assertEqual(type(self.client), Client_0_1)

    def testReading(self):
        datetime = str(dt.now())
        sensor = 'level'
        value = 4.2
        self.client.reading(sensor, datetime, value)
        self.assertEquals(len(self.client.samples), 1)
        print self.client.samples[0]
        self.assertEquals(self.client.samples[0]['type'], sensor)
        self.assertEquals(self.client.samples[0]['value'], value)
        self.assertEquals(self.client.samples[0]['datetime'], datetime)

    @responses.activate
    def testSend_All(self):
        responses.add_callback(
            responses.POST, url,
            callback=client_0_1_response_callback,
            content_type='application/json'
        )
        datetime = str(dt.now())
        sensor = 'level'
        value = 4.2
        self.client.reading(sensor, datetime, value)
        self.client.send_all()

if __name__ == '__main__':
    unittest.main()
