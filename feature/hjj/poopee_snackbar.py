import json
import socket
import threading
from bluetooth import *
from time import sleep

"""stack for feeding"""
FEEDING = []

"""receive a feeding signal from other python files via socket"""
def handle_client(client_socket):
    try:
        while True:
            print('Waiting for a feeding signal...')
            data = client_socket.recv(4)
            data = data.decode('utf-8')
            print('Received ' + data)
            for _ in range(int(data)):
                FEEDING.append('on') # push on stack
    except:
        print('Socket closed!')

"""connect bluetooth and send a feeding signal to the poopee snack bar"""
def connect_bluetooth(mac_address):
    while True: # loop for bluetooth connect
        try:
            bluetooth_socket = BluetoothSocket(RFCOMM)
            bluetooth_socket.connect((mac_address, 1))
            print('Bluetooth connected!')
            while True: # loop for feeding when bluetooth is connected
                temp_len = len(FEEDING)
                print('Number of remaining feeding: ' + temp_len)
                if temp_len > 0:
                    bluetooth_socket.send(FEEDING.pop()) # pop on stack
                    sleep(3)
                sleep(1)
        except:
            print("Bluetooth not connected... retry...")
            sleep(1)

"""read a json file when 'poopee_polling.py' file does not write a json file"""
def read_json(file_path):
    while True:
        try:
            with open(file_path, 'r') as json_file:
                json_data = json.load(json_file)
                print('Success to read a json file!')
                return json_data
        except:
            print('Fail to read json file!')

def main():
    # """for bluetooth"""
    # json_path = 'poopee_data.json'
    # json_data = read_json(json_path)

    # bt_thread = threading.Thread(target=connect_bluetooth, args=(json_data['mac_address'], ))
    # bt_thread.start() 

    """for socket communication"""
    HOST = '127.0.0.1'
    PORT = 9999

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print('Poopee snack bar server start!')

    while True:
        print('Waiting for socket communication...')
        client_socket, _ = server_socket.accept()
        t = threading.Thread(target=handle_client, args=(client_socket, ))
        t.start()
    
    server_socket.close()
                   

if __name__ == '__main__':
    main()