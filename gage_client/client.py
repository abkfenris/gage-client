from itsdangerous import JSONWebSignatureSerializer
import requests

class AuthenticationError(Exception):
    """
    Failed to authenticate with server
    """
    def __init__(self, arg):
        self.args = arg


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
        self.serializer = JSONWebSignatureSerializer(password)
        self.samples = []

    def reading(self, sensor, dt, value):
        """
        Add a new reading to send at next connection

        Parameters:
            sensor (str): Type of sensor (level, current, voltage)
            dt (datetime string): Datetime string of sensor reading
            value (float): Float value of sensor reading
        """
        self.samples.append({'type': sensor,
                                 'datetime': dt,
                                 'value': value})

    def send_all(self):
        """
        Send all samples to server
        """

        payload = {'samples': self.samples,
                   'gage': {'id': self.id}}

        data = self.serializer.dumps(payload)

        r = requests.post(self.url, data=data)

        print r.json()

        if r.status_code is 401:
            raise AuthenticationError
        elif r.status_code is 200 and r.json()['result'] == 'created':
            return (True, r.json()['samples'])
        return False
