import json
import os
import re
from html import unescape

import mariadb
import pandas as pd

HTML_TAG_RE = re.compile(r'<[^>]+>')

prediction_root = os.getenv(key="PREDICTIONS_ROOT",
                            default='C:/Users/41789/Documents/uni/fs21/video_retrieval/')
keyframe_root = os.getenv(key="KEYFRAME_ROOT",
                          default='D:/keyframes/')


def migrate_db():
    nasnet = pd.read_csv(prediction_root + 'nasnet_formated.csv')
    yolo = pd.read_csv(prediction_root + 'yolo.csv',
                       index_col="idx", dtype=str)
    ocr_data = pd.read_csv(prediction_root + 'combinedOCR.csv').dropna(
        subset=['output'])
    keyframe_data = pd.read_csv(prediction_root + 'timeframes.csv')
    db_connection = mariadb.connect(user=os.getenv("db_user"), password=os.getenv("db_pw"),
                                    database=os.getenv("db_name"), host=os.getenv("db_host"), port=3306)
    db_connection.auto_reconnect = True
    cursor = db_connection.cursor()

    cursor.execute(
        "SELECT id,title FROM videos WHERE id=?",
        ('00032',))

    if cursor.fetchone() is None:
        jsons = []
        for filename in os.listdir("C:/Users/41789/Documents/uni/fs21/video_retrieval/info"):
            try:
                with open(os.path.join("C:/Users/41789/Documents/uni/fs21/video_retrieval/info", filename), 'r',
                          encoding="utf8") as f:  # open in readonly mode
                    json_obj = json.loads(f.read())
                    jsons.append((json_obj['v3cId'], json_obj['vimeoId'], json_obj['title'], json.dumps(json_obj['tags']),
                                  unescape(' '.join(HTML_TAG_RE.sub('', json_obj['description']).split()))))
            except ValueError:
                with open(os.path.join("C:/Users/41789/Documents/uni/fs21/video_retrieval/info", filename), 'r',
                          encoding="latin-1") as f:  # open in readonly mode
                    json_obj = json.loads(f.read())
                    jsons.append((json_obj['v3cId'], json_obj['vimeoId'], json_obj['title'], json.dumps(json_obj['tags']),
                                  unescape(' '.join(HTML_TAG_RE.sub('', json_obj['description']).split()))))
        sql = "INSERT INTO videos(id, vimeo_id, title, tags, description) VALUES (?, ?, ?, ?, ?)"
        cursor.executemany(sql, jsons)
        db_connection.commit()
    print("Video table is ready!")

    cursor.execute(
        "SELECT video_fk,frame FROM keyframes WHERE video_fk=?",
        ('00032',))

    if cursor.fetchone() is None:
        data = []
        for index, row in keyframe_data.iterrows():
            data.append((row['keyframe'].split("_")[0], int(row['keyframe'].split("_")[1]),
                         row['starttime'], row['endtime']
                         ))
        sql = "INSERT INTO keyframes(video_fk, frame, start_time, end_time) " \
              "VALUES (?, ?, ?, ?)"
        cursor.executemany(sql, data)
        db_connection.commit()
    print("Keyframe table is ready!")

    cursor.execute(
        "SELECT video_fk FROM yolo_detection WHERE video_fk=?",
        ('00032',))

    if cursor.fetchone() is None:
        data = []
        for index, row in yolo.iterrows():
            data.append((row['video'], int(row['frame']),
                         row['class'], float(row['centerX']), float(row['centerY']), float(row['width']),
                         float(row['height']), float(row['confidence'])
                         ))
        sql = "INSERT INTO yolo_detection(video_fk, frame, class, center_x, center_y, width, height, confidence) " \
              "VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
        cursor.executemany(sql, data)
        db_connection.commit()
    print("Yolo table is ready!")

    cursor.execute(
        "SELECT video_fk FROM nasnet_classification WHERE video_fk=?",
        ('00032',))

    if cursor.fetchone() is None:
        data = []
        for index, row in nasnet.iterrows():
            filename_parts = row['filename'].replace("shot", "").replace("_RKF.png", "").split("_")
            data.append((filename_parts[0], int(filename_parts[1]), row['class'], row['confidence']))
        sql = "INSERT INTO nasnet_classification(video_fk, frame, class, confidence) " \
              "VALUES (?, ?, ?, ?)"
        cursor.executemany(sql, data)
        db_connection.commit()
    print("Nasnet table is ready!")

    cursor.execute(
        "SELECT video_fk FROM tesseract_text WHERE video_fk=?",
        ('00032',))

    if cursor.fetchone() is None:
        data = []
        for index, row in ocr_data.iterrows():
            filename_parts = row['filename'].replace("shot", "").replace("_RKF.png", "").split("_")
            data.append((filename_parts[0], int(filename_parts[1]), row['output']))
        sql = "INSERT INTO tesseract_text(video_fk, frame, text) " \
              "VALUES (?, ?, ?)"
        cursor.executemany(sql, data)
        db_connection.commit()
    print("Tesseract table is ready!")


if __name__ == "__main__":
    migrate_db()
