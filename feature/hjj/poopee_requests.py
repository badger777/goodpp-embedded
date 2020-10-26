import requests
import json
import datetime

"""
register poopee cam for log in
POST at /register
"""
def _ppcam_register(url, ip_addr, serial_num, user_id, headers):
    """modify URL"""
    temp_url = url + 'ppcam/register'
    
    """create data"""
    temp_data = {
        'ip_address': ip_addr,
        'serial_num': serial_num,
        'user_id': user_id
    }

    """https requests"""
    response = requests.post(temp_url, headers=headers, data=json.dumps(temp_data))
    return response.status_code # return type 'int'

class Poopee:
    def __init__(self, user_id, serial_num, ip_addr, image_name):
        self._user_id = user_id
        self._serial_num = serial_num
        self._ip_addr = ip_addr
        self._image_name = image_name
        self._url = 'https://dev.goodpoopee.com/'
        self._headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        """check ppcam is registered"""
        temp_response = requests.post(
            self._url + 'ppcam/login',
            headers=self._headers,
            data=json.dumps({'serial_num': self._serial_num})
        )
        temp_code = temp_response.status_code
        """if ppcam is not registered(http 404), try to register ppcam until ppcam is registered"""
        if temp_code == 404:
            while temp_code != 200:
                print('Try to register poopee cam...')
                temp_code = _ppcam_register(self._url, self._ip_addr, self._serial_num, self._user_id, self._headers)
            print('Poopee cam is registered!')
        print('Poopee class is initialized!')
    
    """
    record the success of the dog's bowel movements
    POST at /{pet_id}/record
    """
    def pet_record(self, pet_id, token):
        """modify URL"""
        temp_url = self._url + 'pet/' + str(pet_id) + '/record'

        """create data"""
        now = datetime.datetime.now()
        timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
        temp_data = {
            'timestamp': timestamp,
            'result': 'SUCCESS'
        }

        """add access token at headers"""
        auth = "Bearer " + token
        temp_headers = {}
        temp_headers['Authorization'] = auth

        """prepare to send an image"""
        temp_file = [
            ('image', open(self._image_name,'rb'))
        ]

        """http request"""
        response = requests.request('POST', temp_url, headers=temp_headers, data=temp_data, files=temp_file)
        if response.status_code == 200:
            print('Recording success!')
        else:
            print('Recording failed!: ' + response.text.encode('utf8'))
        return response.status_code # return type 'int' 

    """
    log in poopee cam and get access token
    POST at /login
    """
    def ppcam_login(self):
        """modify URL"""
        temp_url = self._url + 'ppcam/login'

        """create date"""
        temp_data = {
            'serial_num': self._serial_num
        }

        """https requests"""
        response = requests.post(temp_url, headers=self._headers, data=json.dumps(temp_data))
        if response.status_code == 200:
            response = response.json()
            print('Log in success!')
            return response # return type 'dict'
        else:
            print('Log in failed!: ' + response.text.encode('utf8'))
            return response.status_code # return type 'int'
    
    """
    polling at the server for connect
    GET at /polling
    """
    def ppcam_polling(self, ppcam_id, token):
        """modify URL"""
        temp_url = self._url + 'ppcam/' + str(ppcam_id) + '/polling'

        """add access token at headers"""
        auth = 'Bearer ' + token
        temp_headers = self._headers
        temp_headers['Authorization'] = auth

        """https requests"""
        response = requests.get(temp_url, headers=temp_headers)
        if response.status_code == 200:
            response = response.json()
            if 'feeding' in response:
                response['feeding'] = int(response['feeding'])
            if 'pad' in response:
                response['pad'] = {
                    'ldx': response['pad']['ldx'],
                    'ldy': response['pad']['ldy'],
                    'lux': response['pad']['lux'],
                    'luy': response['pad']['luy'],
                    'rdx': response['pad']['rdx'],
                    'rdy': response['pad']['rdy'],
                    'rux': response['pad']['rux'],
                    'ruy': response['pad']['ruy']   
                }
            if 'ppsnack' in response:
                response['feedback'] = response['ppsnack']['feedback']
                del response['ppsnack']
            print('Polling success!')
            return response # return type 'dict'
        else:
            print('Polling failed!: ' + response.text.encode('utf8'))
            return response.status_code # return type 'int'