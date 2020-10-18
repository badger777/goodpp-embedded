import numpy as np
import cv2
import time
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
def annotate_objects(frame, coordinate, label_text, accuracy, box_color):
    box_left, box_top, box_right, box_bottom = coordinate

    cv2.rectangle(frame, (box_left, box_top), (box_right, box_bottom), box_color, 2)
    (txt_w, txt_h), base = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_PLAIN, 2, 3)
    cv2.rectangle(frame, (box_left - 1, box_top - txt_h), (box_left + txt_w, box_top + txt_h), box_color, -1)
    cv2.putText(frame, label_text, (box_left, box_top+base), cv2.FONT_HERSHEY_PLAIN, 2, (255,255,255), 2)

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
    # setting pad coordinate

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
    while True:
        ret, frame = cap.read()
        if not ret:
            print('cannot read frame')
            break
        img = frame[:, :, ::-1].copy() # BGR to RGB
        img = Image.fromarray(img) # NumPy ndarray to PIL.Image

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
                # annotate_objects(frame, coordinate, label_text, accuracy, box_color)

                if obj.label_id == 17: # id 17 is dog
                    """crop the image"""
                    input_data = crop_image(img, obj.bounding_box.ravel())

                    """predict poopee"""
                    classify = engine_for_predict.classify_with_image(input_data, top_k=1)
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

                    """send a signal to the snack bar if the dog defecates on the pad"""
                    # compare the dog's coordinates with the set pad's coordinates
                    # if the dog defecates on the pad:
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