import numpy as np
import cv2
import time
from PIL import Image
from tflite_runtime.interpreter import Interpreter
from tflite_runtime.interpreter import load_delegate
# from bluetooth import *

def load_labels(path):
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        labels = {}
        for line in lines:
            id, name = line.strip().split(maxsplit=1)
            labels[int(id)] = name
    return labels

def set_interpreter(model_path):
    interpreter = Interpreter(model_path, experimental_delegates=[load_delegate('libedgetpu.so.1.0')])
    interpreter.allocate_tensors()
    return interpreter

def set_input_tensor(interpreter, image):
    """sets the input tensor"""
    tensor_index = interpreter.get_input_details()[0]['index']
    input_tensor = interpreter.tensor(tensor_index)()[0]
    input_tensor[:, :] = image

def get_output_tensor(interpreter, index):
    """returns the output tensor at the given index"""
    output_details = interpreter.get_output_details()[index]
    tensor = np.squeeze(interpreter.get_tensor(output_details['index']))
    return tensor

def detect_object(interpreter, image, threshold):
    set_input_tensor(interpreter, image)
    interpreter.invoke()

    boxes = get_output_tensor(interpreter, 0)
    classes = get_output_tensor(interpreter, 1)
    scores = get_output_tensor(interpreter, 2)
    count = int(get_output_tensor(interpreter, 3))

    results = []
    for i in range(count):
        if scores[i] >= threshold:
            result = {
                'bounding_box': boxes[i],
                'class_id': classes[i],
                'score': scores[i]
            }
            results.append(result)
    return results

def infer_poopee():
    print('infer poopee')

def main():
    """set variables"""
    video_number = 0
    label_path = 'coco_labels.txt'
    model_path_for_object = 'mobilenet_ssd_v2_coco_quant_postprocess_edgetpu.tflite'
    model_path_for_poopee = 'poopee_edgetpu.tflite'
    threshold = 0.4
    prevTime = 0

    """load labels"""
    labels = load_labels(label_path)

    """load video"""
    cap = cv2.VideoCapture(video_number)
    while True:
        ret, frame = cap.read()
        if not ret:
            print("cannot read frame.")
            break
        img = frame[:, :, ::-1].copy() # BGR to RGB
        img = Image.fromarray(img) # NumPy ndarray to PIL.Image

        """detect object"""
        interpreter = set_interpreter(model_path_for_object)
        _, input_height, input_width, _ = interpreter.get_input_details()[0]['shape']
        img = img.resize((input_height, input_width)) # resize the image to 300*300
        results = detect_object(interpreter, img, threshold)
        print(results)

        """infer poopee"""

        """send a signal to the snack bar if the dog defecates on the pad"""

        """calculating and drawing fps"""            
        currTime = time.time()
        fps = 1/ (currTime -  prevTime)
        prevTime = currTime
        cv2.putText(frame, "fps:%.1f"%fps, (10,30), cv2.FONT_HERSHEY_PLAIN, 2, (0,255,0), 2)

        """show video"""
        cv2.imshow('goodpp', frame)
        if cv2.waitKey(1)&0xFF == ord('q'):
            break 
    cap.release()

if __name__ == '__main__':
    main()