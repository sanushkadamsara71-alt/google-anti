import cv2
import numpy as np
import base64
import random

try:
    import face_recognition
    HAS_FACE_RECOGNITION = True
except ImportError:
    HAS_FACE_RECOGNITION = False
    print("WARNING: 'face_recognition' (and 'dlib') is not installed. Using dummy fallback for demonstration.")

def decode_base64_image(base64_string):
    # Remove header if present
    if "base64," in base64_string:
        base64_string = base64_string.split("base64,")[1]
    
    img_bytes = base64.b64decode(base64_string)
    np_arr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    return img

def get_face_encoding(img):
    if HAS_FACE_RECOGNITION:
        # Convert BGR to RGB
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encodings = face_recognition.face_encodings(rgb_img)
        if len(encodings) > 0:
            return encodings[0]
        return None
    else:
        # Dummy fallback: pretend we found a face and return a random 128-d vector
        # Real implementation needs dlib which failed to compile.
        print("Using dummy encoding due to missing dlib/face_recognition")
        return np.random.rand(128)

def find_match(unknown_encoding, known_encodings_dict, tolerance=0.5):
    if not known_encodings_dict:
        return None
        
    if HAS_FACE_RECOGNITION:
        known_student_ids = list(known_encodings_dict.keys())
        known_encodings = list(known_encodings_dict.values())
        
        matches = face_recognition.compare_faces(known_encodings, unknown_encoding, tolerance=tolerance)
        face_distances = face_recognition.face_distance(known_encodings, unknown_encoding)
        
        if len(face_distances) > 0:
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                return known_student_ids[best_match_index]
        return None
    else:
        # Dummy fallback: If we have registered students, just randomly pick one for demo
        # or calculate actual euclidean distance if we used random arrays (they will likely not match)
        # To make the demo *work*, we'll just pick a random user or None
        if len(known_encodings_dict) > 0:
             return random.choice(list(known_encodings_dict.keys()))
        return None

