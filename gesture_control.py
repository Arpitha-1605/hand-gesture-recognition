import cv2
import mediapipe as mp
import numpy as np
import pyautogui
import time

# Initialize MediaPipe
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

prev_gesture = ""

with mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7) as hands:
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        image = cv2.flip(frame, 1)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        results = hands.process(image_rgb)

        gesture = "Detecting..."

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:

                lm_list = []

                # Get landmarks
                for id, lm in enumerate(hand_landmarks.landmark):
                    h, w, c = image.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lm_list.append((id, cx, cy))

                mp_draw.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                if len(lm_list) != 0:

                    thumb = lm_list[4]
                    index = lm_list[8]

                    # -------- DISTANCE --------
                    length = np.hypot(index[1] - thumb[1],
                                      index[2] - thumb[2])

                    # Show distance
                    cv2.putText(image, f"Dist: {int(length)}", (50, 200),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

                    # -------- VOLUME CONTROL --------
                    if length < 40:
                        gesture = "Volume Down 🔉"
                        pyautogui.press("volumedown")
                        time.sleep(0.3)

                    elif length > 120:
                        gesture = "Volume Up 🔊"
                        pyautogui.press("volumeup")
                        time.sleep(0.3)

                    else:
                        # -------- NORMAL GESTURES --------

                        thumb_tip_y = lm_list[4][2]
                        thumb_ip = lm_list[3][2]

                        index_tip = lm_list[8][2]
                        middle_tip = lm_list[12][2]
                        ring_tip = lm_list[16][2]
                        pinky_tip = lm_list[20][2]

                        index_mcp = lm_list[5][2]
                        middle_mcp = lm_list[9][2]
                        ring_mcp = lm_list[13][2]
                        pinky_mcp = lm_list[17][2]

                        # ✊ PAUSE
                        if (index_tip > index_mcp and
                            middle_tip > middle_mcp and
                            ring_tip > ring_mcp and
                            pinky_tip > pinky_mcp):
                            gesture = "PAUSE ✊"

                        # 👍 PLAY
                        elif (thumb_tip_y < thumb_ip and
                              index_tip > index_mcp and
                              middle_tip > middle_mcp):
                            gesture = "PLAY 👍"

                        # ☝️ NEXT
                        elif (index_tip < index_mcp and
                              middle_tip > middle_mcp and
                              ring_tip > ring_mcp and
                              pinky_tip > pinky_mcp):
                            gesture = "NEXT 👉"

                        # ✌️ BACK
                        elif (index_tip < index_mcp and
                              middle_tip < middle_mcp and
                              ring_tip > ring_mcp and
                              pinky_tip > pinky_mcp):
                            gesture = "BACK ✌️"

                        else:
                            gesture = "Detecting..."

        # -------- ACTION CONTROL --------
        if gesture != prev_gesture:
            prev_gesture = gesture

            if gesture == "PLAY 👍":
                pyautogui.press("space")

            elif gesture == "PAUSE ✊":
                pyautogui.press("space")

            elif gesture == "NEXT 👉":
                pyautogui.press("right")

            elif gesture == "BACK ✌️":
                pyautogui.press("left")

        # -------- UI --------
        cv2.rectangle(image, (30, 50), (500, 150), (0, 0, 0), -1)

        cv2.putText(image, gesture, (50, 120),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)

        cv2.imshow("Gesture + Volume Control", image)

        if cv2.waitKey(1) & 0xFF == 27:
            break

cap.release()
cv2.destroyAllWindows()