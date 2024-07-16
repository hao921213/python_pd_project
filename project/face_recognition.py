import cv2
import os
import numpy as np
import sqlite3
from PIL import Image
import time
import shutil

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

recognizer = cv2.face.LBPHFaceRecognizer_create()



def clear_data():
    conn = sqlite3.connect("poker_game.db")
    conn.execute("DELETE FROM PlayerInfo")
    conn.commit()
    conn.close()
    print("All data has been deleted from the database.")
    
    # 刪除trainer目錄下所有文件
    if os.path.exists('trainer'):
        shutil.rmtree('trainer')
        print('Trainer directory has been cleared.')
    
    # 刪除face_data目錄下所有文件
    if os.path.exists('face_data'):
        shutil.rmtree('face_data')
        print('Face data directory has been cleared.')

# 初始化資料庫函式
def initialize_db():
    conn = sqlite3.connect("poker_game.db")
    print("Database connection opened.")
    conn.execute("""
    CREATE TABLE IF NOT EXISTS PlayerInfo (
        FaceModel BLOB,
        Name TEXT,
        Chips INTEGER
    )
    """)
    conn.commit()
    conn.close()
    print("Database connection closed.")


def capture_faces():
    cap = cv2.VideoCapture(0)
    while True:
        face_id = input("Enter a new user ID: ")
        if not get_user_info(face_id):  
            break
        else:
            print("User ID already exists, please enter a different ID.")
    
    count = 0
    while True:
        ret, img = cap.read()
        if not ret:
            continue

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
            count += 1
            cv2.imwrite(f"face_data/User.{face_id}.{count}.jpg", gray[y:y+h, x:x+w])

        cv2.imshow('Capturing Faces', img)

        if cv2.waitKey(100) & 0xFF == ord('q') or count >= 50:
            break

    cap.release()
    cv2.destroyAllWindows()
    return face_id


def get_images_and_labels(path):
    image_paths = [os.path.join(path, f) for f in os.listdir(path)]
    face_samples = []
    ids = []

    for image_path in image_paths:
        PIL_img = Image.open(image_path).convert('L')
        img_numpy = np.array(PIL_img, 'uint8')
        id = int(os.path.split(image_path)[-1].split(".")[1])
        faces = face_cascade.detectMultiScale(img_numpy)
        for (x, y, w, h) in faces:
            face_samples.append(img_numpy[y:y+h, x:x+w])
            ids.append(id)
    return face_samples, ids

def train_model():
    faces, ids = get_images_and_labels('face_data')
    recognizer.train(faces, np.array(ids))
    recognizer.save('trainer/trainer.yml')

def recognize_faces():
    model_path = 'trainer/trainer.yml'
    if not os.path.exists(model_path):
        print("Model file does not exist. Please train the model first.")
        return None
    
    recognizer.read(model_path)
    cap = cv2.VideoCapture(0)
    timeout = 2  # Timeout in seconds
    start_time = time.time()

    while True:
        ret, img = cap.read()
        if not ret:
            continue

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

        for (x, y, w, h) in faces:
            id, confidence = recognizer.predict(gray[y:y+h, x:x+w])
            if confidence < 60:
                print(f"ID: {id}, Confidence: {confidence}")
                user_info = get_user_info(id)
                if user_info:
                    print(f"User Found: {user_info[0]}, Chips: {user_info[1]}")
                else:
                    print("User not found in database.")
            else:
                print("Face not recognized with high confidence.")

        cv2.imshow('Face Recognition', img)

        if (time.time() - start_time) > timeout:
            break

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    return id if confidence < 60 else None


def save_model_to_db(user_id, name, chips):
    model_path = f"trainer/model_{user_id}.yml"
    recognizer.save(model_path)
    
    conn = sqlite3.connect("poker_game.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO PlayerInfo (FaceModel, Name, Chips) VALUES (?, ?, ?)", (model_path, name, chips))
    conn.commit()
    conn.close()

    print("Model path saved to database.")


def get_user_info(user_id):
    conn = sqlite3.connect("poker_game.db")
    cursor = conn.cursor()
    cursor.execute("SELECT Name, Chips FROM PlayerInfo WHERE rowid = ?", (user_id,))
    user_info = cursor.fetchone()
    conn.close()
    return user_info

if __name__ == "__main__":
    if not os.path.exists('trainer'):
        os.makedirs('trainer')
    
    if not os.path.exists('face_data'):
        os.makedirs('face_data')

    initialize_db()

    if input("Do you want to delete all data? (yes/no): ").lower() == 'yes':
        clear_data()
    else:
        user_id = recognize_faces()
        if user_id is None:
            if not get_user_info(user_id):
                print("No existing user found, capturing new faces.")
                new_user_id = capture_faces()
                user_name = input("Enter new user name: ")
                user_chips = int(input("Enter chips (integer): "))
                train_model()
                save_model_to_db(new_user_id, user_name, user_chips)
                print("New user data saved to database.")
            else:
                user_info = get_user_info(user_id)
                print(f"User Found: {user_info[0]}, Chips: {user_info[1]}")
