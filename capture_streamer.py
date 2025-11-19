import datetime
import json
import pyvirtualcam
from pyvirtualcam import PixelFormat
import numpy as np
import cv2
import psycopg2
import time
import os
import simplejpeg
import mediapipe as mp
import zdata as zd
import random

# Import camera configuration
try:
    from camera_config import CAMERA_INDEX, CAMERA_WIDTH, CAMERA_HEIGHT, VERBOSE_LOGGING
except ImportError:
    # Default values if config file is not available
    CAMERA_INDEX = 0
    CAMERA_WIDTH = 10000
    CAMERA_HEIGHT = 10000
    VERBOSE_LOGGING = True


def DrawFPS(img, fps):
    cv2.putText(img, f'FPS: {int(fps)}', (20, 70), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 2)


def findFaces(img, faceDetection):
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = faceDetection.process(imgRGB)
    # print(self.results)
    bboxs = []
    if results.detections:
        for id, detection in enumerate(results.detections):
            bboxC = detection.location_data.relative_bounding_box
            ih, iw, ic = img.shape
            bbox = int(bboxC.xmin * iw), int(bboxC.ymin * ih), \
                   int(bboxC.width * iw), int(bboxC.height * ih)
            bboxs.append([id, bbox, detection.score])
    return img, bboxs


def DrawRectagle(img, bbox, gbboxs, detection_score, emb, l=30, t=5, rt=3, dpix=80):
    for box in bbox:
        num = box[0]
        dots = box[1]
        score = box[2][0]
        # text =  box[2]
        newgbboxs = gbboxs
        if score >= detection_score:
            x, y, w, h = dots
            x1, y1 = x + w, y + h
            color = (0, 255, 0)
            cv2.rectangle(img, dots, color, rt)
            cMilliseconds = int(time.time() * 1000)
            newgbboxs = []
            num = -1
            d = 10 ** 8
            name = ""
            for gitem in gbboxs:
                gMilliseconds = gitem[4]
                if abs(gMilliseconds - cMilliseconds) <= lifeTime:
                    newgbboxs.append(gitem)
                    cbox = gitem[1]
                    # print(dots)
                    # print(gitem[1])
                    # print("gitem[1]")
                    if dist(dots, cbox) < d:
                        d = dist(dots, cbox)
                        if d < dpix:
                            name = emb[gitem[3]]['name']
            gbboxs = newgbboxs
            fontScale = 2
            color = (0, 255, 0)
            cv2.putText(img, name,
                        (dots[0], dots[1] - 20), cv2.FONT_HERSHEY_COMPLEX,
                        fontScale, color, 3)
            # cv2.putText(img, name,
            #             (dots[0], dots[1] - 20), cv2.FONT_HERSHEY_COMPLEX,
            #             0.5, (255, 0, 255), 1)

    return img, gbboxs


def dist(dots, box):
    d = 0
    x1, y1, w1, h1 = dots
    x2, y2, w2, h2 = box
    xx1 = x1 + w1 / 2
    yy1 = y1 + h1 / 2
    xx2 = x2 + w2 / 2
    yy2 = y2 + h2 / 2
    d = np.sqrt((xx1 - xx2) ** 2 + (yy1 - yy2) ** 2)
    return d


def toPG(connection, img, bbox):
    # encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 70]
    # _, data = cv2.imencode('.jpg', img, encode_param)
    # frame = data.tobytes()
    frame = simplejpeg.encode_jpeg(image=img, quality=90)
    milliseconds = int(time.time() * 1000)
    dt = datetime.datetime.fromtimestamp(milliseconds / 1000.0)
    # print(dt)
    score = milliseconds
    cursor = connection.cursor()
    bbox = json.dumps(str(bbox))
    sql_insert_with_param = """INSERT INTO z1frame
                          (frame, milliseconds ,timestr, bbox)
                          VALUES (%s, %s, %s, %s);"""
    data_tuple = (frame, milliseconds, dt, bbox)
    cursor.execute(sql_insert_with_param, data_tuple)
    connection.commit()


def fromPGZdata(connection):
    cursor = connection.cursor()
    postgreSQL_select_Query = "SELECT * FROM public.zdata ORDER BY milliseconds DESC LIMIT 1"
    cursor.execute(postgreSQL_select_Query)
    datarecord = cursor.fetchone()
    zjson = []
    milliseconds = 0
    if datarecord:
        id = datarecord[0]
        zjson = datarecord[1]
        milliseconds = datarecord[2]
        timestr = datarecord[3]
        sql_delete_query = "Delete from public.zdata where id = " + str(id)
        cursor.execute(sql_delete_query)
        connection.commit()
        if len(zjson) > 1:
            zjson = zjson.replace("'", "")
            zjson = zjson.replace("\"", "")
            import ast
            zjson = ast.literal_eval(zjson)
    return zjson, milliseconds


def init_camera(camera_index=0, width=10000, height=10000, verbose=True):
    """Initialize camera with proper backend and fallback mechanisms"""
    # Try with DirectShow backend first (Windows/OBS compatibility)
    backends = [
        (cv2.CAP_DSHOW, "DirectShow"),
        (cv2.CAP_MSMF, "Media Foundation"),
        (cv2.CAP_ANY, "Any available")
    ]
    
    camera_indices = [camera_index, 0, 1, 2]  # Try specified index first, then common defaults
    
    cap = None
    for backend_id, backend_name in backends:
        for cam_idx in camera_indices:
            try:
                if verbose:
                    print(f"Trying camera {cam_idx} with {backend_name} backend...")
                test_cap = cv2.VideoCapture(cam_idx, backend_id)
                if test_cap.isOpened():
                    # Test if we can actually read a frame
                    ret, frame = test_cap.read()
                    if ret and frame is not None:
                        cap = test_cap
                        if verbose:
                            print(f"Successfully opened camera {cam_idx} with {backend_name} backend")
                        break
                    else:
                        test_cap.release()
                else:
                    test_cap.release()
            except Exception as e:
                if verbose:
                    print(f"Failed to open camera {cam_idx} with {backend_name}: {e}")
                if test_cap is not None:
                    test_cap.release()
        if cap is not None:
            break
    
    if cap is None or not cap.isOpened():
        raise RuntimeError("Cannot open any camera. Please check camera connection and permissions.")
    
    # Set resolution
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    
    actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    if verbose:
        print(f"Camera resolution: {actual_width}x{actual_height}")
    
    return cap, actual_width, actual_height


if __name__ == '__main__':
    connection = psycopg2.connect(user="personauser", password="pgpwd4persona", host="127.0.0.1", port="5432",
                                  database="personadb")
    connection.autocommit = True
    emb = zd.getEmb()
    lifeTime = 1000 * 5
    number_of_processing_frame = 7

    # Initialize camera with configuration from camera_config.py
    # You can modify camera_config.py to change camera settings
    cap, width, height = init_camera(camera_index=CAMERA_INDEX, width=CAMERA_WIDTH, height=CAMERA_HEIGHT, verbose=VERBOSE_LOGGING)

    # cap = cv2.VideoCapture("rtsp://admin:FreePAS12@192.168.1.65:554/ISAPI/Streaming/Channels/101")
    # cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    # cap = cv2.VideoCapture("rtsp://admin:FreePAS12@192.168.88.23:554/ISAPI/Streaming/Channels/1")
    # cap = cv2.VideoCapture("rtsp://admin:FreePAS12@192.168.88.25:554/ISAPI/Streaming/Channels/1")
    # cap = cv2.VideoCapture("d:\\test1.mp4")

    with pyvirtualcam.Camera(width=990, height=540, fps=30, fmt=PixelFormat.BGR) as cam:
        sframe = []
        count = 0
        pTime = 0
        detection_score = 0.4  # порог чувствительности для поиска лица от 0 до 1
        minDetectionCon = 0.6
        mpFaceDetection = mp.solutions.face_detection
        # mpDraw = mp.solutions.drawing_utils
        faceDetection = mpFaceDetection.FaceDetection(min_detection_confidence=minDetectionCon,
                                                      model_selection=1)
        gbboxs = []
        gdash = []
        while True:

            if count % 75 == 0:  #каждый 75 кадр провперка есть ли новое лицо в для загрузки в emb
                if zd.checkNew():
                    zd.addEmb()
                    emb = zd.getEmb()

            count += 1
            cTime = time.time()
            fps = 1 / (cTime - pTime)
            ret, frame = cap.read()
            if not ret:
                print("Can't receive frame (stream end?). Exiting ...")
                break
            if len(frame) > 1:
                pTime = cTime
                # DrawFPS(frame, fps)
                img, bboxs = findFaces(frame, faceDetection)
                # print(bboxs)
                if count % number_of_processing_frame == 0:
                    count = 0
                    if len(bboxs) > 0:
                        toPG(connection, frame, bboxs)
                    else:
                        count -= 1
                zjson, milliseconds = fromPGZdata(connection)
                if int(milliseconds) > 0:
                    for item in zjson:
                        # iMilliseconds=item[3]
                        # print(item, iMilliseconds, milliseconds)
                        item.append(milliseconds)
                        gbboxs.append(item)
                    # cv2.imwrite(".\\capture\\" + str(milliseconds) + str(random.randint(0, 10 ** 10)) + ".jpg", frame)
                frame, gbboxs = DrawRectagle(img, bboxs, gbboxs, detection_score, emb)
                # print(tuple(frame.shape[1::-1]))
                sframe = cv2.resize(frame, (990, 540))
                cam.send(sframe)
                cam.sleep_until_next_frame()
    connection.commit()
    connection.close()
