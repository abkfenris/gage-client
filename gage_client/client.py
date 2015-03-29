from itsdangerous import JSONWebSignatureSerializer
import requests
import logging

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
            logging.debug('Creating Client_0_1 for API version 0.1')
            return Client_0_1.__new__(Client_0_1, url, id, password)
        logging.error('Did not create Client based on url')

    def __init__(self, url, id, password):
        """
        Initialize a new client

        Parameters:
            url (str): URL for aPI endpoint
            id (int): Client ID number
            password (str): Password string to submit samples
        """
        logging.error('__init__ not implemented on generic Client class')
        raise NotImplementedError

    def reading(self, sensor, dt, value):
        """
        Add a new reading to the ones the Client will send to the server
        """
        logging.error('reading method not implemented on generic Client class')
        raise NotImplementedError

    def send_all(self):
        logging.error('send_all method not implemented on generic Client class')
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
        logging.debug('Client_0_1 initialized for {url} and gage id {id}'.format(url=url, id=id))

    def reading(self, sensor, dt, value, id=None):
        """
        Add a new reading to send at next connection

        Parameters:
            sensor (str): Type of sensor (level, current, voltage)
            dt (datetime string): Datetime string of sensor reading
            value (float): Float value of sensor reading
            id (int): Integer identifying sample, if not given, just use length of sample list
        """
        if id is None:
            self.samples.append({'type': sensor,
                                 'datetime': dt,
                                 'value': value,
                                 'sender_id': len(self.samples)})
        else:
            self.samples.append({'type': sensor,
                                 'datetime': dt,
                                 'value': value,
                                 'sender_id': id})
        return True

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
            sucessful_ids = []
            for sample in r.json()['samples']:
                sucessful_ids.append(sample['sender_id'])
            print sucessful_ids
            samples = self.samples
            for x in range(len(samples)):
                if samples[x]['sender_id'] in sucessful_ids:
                    self.samples.pop(x)
            print self.samples
            return (True, sucessful_ids)

        return False
