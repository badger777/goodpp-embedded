import numpy as np
import cv2
import time
import json
import os
import collections
from poopee_requests import Poopee
from PIL import Image
from edgetpu.detection.engine import DetectionEngine
from edgetpu.classification.engine import ClassificationEngine
# from bluetooth import *

"""load labels"""
def load_labels(path):
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        labels = {}
        for line in lines:
            id, name = line.strip().split(maxsplit=1)
            labels[int(id)] = name
    return labels

"""draws the bounding box and label"""
def annotate_objects(frame, coordinate, label_text, box_color):
    box_left, box_top, box_right, box_bottom = coordinate

    cv2.rectangle(frame, (box_left, box_top), (box_right, box_bottom), box_color, 2)
    (txt_w, txt_h), base = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_PLAIN, 2, 3)
    cv2.rectangle(frame, (box_left - 1, box_top - txt_h), (box_left + txt_w, box_top + txt_h), box_color, -1)
    cv2.putText(frame, label_text, (box_left, box_top+base), cv2.FONT_HERSHEY_PLAIN, 2, (255,255,255), 2)

"""draws the bounding box and label for the pad"""
def annotate_pad(frame, coordinate, box_color):
    points = np.array([
        [coordinate['lux'], coordinate['luy']],
        [coordinate['rux'], coordinate['ruy']],
        [coordinate['rdx'], coordinate['rdy']],
        [coordinate['ldx'], coordinate['ldy']]
    ], np.int32)
    label_text = 'pad'
    
    cv2.polylines(frame, [points], True, box_color, 2)
    (txt_w, txt_h), base = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_PLAIN, 2, 3)
    cv2.rectangle(frame, (coordinate['lux'] - 1, coordinate['luy'] - txt_h), (coordinate['lux'] + txt_w, coordinate['luy'] + txt_h), box_color, -1)
    cv2.putText(frame, label_text, (coordinate['lux'], coordinate['luy']+base), cv2.FONT_HERSHEY_PLAIN, 2, (255,255,255), 2)


"""crop the image to 224*224 and return"""
def crop_image(image, coordinate):
    y = coordinate[3] - coordinate[1]
    x = coordinate[2] - coordinate[0]
    if x >= y:
        gap = (x - y)/2.0
        coordinate[1] -= gap
        coordinate[3] += gap
    else:
        gap = (y - x)/2.0
        coordinate[0] -= gap
        coordinate[2] += gap

    coordinate = tuple(map(int, coordinate))
    image = image.crop(coordinate).resize((224, 224))
    return image

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

"""record the success of the dog's bowel movements to server"""
def send_result(poopee, image, pet_id, token, image_name):
    image.save(image_name)

    response = poopee.pet_record(pet_id, token)
    """
    when the token expires(http 401), the token is reissued
    this code brings security issues, so we will need to fix the code later
    """
    if response == 401:
        response = poopee.ppcam_login()
        token = response['device_access_token']
        response = poopee.pet_record(pet_id, token)

    try:
        os.remove(image_name)
    except:
        print('Failed to delete image!')
    return response, token

def main():
    """set variables"""
    video_number = 2
    label_path = 'coco_labels.txt'
    model_path_for_object = 'mobilenet_ssd_v2_coco_quant_postprocess_edgetpu.tflite'
    model_path_for_poopee = 'poopee_edgetpu.tflite'
    threshold = 0.4
    # mac_address = '' # initializing for bluetooth connection
    prevTime = 0 # initializing for calculating fps
    box_colors = {} # initializing for setting color
    pad_coordinate = {}
    json_path = 'poopee_data.json'
    
    """set variables to initialize class"""
    json_data = read_json(json_path)
    serial_num, user_id, ip_addr, image_name = json_data['serial_num'], json_data['user_id'], json_data['ip_addr'], json_data['image_name']

    """set variables to draw the bounding box and label for the pad"""
    # pad_color = [int(j) for j in np.random.randint(0,255, 3)] 

    """load class"""
    poopee = Poopee(user_id, serial_num, ip_addr, image_name)

    """log in ppcam"""
    response = poopee.ppcam_login()
    if str(type(response)) == "<class 'dict'>":
        token = response['device_access_token']
        ppcam_id = response['ppcam_id']
        pet_id = response['pet_id']
        # print(token, ppcam_id, pet_id)
    else:
        return response # if login fails, the program is terminate

    """connect bluetooth"""
    # client_socket = BluetoothSocket(RFCOMM)
    # client_socket.connect((mac_address, 1))
    # print("bluetooth connected!")

    """load labels for detect object"""
    labels = load_labels(label_path)

    """load engine for detect object"""
    engine_for_object = DetectionEngine(model_path_for_object)

    """load engine for predict poopee"""
    engine_for_predict = ClassificationEngine(model_path_for_poopee)

    """load video"""
    cap = cv2.VideoCapture(video_number)
    # for checking the sequences
    queue = [2]*20
    p_flag = False
    isOnpad = False

    while True:
        ret, frame = cap.read()
        if not ret:
            print('cannot read frame')
            break
        img = frame[:, :, ::-1].copy() # BGR to RGB
        img = Image.fromarray(img) # NumPy ndarray to PIL.Image

        """draw the bounding box and label for the pad"""
        # json_data = read_json(json_path)
        # pad_coordinate = json_data['pad']
        # annotate_pad(frame, pad_coordinate, pad_color)

        """detect object"""
        candidates = engine_for_object.detect_with_image(img, threshold=threshold, top_k=len(labels), keep_aspect_ratio=True, relative_coord=False, resample=0)
        if candidates:
            for obj in candidates:
                """set color for drawing"""
                if obj.label_id in box_colors:
                    box_color = box_colors[obj.label_id] # the same color for the same object
                else:
                    box_color = [int(j) for j in np.random.randint(0,255, 3)] # random color for new object
                    box_colors[obj.label_id] = box_color

                coordinate = tuple(map(int, obj.bounding_box.ravel()))
                accuracy = int(obj.score * 100) 
                label_text = labels[obj.label_id] + ' (' + str(accuracy) + '%)'
                """draws the bounding box and label"""
                # annotate_objects(frame, coordinate, label_text, box_color)

                if obj.label_id == 17: # id 17 is dog
                    """crop the image"""
                    dog_image = crop_image(img, obj.bounding_box.ravel())

                    """predict poopee"""
                    classify = engine_for_predict.classify_with_image(dog_image, top_k=1)
                    result = classify[0][0]
                    accuracy = classify[0][1] * 100

                    """
                    predict poopee
                    0 --> poo
                    1 --> pee
                    2 --> nothing
                    """

                    print("dog's coordinate is", coordinate, end=' ')
                    if result == 0:
                        print('and dog poop', end=' ')
                    elif result == 1:
                        print('and dog pees', end=' ')
                    else:
                        print('and dog is nothing', end=' ')
                    print('with', accuracy, 'percent accuracy.')

                    for r in range(1,10) :
                        queue[r-1] = queue[r]
                    queue[9] = result

                    if ((result == 0 or 1) and isOnpad == False) :
                        """send a signal to the snack bar if the dog defecates on the pad"""
                        temp_key, temp_value = ('lux', 'luy', 'rdx', 'rdy'), coordinate
                        dog_coordinate = dict(zip(temp_key, temp_value))
                        json_data = read_json(json_path)
                        pad_coordinate, feedback = json_data['pad'], json_data['feedback']

                        if ((pad_coordinate["rdx"] < dog_coordinate["lux"]) or (pad_coordinate["lux"] > dog_coordinate["rdx"]) or (pad_coordinate["luy"] > dog_coordinate["rdy"]) or (pad_coordinate["rdy"] < dog_coordinate["luy"])) :
                            continue
                        else :
                            # dog area
                            dog_wid = dog_coordinate["rdx"] - dog_coordinate["lux"]
                            dog_hei = dog_coordinate["rdy"] - dog_coordinate["luy"]
                            dog_area = dog_wid * dog_hei

                            # overlapped area
                            lx = max(pad_coordinate["lux"], dog_coordinate["lux"])
                            rx = min(pad_coordinate["rdx"], dog_coordinate["rdx"])
                            dy = max(pad_coordinate["rdy"], dog_coordinate["rdy"])
                            uy = min(pad_coordinate["luy"], dog_coordinate["luy"])

                            co_wid = rx - lx
                            co_hei = dy - uy
                            co_area = co_wid * co_hei

                            # Decide whether the dog is on the pad
                            if (co_area / dog_area >= 0.4) :
                                isOnpad = True

                    
                    # Sequential decision
                    Q = np.array(queue)
                    counte = collections.Counter(Q)
                    Q_res = counte.most_common(n=1)[0][0]
            
                    if (Q_res == 0 or 1) :
                        p_flag = True
                    else :
                        if (p_flag == True) :
                            # Success
                            if (isOnpad == True) :
                                response, token = send_result(poopee, dog_image, pet_id, token, image_name)
                                client_socket.send("on")
                            # defecates on wrong place
                            else :
                                # 배변 실패
                                response, token = send_result(poopee, dog_image, pet_id, token, image_name)
                            p_flag = False
                            isOnpad = False
                        else :
                            continue


                
                    # compare the dog's coordinates with the set pad's coordinates & analyze the sequence
                    # if the dog defecates on the pad:
                    #     response, token = send_result(poopee, dog_image, pet_id, token, image_name)
                    #     client_socket.send("on")

        """calculating and drawing fps"""            
        currTime = time.time()
        fps = 1/ (currTime -  prevTime)
        prevTime = currTime
        print('fps is', fps)
        # cv2.putText(frame, "fps:%.1f"%fps, (10,30), cv2.FONT_HERSHEY_PLAIN, 2, (0,255,0), 2)

        """show video"""
        # cv2.imshow('goodpp', frame)
        # if cv2.waitKey(1)&0xFF == ord('q'):
        #     break # press q to break
    
    """release video"""
    cap.release()

    """disconnect bluetooth"""
    # client_socket.close()
    # print("bluetooth disconnected!")

if __name__ == '__main__':
    main()