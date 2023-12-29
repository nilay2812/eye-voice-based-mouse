import cv2
import mediapipe as mp
import pyautogui
import speech_recognition as sr


cam = cv2.VideoCapture(0)


face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)


screen_w, screen_h = pyautogui.size()


recognizer = sr.Recognizer()
microphone = sr.Microphone()


input_mode = "voice_command"

voice_click_flag = False

def move_cursor(direction):
    if direction == "up":
        pyautogui.move(0, -100)
    elif direction == "down":
        pyautogui.move(0, 100)
    elif direction == "left":
        pyautogui.move(-100, 0)
    elif direction == "right":
        pyautogui.move(100, 0)

def listen_for_commands():
    with microphone as source:
        print("Listening for voice commands...")
        audio = recognizer.listen(source)

    try:
        command = recognizer.recognize_google(audio)  # Use Google Web Speech API for recognition
        print("You said:", command)
        return command.lower()  # Convert the recognized command to lowercase for case-insensitivity
    except sr.UnknownValueError:
        print("Could not understand audio.")
        return None
    except sr.RequestError as e:
        print("Could not request results; {0}".format(e))
        return None

while True:
    if input_mode == "eye_tracking":
        _, frame = cam.read()
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process the frame to detect facial landmarks
        output = face_mesh.process(rgb_frame)
        landmark_points = output.multi_face_landmarks

        frame_h, frame_w, _ = frame.shape

        if landmark_points:
            landmarks = landmark_points[0].landmark

            left_eye_open = landmarks[159].y < landmarks[145].y

            if left_eye_open:
                cv2.putText(frame, "Left Eye Open", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            else:
                cv2.putText(frame, "Left Eye Closed", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            # Check if the left eye is closed and trigger a left click
            if not left_eye_open:
                pyautogui.click()

            # Calculate the position of specific landmarks
            for id, landmark in enumerate(landmarks[474:478]):
                x = int(landmark.x * frame_w)
                y = int(landmark.y * frame_h)
                cv2.circle(frame, (x, y), 3, (0, 255, 0))
                
                if id == 1:
                    screen_x = screen_w * landmark.x
                    screen_y = screen_h * landmark.y
                    pyautogui.moveTo(screen_x, screen_y)

            left = [landmarks[145], landmarks[159]]

            for landmark in left:
                x = int(landmark.x * frame_w)
                y = int(landmark.y * frame_h)
                cv2.circle(frame, (x, y), 3, (0, 255, 255))

            if (left[0].y - left[1].y) < 0.021:
                pyautogui.click()
                pyautogui.sleep(1)

        cv2.imshow('Eye Controlled Mouse', frame)
    
    # Switch input mode based on key press
    key = cv2.waitKey(1)
    if key == ord('e'):
        input_mode = "eye_tracking"
        cam = cv2.VideoCapture(0)  # Reinitialize the camera when switching to eye mode
    elif key == ord('v'):
        input_mode = "voice_command"
        cam.release()  # Release the camera when switching to voice mode

    # Listen for voice commands when in voice command mode
    if input_mode == "voice_command":
        voice_command = listen_for_commands()

        if voice_command:
            if "scroll up" in voice_command:
                pyautogui.scroll(-100)  # Scroll up
            elif "scroll down" in voice_command:
                pyautogui.scroll(100)  # Scroll down
            elif "move up" in voice_command:
                move_cursor("up")
            elif "move down" in voice_command:
                move_cursor("down")
            elif "move left" in voice_command:
                move_cursor("left")
            elif "move right" in voice_command:
                move_cursor("right")
            elif "left click" in voice_command:
                pyautogui.click()  # Trigger a left click using voice command
            elif "exit now" in voice_command:
                exit(0)

cv2.destroyAllWindows()
cam.release()
