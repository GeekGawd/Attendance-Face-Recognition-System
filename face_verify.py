import cv2
from PIL import Image
import argparse
from pathlib import Path
from multiprocessing import Process, Pipe,Value,Array
import torch
from config import get_config
from mtcnn import MTCNN
from Learner import face_learner
from utils import load_facebank, draw_box_name, prepare_facebank
from database import mark_attendance_db
import time
import threading
import numpy as np
# Create a semaphore with the maximum number of threads allowed
semaphore = threading.Semaphore()

def mark_attendance_db_thread(name):
    # Acquire the semaphore
    semaphore.acquire()

    try:
        # Call the function
        mark_attendance_db(name)
    finally:
        # Release the semaphore
        semaphore.release()

parser = argparse.ArgumentParser(description='for face verification')
parser.add_argument("-s", "--save", help="whether save",action="store_true")
parser.add_argument('-th','--threshold',help='threshold to decide identical faces',default=1.54, type=float)
parser.add_argument("-u", "--update", help="whether perform update the facebank",action="store_true")
parser.add_argument("-tta", "--tta", help="whether test time augmentation",action="store_true")
parser.add_argument("-c", "--score", help="whether show the confidence score",action="store_true")
args = parser.parse_args()

conf = get_config(False)

mtcnn = MTCNN()
print('arcface loaded')

learner = face_learner(conf, True)
learner.threshold = args.threshold
if conf.device.type == 'cpu':
    learner.load_state(conf, 'cpu_final.pth', True, True)
else:
    learner.load_state(conf, 'final.pth', True, True)
learner.model.eval()
print('learner loaded')

if args.update:
    targets, names = prepare_facebank(conf, learner.model, mtcnn, tta = args.tta)
    print('facebank updated')
else:
    targets, names = load_facebank(conf)
    print('facebank loaded')

# inital camera

def draw_box_name_with_name(bbox, detected_name, your_name, frame):
    x, y, w, h = bbox
    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)  # Draw the bounding box

    # Display the detected name below the bounding box
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.5
    font_thickness = 1
    text_size = cv2.getTextSize(detected_name, font, font_scale, font_thickness)[0]

    cv2.putText(frame, detected_name, (x + (w - text_size[0]) // 2, y - 5),
                font, font_scale, (0, 255, 0), font_thickness, cv2.LINE_AA)

    # Display your name above the bounding box
    text_size_your_name = cv2.getTextSize(your_name, font, font_scale, font_thickness)[0]
    cv2.putText(frame, your_name, (x + (w - text_size_your_name[0]) // 2, y - 20),
                font, font_scale, (0, 0, 255), font_thickness, cv2.LINE_AA)

    return frame


cap = cv2.VideoCapture(0)
cap.set(3,500)
cap.set(4,500)

class faceRec:
    def __init__(self):
        self.width = 800
        self.height = 800
        self.image = None
    def main(self): 
        while cap.isOpened():
            isSuccess,frame = cap.read()
            if isSuccess:            
                try:     
                    image = Image.fromarray(frame)
                    bboxes, faces = mtcnn.align_multi(image, conf.face_limit, conf.min_face_size)
                    if isinstance(bboxes, list):
                        continue
                    bboxes = bboxes[:,:-1] #shape:[10,4],only keep 10 highest possibiity faces
                    bboxes = bboxes.astype(int)
                    bboxes = bboxes + [-1,-1,1,1] # personal choice
                    results, score = learner.infer(conf, faces, targets, args.tta)
                    for idx,bbox in enumerate(bboxes):
                        if args.score:
                            frame = draw_box_name(bbox, names[results[idx] + 1] + '_{:.2f}'.format(score[idx]), frame)
                        else:
                            print(score)
                            try:
                                if float('{:.2f}'.format(score[idx])) > .98:
                                    name = names[0]
                                else:    
                                    name = names[results+1]
                                    thread = threading.Thread(target=mark_attendance_db_thread, args=(name,))
                                    thread.start()
                                print(f"name: {names[results + 1]}")
                                frame = draw_box_name(bbox, names[results + 1], frame)
                            except:
                                pass
                            # frame = draw_box_name_with_name(bbox, names[results + 1], names[results + 1], frame)
                except ValueError:
                    pass
                ret, jpeg = cv2.imencode('.jpg', frame)
                return jpeg.tostring()


            if cv2.waitKey(1)&0xFF == ord('q'):
                break

        cap.release()

        cv2.destroyAllWindows()    
    
if __name__ == '__main__':
    faceRec().main()