import json
from time import sleep
from poopee_requests import Poopee

def read_json(file_path):
    with open(file_path, 'r') as json_file:
        json_data = json.load(json_file)
        print('Success to read a json file!')
        return json_data

def write_json(file_path, json_data):
    with open(file_path, 'w') as json_file:
        json.dump(json_data, json_file, indent=4)
        print('Success to write a json file!')

def main():
    """set json file path"""
    file_path = 'poopee_data.json'

    """set variables to initialize class"""
    json_data = read_json(file_path)
    serial_num, user_id, ip_addr, image_name = json_data['serial_num'], json_data['user_id'], json_data['ip_addr'], json_data['image_name']

    """load class"""
    poopee = Poopee(user_id, serial_num, ip_addr, image_name)

    """log in ppcam"""
    response = poopee.ppcam_login()
    if str(type(response)) == "<class 'dict'>":
        token = response['device_access_token']
        ppcam_id = response['ppcam_id']
        # pet_id = response['pet_id']
    else:
        return response # if login fails, the program is terminated

    """polling every 3 seconds"""
    while True:
        response = poopee.ppcam_polling(ppcam_id, token)
        
        """
        when the token expires(http 401), the token is reissued
        this code brings security issues, so we will need to fix the code later
        """
        if response == 401:
           response = poopee.ppcam_login()
           token = response['device_access_token']
           response = poopee.ppcam_polling(ppcam_id, token)
        
        if str(type(response)) == "<class 'dict'>": 
            """give snacks as much as requested by the user"""
            if 'feeding' in response:
                for _ in range(response['feeding']):
                    print('feeding') # 간식 주기
                    sleep(1)
            """update pad data in json file"""
            if 'pad' in response:
                json_data = read_json(file_path)
                json_data['pad'] = response['pad']
                write_json(file_path, json_data)
                print('Update pad data!')
            """update feedback data in json file"""
            if 'feedback' in response:
                json_data = read_json(file_path)
                json_data['feedback'] = response['feedback']
                write_json(file_path, json_data)
                print('Update feedback data!') 
        else:
            return response # if polling fails, the program is terminated
        
        sleep(3)

if __name__ == '__main__':
    main()