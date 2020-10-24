import requests
import json
import datetime
from PIL import Image

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
    return response.status_code

class Poopee:
    def __init__(self, user_id, serial_num, ip_addr):
        self._user_id = user_id
        self._serial_num = serial_num
        self._ip_addr = ip_addr
        self._url = 'https://dev.goodpoopee.com/'
        self._headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
    """
    save the success or failure of the dog's bowel movements
    POST at /{pet_id}/record
    """
    def pet_record(self, pet_id, result, image, token):
        """modify URL"""
        temp_url = self._url + 'pet/' + str(pet_id) + '/record'

        """create data"""
        now = datetime.datetime.now()
        timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
        temp_data = {
            'timestamp': timestamp,
            'result': result
        }

        """add access token at headers"""
        auth = "Bearer " + token
        temp_headers = {}
        temp_headers['Authorization'] = auth

        """prepare to send an image"""
        temp_file = [
            ('image', open(image,'rb'))
        ]

        """http request"""
        response = requests.request('POST', temp_url, headers=temp_headers, data=temp_data, files=temp_file)
        return response.status_code

    """
    log in poopee cam and get access token
    if poopee cam is not registered (code 404), please run Requests.ppcam_register
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
        
        if response.status_code == 404: # if ppcam is not registered, register ppcam and log in again
            response = _ppcam_register(self._url, self._ip_addr, self._serial_num, self._user_id, self._headers)
            if response.status_code == 200:
                response = requests.post(temp_url, headers=self._headers, data=json.dumps(temp_data))
            else:
                print("Register failed!: " + response.text.encode('utf8'))
                return response.status_code 

        if response.status_code == 200:
            response = response.json()
            return response
        else:
            print("Log in failed!: " + response.text.encode('utf8'))
            return response.status_code
    
    """
    polling at the server for connect
    GET at /polling
    """
    def ppcam_polling(self, ppcam_id, token):
        """modify URL"""
        temp_url = self._url + 'ppcam/' + str(ppcam_id) + '/polling'

        """add access token at headers"""
        auth = "Bearer " + token
        temp_headers = self._headers
        temp_headers['Authorization'] = auth

        """https requests"""
        response = requests.get(temp_url, headers=temp_headers)
        if response.status_code == 200:
            response = response.json()
            if 'pad' in response:
                del response['pad']['id']
                del response['pad']['ppcam_id']
                del response['pad']['user_id']
            if 'ppsnack' in response:
                response['feedback'] = response['ppsnack']['feedback']
                del response['ppsnack']
            return response
        else:
            print("Polling failed!: " + response.text.encode('utf8'))
            return response.status_code