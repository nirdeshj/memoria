import cv2 as cv
import os
from django.utils.timezone import now
from datetime import timedelta
from .models import Reminder
import threading


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
haar_cascade = cv.CascadeClassifier(os.path.join(BASE_DIR, 'face_detect.xml'))
people = ['Manjil', 'Nirdesh']
face_recognizer = cv.face.LBPHFaceRecognizer_create()
face_recognizer.read(os.path.join(BASE_DIR, 'face_trained.yml'))
THRESHOLD = 80

# Global variable to store current reminder
current_reminder = {'text': '', 'show': False}
reminder_lock = threading.Lock()

def check_reminders_thread(patient_id):
    """Check reminders in background thread"""
    global current_reminder
    import time
    while True:
        try:
            current_time = now()
            reminders = Reminder.objects.filter(
                patient_id=patient_id,
                time__lte=current_time,
                time__gte=current_time - timedelta(seconds=30),
                is_sent=False
            )
            
            if reminders.exists():
                reminder = reminders.first()
                with reminder_lock:
                    current_reminder['text'] = f"{reminder.title} - {reminder.description}"
                    current_reminder['show'] = True
                
                # Mark as sent
                reminder.is_sent = True
                reminder.save()
                
                # Hide after 5 seconds
                time.sleep(15)
                with reminder_lock:
                    current_reminder['show'] = False
            else:
                time.sleep(1)  # Check every second
        except Exception as e:
            print(f"Reminder check error: {e}")
            time.sleep(1)

def gen_frames(patient_id):
    """Generate video frames with face recognition and reminders"""
    global current_reminder
    
    # Start reminder checking thread
    reminder_thread = threading.Thread(target=check_reminders_thread, args=(patient_id,), daemon=True)
    reminder_thread.start()
    
    vid = cv.VideoCapture(0)
    
    if not vid.isOpened():
        yield b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + b'\r\n'
        return
    
    while True:
        ret, img = vid.read()
        if not ret:
            break
        
        # Face recognition
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        gray = cv.equalizeHist(gray)
        faces_rect = haar_cascade.detectMultiScale(gray, 1.1, 6)
        
        for (x, y, w, h) in faces_rect:
            faces_roi = gray[y:y + h, x:x + w]
            face_roi = cv.equalizeHist(faces_roi)
            
            label, confidence = face_recognizer.predict(face_roi)
            
            if confidence < THRESHOLD:
                name = people[label]
                text = f"{name} ({confidence:.1f})"
                color = (0, 255, 0)
            else:
                name = "Unknown"
                text = name
                color = (0, 0, 255)
            
            cv.putText(img, text, (x + 10, y + h + 25),
                      cv.FONT_HERSHEY_COMPLEX, 0.9, color, 2)
            cv.rectangle(img, (x, y), (x + w, y + h), color, 2)
        
        # Add reminder overlay if active
        with reminder_lock:
            if current_reminder['show']:
                reminder_text = current_reminder['text']
                # Draw reminder box
                text_size = cv.getTextSize(reminder_text, cv.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
                box_width = text_size[0] + 20
                box_height = 60
                cv.rectangle(img, (10, 10), (10 + box_width, 10 + box_height), (255, 255, 255), -1)
                cv.rectangle(img, (10, 10), (10 + box_width, 10 + box_height), (0, 255, 0), 2)
                # Split text if too long
                words = reminder_text.split()
                lines = []
                current_line = ""
                for word in words:
                    test_line = current_line + word + " "
                    if cv.getTextSize(test_line, cv.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0][0] < box_width - 10:
                        current_line = test_line
                    else:
                        if current_line:
                            lines.append(current_line.strip())
                        current_line = word + " "
                if current_line:
                    lines.append(current_line.strip())
                
                y_offset = 35
                for line in lines[:2]:  # Max 2 lines
                    cv.putText(img, line, (15, y_offset), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
                    y_offset += 25
        
        # Encode frame
        ret, buffer = cv.imencode('.jpg', img)
        if not ret:
            continue
        
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    
    vid.release()
