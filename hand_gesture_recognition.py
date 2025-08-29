import cv2
import mediapipe as mp
import numpy as np
import math

class HandGestureRecognizer:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils
        
    
        self.gestures = {
            'open_palm': 'Open Palm',
            'fist': 'Fist',
            'peace_sign': 'Peace Sign',
            'thumbs_up': 'Thumbs Up'
        }
        
       
        self.cap = cv2.VideoCapture(0)
        
        
        self.tolerance = 0.1
        
    def calculate_distance(self, point1, point2):
        """Calculate Euclidean distance between two points"""
        return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
    
    def calculate_angle(self, point1, point2, point3):
        """Calculate angle between three points"""
        a = np.array([point1[0], point1[1]])
        b = np.array([point2[0], point2[1]])
        c = np.array([point3[0], point3[1]])
        
        ba = a - b
        bc = c - b
        
        cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
        angle = np.arccos(cosine_angle)
        
        return np.degrees(angle)
    
    def is_finger_extended(self, tip, pip, wrist, tolerance_factor=1.0):
        """Check if a finger is extended with tolerance"""
        tip_distance = self.calculate_distance(tip, wrist)
        pip_distance = self.calculate_distance(pip, wrist)
        
        
        threshold = pip_distance * (1 + self.tolerance * tolerance_factor)
        return tip_distance > threshold
    
    def is_finger_closed(self, tip, pip, wrist, tolerance_factor=1.0):
        """Check if a finger is closed with tolerance"""
        tip_distance = self.calculate_distance(tip, wrist)
        pip_distance = self.calculate_distance(pip, wrist)
        
       
        threshold = pip_distance * (1 - self.tolerance * tolerance_factor)
        return tip_distance < threshold
    
    def detect_open_palm(self, landmarks):
       
        wrist = landmarks[0]
        
        # Check if all fingers are extended with some tolerance
        thumb_extended = self.is_finger_extended(landmarks[4], landmarks[3], wrist, 1.5)
        index_extended = self.is_finger_extended(landmarks[8], landmarks[6], wrist, 1.0)
        middle_extended = self.is_finger_extended(landmarks[12], landmarks[10], wrist, 1.0)
        ring_extended = self.is_finger_extended(landmarks[16], landmarks[14], wrist, 1.0)
        pinky_extended = self.is_finger_extended(landmarks[20], landmarks[18], wrist, 1.0)
        
        return thumb_extended and index_extended and middle_extended and ring_extended and pinky_extended
    
    def detect_fist(self, landmarks):
       
        wrist = landmarks[0]
        
       
        thumb_closed = self.is_finger_closed(landmarks[4], landmarks[3], wrist, 0.8)
        index_closed = self.is_finger_closed(landmarks[8], landmarks[6], wrist, 1.0)
        middle_closed = self.is_finger_closed(landmarks[12], landmarks[10], wrist, 1.0)
        ring_closed = self.is_finger_closed(landmarks[16], landmarks[14], wrist, 1.0)
        pinky_closed = self.is_finger_closed(landmarks[20], landmarks[18], wrist, 1.0)
        
       
        closed_fingers = sum([thumb_closed, index_closed, middle_closed, ring_closed, pinky_closed])
        return closed_fingers >= 4
    
    def detect_peace_sign(self, landmarks):
        
        wrist = landmarks[0]
        
       
        index_extended = self.is_finger_extended(landmarks[8], landmarks[6], wrist, 1.2)
        middle_extended = self.is_finger_extended(landmarks[12], landmarks[10], wrist, 1.2)
        
       
        thumb_closed = self.is_finger_closed(landmarks[4], landmarks[3], wrist, 0.7)
        ring_closed = self.is_finger_closed(landmarks[16], landmarks[14], wrist, 1.0)
        pinky_closed = self.is_finger_closed(landmarks[20], landmarks[18], wrist, 1.0)
        
       
        others_closed = sum([thumb_closed, ring_closed, pinky_closed])
        return index_extended and middle_extended and others_closed >= 2
    
    def detect_thumbs_up(self, landmarks):
        
        wrist = landmarks[0]
        
        
        thumb_tip = landmarks[4]
        thumb_ip = landmarks[3]
        
      
        thumb_extended_up = (thumb_tip[1] < wrist[1] and 
                           thumb_tip[1] < thumb_ip[1] and 
                           self.is_finger_extended(thumb_tip, thumb_ip, wrist, 1.5))
        
        
        index_closed = self.is_finger_closed(landmarks[8], landmarks[6], wrist, 1.2)
        middle_closed = self.is_finger_closed(landmarks[12], landmarks[10], wrist, 1.2)
        ring_closed = self.is_finger_closed(landmarks[16], landmarks[14], wrist, 1.2)
        pinky_closed = self.is_finger_closed(landmarks[20], landmarks[18], wrist, 1.2)
        
        
        others_closed = sum([index_closed, middle_closed, ring_closed, pinky_closed])
        
        return thumb_extended_up and others_closed >= 3
    
    def classify_gesture(self, landmarks):
        
        if self.detect_thumbs_up(landmarks):
            return self.gestures['thumbs_up']
        elif self.detect_open_palm(landmarks):
            return self.gestures['open_palm']
        elif self.detect_peace_sign(landmarks):
            return self.gestures['peace_sign']
        elif self.detect_fist(landmarks):
            return self.gestures['fist']
        else:
            return "Unknown"
    
    def run(self):
        
        print("Hand Gesture Recognition Started!")
        print("Press 'q' to quit")
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Failed to grab frame")
                break
            
           
            frame = cv2.flip(frame, 1)
            
            
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
           
            results = self.hands.process(rgb_frame)
            
            gesture_name = "No Hand Detected"
            
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    
                    self.mp_draw.draw_landmarks(
                        frame, 
                        hand_landmarks, 
                        self.mp_hands.HAND_CONNECTIONS
                    )
                    
                    
                    landmarks = []
                    for landmark in hand_landmarks.landmark:
                        h, w, c = frame.shape
                        x, y = int(landmark.x * w), int(landmark.y * h)
                        landmarks.append((x, y))
                    
                 
                    gesture_name = self.classify_gesture(landmarks)
            
           
            cv2.putText(
                frame, 
                f"Gesture: {gesture_name}", 
                (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 
                1, 
                (0, 255, 0), 
                2
            )
            
          
            cv2.imshow('Hand Gesture Recognition', frame)
            
           
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
       
        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    recognizer = HandGestureRecognizer()
    recognizer.run()
