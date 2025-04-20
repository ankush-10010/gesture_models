from app_onehand import get_args
import cv2 as cv
import csv
import copy
import numpy as np
import pyautogui
import time
import mediapipe as mp
from utils import CvFpsCalc
import os
from collections import Counter
from collections import deque
from app_onehand import KeyPointClassifier
from app_onehand import PointHistoryClassifier
from app_onehand import draw_bounding_rect
from app_onehand import draw_info
from app_onehand import draw_info_text
from app_onehand import draw_landmarks
from app_onehand import draw_point_history
from app_onehand import select_mode
from app_onehand import logging_csv
from app_onehand import pre_process_landmark
from app_onehand import pre_process_point_history
from app_onehand import calc_bounding_rect
from app_onehand import calc_landmark_list

def main():
    # Argument parsing #################################################################
    args = get_args()

    cap_device = args.device
    cap_width = args.width
    cap_height = args.height

    use_static_image_mode = args.use_static_image_mode
    min_detection_confidence = args.min_detection_confidence
    min_tracking_confidence = args.min_tracking_confidence

    use_brect = True

    # Camera preparation ###############################################################
    cap = cv.VideoCapture(cap_device)
    cap.set(cv.CAP_PROP_FRAME_WIDTH, cap_width)
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, cap_height)

    # Model load #############################################################
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=use_static_image_mode,
        max_num_hands=2,
        min_detection_confidence=min_detection_confidence,
        min_tracking_confidence=min_tracking_confidence,
    )

    keypoint_classifier = KeyPointClassifier()

    point_history_classifier = PointHistoryClassifier()

    # Read labels ###########################################################
    with open(r'C:\CODE\Machine_Learning\hand-gesture-recognition-mediapipe-main\model\keypoint_classifier\keypoint_classifier_label.csv',
              encoding='utf-8-sig') as f:
        keypoint_classifier_labels = csv.reader(f)
        keypoint_classifier_labels = [
            row[0] for row in keypoint_classifier_labels
        ]
    with open(
            r'C:\CODE\Machine_Learning\hand-gesture-recognition-mediapipe-main\model\point_history_classifier\point_history_classifier_label.csv',
            encoding='utf-8-sig') as f:
        point_history_classifier_labels = csv.reader(f)
        point_history_classifier_labels = [
            row[0] for row in point_history_classifier_labels
        ]

    # FPS Measurement ########################################################
    cvFpsCalc = CvFpsCalc(buffer_len=10)

    # Coordinate history #################################################################
    history_length = 16
    point_history = deque(maxlen=history_length)

    # Finger gesture history ################################################
    finger_gesture_history = deque(maxlen=history_length)

    #  ########################################################################
    mode = 0
    last_print_time_left=5.000000000000001
    last_print_time_right=5.00000000000001
    left_closed=False
    right_closed=False
    left_closed_time=5.0000000000000001
    while True:
        fps = cvFpsCalc.get()

        # Process Key (ESC: end) #################################################
        key = cv.waitKey(10)
        if key == 27:  # ESC
            break
        number, mode = select_mode(key, mode)

        # Camera capture #####################################################
        ret, image = cap.read()
        if not ret:
            break
        image = cv.flip(image, 1)  # Mirror display
        debug_image = copy.deepcopy(image)

        # Detection implementation #############################################################
        image = cv.cvtColor(image, cv.COLOR_BGR2RGB)

        image.flags.writeable = False
        results = hands.process(image)
        image.flags.writeable = True

        #  ####################################################################
        if results.multi_hand_landmarks is not None:
            for i,(hand_landmarks, handedness) in enumerate(zip(results.multi_hand_landmarks,
                                                  results.multi_handedness)):
                hand_label=handedness.classification[0].label
                # if hand_label=="Left":
                #     print("left")
                # Bounding box calculation
                brect = calc_bounding_rect(debug_image, hand_landmarks)
                # Landmark calculation
                landmark_list = calc_landmark_list(debug_image, hand_landmarks)

                # Conversion to relative coordinates / normalized coordinates
                pre_processed_landmark_list = pre_process_landmark(
                    landmark_list)
                pre_processed_point_history_list = pre_process_point_history(
                    debug_image, point_history)
                # Write to the dataset file
                logging_csv(number, mode, pre_processed_landmark_list,
                            pre_processed_point_history_list)

                # Hand sign classification
                hand_sign_id = keypoint_classifier(pre_processed_landmark_list)
                if hand_sign_id == 2:  # Point gesture
                    point_history.append(landmark_list[8])
                else:
                    point_history.append([0, 0])

                # Finger gesture classification
                finger_gesture_id = 0
                point_history_len = len(pre_processed_point_history_list)
                if point_history_len == (history_length * 2):
                    finger_gesture_id = point_history_classifier(
                        pre_processed_point_history_list)

                # Calculates the gesture IDs in the latest detection
                finger_gesture_history.append(finger_gesture_id)
                most_common_fg_id = Counter(
                    finger_gesture_history).most_common()
                # Drawing part
                debug_image = draw_bounding_rect(use_brect, debug_image, brect)
                debug_image = draw_landmarks(debug_image, landmark_list)
                debug_image = draw_info_text(
                    debug_image,
                    brect,
                    handedness,
                    keypoint_classifier_labels[hand_sign_id],
                    point_history_classifier_labels[most_common_fg_id[0][0]],
                )
                # if hand_label=="Left":
                #     print(keypoint_classifier_labels[hand_sign_id])
                #     # if keypoint_classifier_labels[hand_sign_id]
                if hand_label=="Left" and keypoint_classifier_labels[hand_sign_id]=="Close" and time.time()-last_print_time_left>5:
                    print("Left hand is closed")
                    last_print_time_left=time.time()
                if hand_label=="Right" and time.time()-last_print_time_right>5:
                    if keypoint_classifier_labels[hand_sign_id]=="Open":
                        print("RIght hand is open")
                        # pyautogui.leftClick(x=1832,y=20)
                        pyautogui.leftClick(x=1781,y=645)
                        last_print_time_right=time.time()
                # if (hand_label=="Left" and keypoint_classifier_labels[hand_sign_id]=="Close") and (hand_label=="Right" and keypoint_classifier_labels[hand_sign_id]=="Close"):
                #     print("conditions satisfied")
                # if hand_label=="Left" and keypoint_classifier_labels[hand_sign_id]=="Close":
                #     print("Left loop")
                #     if hand_label=="Right" and keypoint_classifier_labels[hand_sign_id]=="Close":
                #         print("right loop")
                #         print("Conditions satisfied 2")
                if hand_label=="Left" and keypoint_classifier_labels[hand_sign_id]=="Close":
                    left_closed=True
                if hand_label=="Right" and keypoint_classifier_labels[hand_sign_id]=="Close":
                    right_closed=True
                if left_closed and right_closed and time.time()-left_closed_time>5:
                    print("Both the hands are closed at the same time")
                    left_closed=False
                    right_closed=False
                    left_closed_time=time.time()
        else:
            point_history.append([0, 0])

        debug_image = draw_point_history(debug_image, point_history)
        debug_image = draw_info(debug_image, fps, mode, number)

        # Screen reflection #############################################################
        cv.imshow('Hand Gesture Recognition', debug_image)

    cap.release()
    cv.destroyAllWindows()
if __name__=="__main__":
    main()
