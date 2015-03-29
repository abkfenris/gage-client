import unittest
import json
import responses
import requests
from itsdangerous import JSONWebSignatureSerializer, BadSignature
from datetime import datetime as dt

from gage_client import Client
from gage_client.client import Client_0_1, AuthenticationError, SendError

password = 'password'
url_stub = 'http://riverflo.ws/api/0.1/'
gage_id = 5
s = JSONWebSignatureSerializer(password)
url = url_stub + 'gages/' + str(gage_id) + '/sample'
bad_password = 'badpassword'


def client_0_1_response_callback(request):
    #print request.body
    try:
        payload = s.loads(request.body)
    except BadSignature:
        print 'Bad Signature'
        output = {'error': 'unauthorized',
                  'message': 'bad signature'}
        return (401, {}, json.dumps(output))
    #print payload
    samples = payload['samples']
    output_samples = []
    count = 0
    for sample in samples:
        result_json = {
            'datetime': sample['datetime'],
            'id ': count,
            'sender_id': sample['sender_id'],
            'url': 'http://example.com/api/0.1/samples/(count)'.format(count=count),
            'value': sample['value']
        }
        output_samples.append(result_json)

    resp_body = {'gage': {'id': payload['gage']['id']},
                 'result': 'created',
                 'samples': output_samples}
    return (200, {}, json.dumps(resp_body))


class Test_Client_0_1(unittest.TestCase):

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
        self.assertEquals(len(self.client.readings()), 1)

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

class Test_Client_0_1_Ids(Test_Client_0_1):

    def testReading(self):
        datetime = str(dt.now())
        sensor = 'level'
        value = 4.2
        self.client.reading(sensor, datetime, value, id=1)
        self.assertEquals(len(self.client.samples), 1)
        print self.client.samples[0]
        self.assertEquals(self.client.samples[0]['type'], sensor)
        self.assertEquals(self.client.samples[0]['value'], value)
        self.assertEquals(self.client.samples[0]['datetime'], datetime)


class Test_Client_0_1_BadPassword(Test_Client_0_1):

    def setUp(self):
        responses.reset()
        self.client = Client(url, gage_id, bad_password)

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
        self.assertRaises(AuthenticationError, self.client.send_all)

class Test_Client_0_1_BadEndpoint(Test_Client_0_1):

    @responses.activate
    def testSend_All(self):
        responses.add(
            responses.POST, url,
            body='eyJhbGciOiJIUzI1NiJ9.eyJnYWdlIjp7ImlkIjoxfSwic2FtcGxlcyI6',
            content_type='application/txt',
            status=200
        )
        datetime = str(dt.now())
        sensor = 'level'
        value = 4.2
        self.client.reading(sensor, datetime, value)
        self.assertRaises(SendError, self.client.send_all)

if __name__ == '__main__':
    unittest.main()
