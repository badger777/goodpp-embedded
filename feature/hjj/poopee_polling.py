import json
from time import sleep
from poopee_requests import Poopee

def main():
    with open('poopee_data.json') as json_file:
        json_data = json.load(json_file)
        serial_num, user_id, ip_addr = json_data['serial_num'], json_data['user_id'], json_data['ip_addr']

    poopee = Poopee(user_id, serial_num, ip_addr)
    response = poopee.ppcam_login()
    if str(type(response)) == "<class 'dict'>":
        token = response['device_access_token']
        ppcam_id = response['ppcam_id']
        pet_id = response['pet_id']
    else:
        return response

    while True:
        response = poopee.ppcam_polling(ppcam_id, token)
        # 401일때 코드 추가 필요
        print(response)
        
        if str(type(response)) == "<class 'dict'>": 
            if 'feeding' in response:
                for i in range(response['feeding']):
                    print('feeding') # 간식 주기
                    sleep(1)
            if 'pad' in response:
                print('pad') # json 업데이트
            if 'feedback' in response:
                print('feedback') # json 업데이트
        else:
            return response

        sleep(3)

if __name__ == '__main__':
    main()