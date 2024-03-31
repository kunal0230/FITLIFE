# Import necessary libraries
from flask import Flask, render_template, Response
import cv2
import mediapipe as mp
import math
from datetime import datetime
import os
import json

app = Flask(__name__)

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

# Initialize the MediaPipe pose detection object
pose = mp_pose.Pose()

# Open the default camera (index 0) for capturing video
cap = cv2.VideoCapture(0)

# Check if the camera is successfully opened
if not cap.isOpened():
    print("Failed to open the camera")
    exit()

# Initialize variables for counting bicep curls and delay timer
left_arm_up = False
right_arm_up = False
left_curl_count = 0
right_curl_count = 0
delay_timer = 0  # Delay timer for the 5-second countdown
countdown_timer = 5  # Countdown timer for starting the exercise

# Flag to indicate if tracking and counting should start
start_tracking = False

# Function to get the current timestamp
def get_current_time():
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/bicep_curls')
def bicep_curls():
    return render_template('index.html')

def generate_frames():
    global left_arm_up
    global right_arm_up
    global left_curl_count
    global right_curl_count
    global delay_timer
    global start_tracking
    global countdown_timer

    left_angle = 0
    right_angle = 0
    results = None

    while True:
        ret, frame = cap.read()

        if not ret:
            print("Failed to capture frame")
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        if countdown_timer > 0:
            countdown_text = f"Starting in {countdown_timer} seconds"
            text_size = cv2.getTextSize(countdown_text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
            text_x = (frame.shape[1] - text_size[0]) // 2
            text_y = (frame.shape[0] + text_size[1]) // 2
            cv2.putText(frame, countdown_text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            countdown_timer -= 1
        else:
            if start_tracking:
                results = pose.process(frame_rgb)

                if results.pose_landmarks:
                    left_shoulder = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER]
                    left_elbow = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ELBOW]
                    left_wrist = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST]

                    # Calculate the angle between the left shoulder, elbow, and wrist
                    left_angle = math.degrees(math.atan2(left_wrist.y - left_elbow.y, left_wrist.x - left_elbow.x) -
                                              math.atan2(left_shoulder.y - left_elbow.y, left_shoulder.x - left_elbow.x))
                    left_angle = abs(left_angle)

                    right_shoulder = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER]
                    right_elbow = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ELBOW]
                    right_wrist = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST]

                    # Calculate the angle between the right shoulder, elbow, and wrist
                    right_angle = math.degrees(math.atan2(right_wrist.y - right_elbow.y, right_wrist.x - right_elbow.x) -
                                               math.atan2(right_shoulder.y - right_elbow.y, right_shoulder.x - right_elbow.x))
                    right_angle = abs(right_angle)

                    # Check if the person is in a valid pose (standing)
                    if left_shoulder.y < left_elbow.y and right_shoulder.y < right_elbow.y:
                        # Check if the left arm is up
                        if left_angle < 60 and not left_arm_up:
                            left_arm_up = True
                        elif left_angle > 170 and left_arm_up:
                            left_curl_count += 1
                            left_arm_up = False
                        elif left_angle > 35:
                            cv2.putText(frame, "Keep your elbow close to your body. Don't lift your left elbow.", (10, 400), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                        # Check if the right arm is up
                        if right_angle < 60 and not right_arm_up:
                            right_arm_up = True
                        elif right_angle > 170 and right_arm_up:
                            right_curl_count += 1
                            right_arm_up = False
                        elif right_angle > 35:
                            cv2.putText(frame, "Keep your elbow close to your body. Don't lift your right elbow.", (10, 450), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                    else:
                        # If the person is not in a valid pose (not standing), provide a message or skip counting
                        cv2.putText(frame, "Stand up for accurate bicep curl counting", (10, 350), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                        # You may choose to skip counting or reset counts based on your requirement
                        left_arm_up = False
                        right_arm_up = False
                        left_curl_count = 0
                        right_curl_count = 0

                    if left_wrist.y < left_shoulder.y or right_wrist.y < right_shoulder.y:
                        cv2.putText(frame, "Keep your wrists below your shoulders", (10, 500), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                # Draw landmarks and angles on the frame
                mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                          mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                                          mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2))

        text_bg_color = (255, 255, 255)
        cv2.rectangle(frame, (0, 0), (350, 250), text_bg_color, -1)

        font_scale = 1.5
        font_color = (0, 0, 0)
        line_spacing = 40
        cv2.putText(frame, f"Left Curls: {left_curl_count}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_color, 2)
        cv2.putText(frame, f"Right Curls: {right_curl_count}", (10, 60 + line_spacing), cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_color, 2)
        cv2.putText(frame, f"Left Angle: {int(left_angle)} ", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_color, 2)
        cv2.putText(frame, f"Right Angle: {int(right_angle)} ", (10, 200), cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_color, 2)

        ret, buffer = cv2.imencode('.jpg', frame)
        if ret:
            frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(debug=True)
