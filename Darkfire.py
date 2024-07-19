import tkinter as tk
from tkinter import Menu, messagebox
import threading
import subprocess
import cv2
import Magnifier
import mediapipe as mp
import pyautogui
import time
import Text_to_speech

pyautogui.FAILSAFE = False
# Global variables
tracking_active = threading.Event()


# Function to start eye tracking
def start_tracking():
    if not tracking_active.is_set():
        tracking_active.set()
        threading.Thread(target=run_tracking).start()


def run_tracking():
    pyautogui.FAILSAFE = False  # Disable fail-safe for this example

    cam = cv2.VideoCapture(4)  # Change the camera index if needed
    # Reduce the resolution for faster processing
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 800)

    face_mesh = mp.solutions.face_mesh.FaceMesh(
        static_image_mode=False,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.6,
        min_tracking_confidence=0.6
    )
    screen_w, screen_h = pyautogui.size()

    # Landmarks for the pupil centers
    LEFT_PUPIL_CENTER = 473
    RIGHT_PUPIL_CENTER = 468

    # Define landmarks for left and right eyes
    LEFT_EYE = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
    RIGHT_EYE = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]

    # Calibration data
    initial_left_pupil_pos = None
    initial_right_pupil_pos = None

    # Blink detection data
    left_wink_start_time = None
    right_wink_start_time = None
    wink_duration_threshold = 0.5  # seconds

    def get_pupil_center(landmarks, pupil_center_index):
        return landmarks[pupil_center_index].x, landmarks[pupil_center_index].y

    def calculate_eye_aspect_ratio(eye_landmarks, landmarks):
        # Vertical eye landmarks
        v1 = landmarks[eye_landmarks[1]].y - landmarks[eye_landmarks[5]].y
        v2 = landmarks[eye_landmarks[2]].y - landmarks[eye_landmarks[4]].y

        # Horizontal eye landmark
        h = landmarks[eye_landmarks[0]].x - landmarks[eye_landmarks[3]].x

        # Eye Aspect Ratio
        ear = (v1 + v2) / (2.0 * h)
        return ear

    while True:
        _, frame = cam.read()
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        output = face_mesh.process(rgb_frame)
        landmark_points = output.multi_face_landmarks
        frame_h, frame_w, _ = frame.shape

        if landmark_points:
            landmarks = landmark_points[0].landmark

            left_pupil_center = get_pupil_center(landmarks, LEFT_PUPIL_CENTER)
            right_pupil_center = get_pupil_center(landmarks, RIGHT_PUPIL_CENTER)

            if initial_left_pupil_pos is None or initial_right_pupil_pos is None:
                # Calibrate the initial pupil positions
                initial_left_pupil_pos = left_pupil_center
                initial_right_pupil_pos = right_pupil_center

            # Calculate the changes in pupil positions
            delta_left_x = left_pupil_center[0] - initial_left_pupil_pos[0]
            delta_left_y = left_pupil_center[1] - initial_left_pupil_pos[1]
            delta_right_x = right_pupil_center[0] - initial_right_pupil_pos[0]
            delta_right_y = right_pupil_center[1] - initial_right_pupil_pos[1]

            # Average the deltas for smoother movement
            delta_x = (delta_left_x + delta_right_x) / 2
            delta_y = (delta_left_y + delta_right_y) / 2

            # Scale the delta to control the sensitivity
            sensitivity = 1.2  # Adjust this value to control the sensitivity
            screen_x = screen_w / 2 + delta_x * screen_w * sensitivity
            screen_y = screen_h / 2 + delta_y * screen_h * sensitivity

            pyautogui.moveTo(screen_x, screen_y)

            # Calculate eye aspect ratios
            left_ear = calculate_eye_aspect_ratio(LEFT_EYE, landmarks)
            right_ear = calculate_eye_aspect_ratio(RIGHT_EYE, landmarks)

            # Detect winks (adjust these thresholds as needed)
            current_time = time.time()
            print(f"Left EAR: {left_ear:.2f}, Right EAR: {right_ear:.2f}")  # Debugging print
            if left_ear < 0.02 and right_ear > 0.05:
                if left_wink_start_time is None:
                    left_wink_start_time = current_time
                elif current_time - left_wink_start_time >= wink_duration_threshold:
                    print("Left wink detected")
                    pyautogui.click(button='left')
                    print("LEFT_CLICK")
                    left_wink_start_time = 0.5  # Reset wink start time
                    pyautogui.sleep(0.5)  # Prevent multiple clicks
            else:
                left_wink_start_time = 0.5  # Reset if eye is open

            if right_ear < 0.02 and left_ear > 0.05:
                if right_wink_start_time is None:
                    right_wink_start_time = current_time
                elif current_time - right_wink_start_time >= wink_duration_threshold:
                    print("Right wink detected")
                    pyautogui.click(button='right')
                    print("RIGHT_CLICK")
                    right_wink_start_time = 0.5  # Reset wink start time
                    pyautogui.sleep(0.5)  # Prevent multiple clicks
            else:
                right_wink_start_time = 0.5  # Reset if eye is open

            # Visualize pupil landmarks and center
            for pupil_center in [left_pupil_center, right_pupil_center]:
                x = int(pupil_center[0] * frame_w)
                y = int(pupil_center[1] * frame_h)
                cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)

        cv2.imshow("Pupil Controlled Mouse", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()


# Function to stop eye tracking
def stop_tracking():
    if tracking_active.is_set():
        tracking_active.clear()
        cv2.destroyAllWindows()
        root.destroy()
        print("Stopping eye tracking...")


# Function to exit the application
def exit_app():
    stop_tracking()  # Ensure tracking is stopped before exiting
    root.destroy()


# Function for Magnifier
def magnifier():
    if __name__ == "__main__":
        app = Magnifier.MagnifierApp(root)
        root.mainloop()


# Function to launch Magnifier as a subprocess (if needed)
def magnifiers():
    subprocess.Popen(['python', 'Magnifier.py'])


# Function for Text to Speech
def text_to_speech():
    app = Text_to_speech.TextToSpeech(root)
    app.open_tts_window()
    root.mainloop()


if __name__ == "__main__":
    # Create the main window
    root = tk.Tk()
    root.title("Eye Tracking Control")
    root.configure(bg="lightblue")

    # Get screen dimensions
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Calculate a suitable window size
    window_width = max(800, screen_width - 10)  # Limit max width to 800
    window_height = max(600, screen_height - 100)  # Limit max height to 600

    # Center the window
    x_position = (screen_width - window_width) // 2
    y_position = (screen_height - window_height) // 2

    root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

    # Create the menu
    menu = Menu(root)
    root.config(menu=menu)

    options_menu = Menu(menu, tearoff=0)
    menu.add_cascade(label="Options", menu=options_menu)
    options_menu.add_command(label="Text to Speech", command=text_to_speech)
    options_menu.add_command(label="Magnifier", command=magnifier)
    options_menu.add_command(label="Exit", command=exit_app)

    # Create the Activate menu
    activate_menu = tk.Menu(menu, tearoff=0)
    menu.add_cascade(label="Activate", menu=activate_menu)

    # Add the Start and Stop Tracking commands to the Activate menu
    activate_menu.add_command(label="Start Tracking", command=start_tracking)
    activate_menu.add_command(label="Stop Tracking", command=stop_tracking)

    # Start the main event loop
    root.mainloop()
