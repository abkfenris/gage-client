from itsdangerous import JSONWebSignatureSerializer
import requests

class AuthenticationError(Exception):
    """
    Failed to authenticate with server
    """
    def __init__(self, arg):
        self.args = arg


class Client(object):
    """
    Generic API Client
    """
    def __new__(cls, url, id, password):
        """
        Builds the right client class for the API based on the url given
        """
        if '/0.1' in url:
            return Client_0_1.__new__(Client_0_1, url, id, password)

    def __init__(self, url, id, password):
        """
        Initialize a new client

        Parameters:
            url (str): URL for aPI endpoint
            id (int): Client ID number
            password (str): Password string to submit samples
        """
        raise NotImplementedError

    def reading(self, sensor, dt, value):
        """
        Add a new reading to the ones the Client will send to the server
        """
        raise NotImplementedError

    def send_all(self):
        raise NotImplementedError


class Client_0_1(Client):
    def __new__(cls, url, id, password):
        instance = object.__new__(Client_0_1)
        return instance

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
