from itsdangerous import JSONWebSignatureSerializer
import requests

class Client(object):
    def __init__(self, url, id, password):
        """
        Initialize a new client

        Parameters:
            url (str): Url for API endpoint
            id (int): Client ID number
            password (str): Shared password string for signature
        """
        self.url = url
        self.id = id
        self.password = password
        self.samples = {}

    def reading(self, sensor, dt, value):
        """
        Add a new reading to send at next connection

        Parameters:
            sensor (str): Type of sensor (level, current, voltage)
            dt (datetime string): Datetime string of sensor reading
            value (float): Float value of sensor reading
        """
        try:
            self.samples[sensor][dt] = value
        except KeyError:
            self.samples[sensor] = {}
            self.samples[sensor][dt] = value

    def send_all(self):
        """
        Send all samples to server
        """
        samples = []
        for sensor in self.samples:
            for dt in self.samples[sensor]:
                samples.append({'type': sensor,
                                'datetime': dt,
                                'value': self.samples[sensor][dt]})

        payload = {'samples': samples,
                   'gage': {'id': self.id}}

        s = JSONWebSignatureSerializer(self.password)

        data = s.dumps(payload)
        print 'sending:'
        print payload
        print 'Signature:'
        print data
        print 'to:'
        print self.url
