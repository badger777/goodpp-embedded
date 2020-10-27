import json
import socket
import threading
from bluetooth import *
from time import sleep

FOOD = []

def handle_client(client_socket, bluetooth_socket):
    try:
        while True:
            data = client_socket.recv(4)
            data = data.decode('utf-8')
            print('Received ' + data)
            for _ in range(int(data)):
                FOOD.append('on')
            print(len(FOOD))
    except:
        print('Socket closed!')

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
    json_path = 'poopee_data.json'

    json_data = read_json(json_path)
    mac_address = json_data['mac_address']

    HOST = '127.0.0.1'
    PORT = 9999

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print("Poopee snack bar server start!")

    while True:
        try:
            bluetooth_socket = BluetoothSocket(RFCOMM)
            bluetooth_socket.connect((mac_address, 1))
            print("Bluetooth connected!")
            while True:
                print('waiting')
                client_socket, _ = server_socket.accept()
                t = threading.Thread(target=handle_client, args=(client_socket, bluetooth_socket, ))
                t.start()
                # bluetooth_socket.send("on")
                # sleep(3)
        except KeyboardInterrupt:
            server_socket.close()
            bluetooth_socket.close()
            return _
        except:
            print("Bluetooth not connected... retry...")
            sleep(1)        

if __name__ == '__main__':
    main()