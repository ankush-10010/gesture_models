import pygame
from random import randint
from star import Star
from player import Player
from meteor import Meteor
from AnimatedExplosion import AnimatedExplosion
from functions import collision
from functions import display_score

from app_onehand import get_args
import cv2 as cv
import csv
import copy
import time
import mediapipe as mp
from utils import CvFpsCalc
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

import threading 
#general setup
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
    with open(r'C:\CODE\Machine_Learning\SpaceInvader_Improved\model\keypoint_classifier\keypoint_classifier_label.csv',
              encoding='utf-8-sig') as f:
        keypoint_classifier_labels = csv.reader(f)
        keypoint_classifier_labels = [
            row[0] for row in keypoint_classifier_labels
        ]
    with open(
            r'C:\CODE\Machine_Learning\SpaceInvader_Improved\model\point_history_classifier\point_history_classifier_label.csv',
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
    last_ss_time=time.time()-2.000000001
    pygame.init() #for initialising the game
    info=pygame.display.Info() #it gets the size of the window that the user is working on
    screen_width=info.current_w
    screen_height=info.current_h
    display_surface=pygame.display.set_mode((screen_width-50,screen_height-70))
    game_icon=pygame.image.load(r"C:\CODE\Python\SpaceInvader\Images\game_icon.png")
    pygame.display.set_icon(game_icon)
    pygame.display.set_caption("Space Invader") # sets the title of the game to be space invader
    pygame.display.get_window_size()
    running=True
    clock=pygame.time.Clock()
    #import
    meteor_surf=pygame.image.load(r"C:\CODE\Python\SpaceInvader\Images\meteor.png").convert_alpha()
    laser_surf=pygame.image.load(r"C:\CODE\Python\SpaceInvader\Images\laser.png").convert_alpha()
    star_surf=pygame.image.load(r"C:\CODE\Python\SpaceInvader\Images\star.png").convert_alpha()
    font=pygame.font.Font(r"C:\CODE\Python\SpaceInvader\Rustic_Barn.ttf",40) #(font style,size)
    explosion_frames=[]
    for i in range(20):
        image_path=fr"C:\CODE\Python\SpaceInvader\explosion\explosion\{i}.png"
        try:
            image=pygame.image.load(image_path).convert_alpha()
            explosion_frames.append(image)
        except pygame.error as e:
            print(fr"Could not load image {image_path}:{e}") 
    laser_sound=pygame.mixer.Sound(r"C:\CODE\Python\SpaceInvader\Sound\laser.wav")
    laser_sound.set_volume(0.5)
    laser_sound_rapid_fire=pygame.mixer.Sound(r"C:\CODE\Python\SpaceInvader\Sound\rapid_fire_sound.mp3")
    explosion_sound=pygame.mixer.Sound(r"C:\CODE\Python\SpaceInvader\Sound\explosion.wav")
    game_over_sound=pygame.mixer.Sound(r"C:\CODE\Python\SpaceInvader\Sound\game_over.mp3")
    game_music=pygame.mixer.Sound(r"C:\CODE\Python\SpaceInvader\Sound\game_music.wav")
    game_music.set_volume(0.3)
    game_music.play(loops=-1) #will play the music infinetely,as long as the code runs
    #Sprites
    all_sprites=pygame.sprite.Group()
    meteor_sprites=pygame.sprite.Group()
    laser_sprites=pygame.sprite.Group()
    for i in range (30):
        Star(all_sprites,star_surf,screen_width-100,screen_height-100) #the all sprites is a group and star_surf is a surface of the star
    player=Player(all_sprites,screen_width,screen_height,laser_surf,laser_sound,all_sprites,laser_sprites,"single_fire",laser_sound_rapid_fire)
    #custom events (meteor events)
    meteor_events=pygame.event.custom_type()
    pygame.time.set_timer(meteor_events,500) #here its 500 miliseconds (1/2 second)

    def hand_gesture_detection():
        global gesture_detected
        global gesture_x
        global gesture_y
        global left_close
        global right_close
        global down
        global up
        global gesture_shoot
        gesture_shoot=False
        gesture_x=0
        gesture_y=0
        gesture_detected=None
        mode=0
        down=False
        up=False
        left_close=False
        right_close=False
        last_print_time_left=5.0000000000000001
        last_print_time_left_open=5.00000000001
        last_print_time_right=5.000000000000001
        left_closed_time=5.00000000000000001
        last_down_time=5.00000000000000001
        right_closed=False
        left_closed=False
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

                    #movement of the player in x direction


                    if hand_label=="Left" and keypoint_classifier_labels[hand_sign_id]=="Open":
                        print("Left hand is Open")
                        gesture_x=0
                        left_close=False
                    elif hand_label=="Left" and keypoint_classifier_labels[hand_sign_id]=="Close":
                        print("Left hand is Closed")
                        gesture_x=-1
                        left_close=True
                    elif hand_label=="Right" and keypoint_classifier_labels[hand_sign_id]=="Close":
                        print("Right hand is Closed")
                        gesture_x=+1
                        right_close=True
                    elif hand_label=="Right" and keypoint_classifier_labels[hand_sign_id]=="Open":
                        print("Right hand is Open")
                        gesture_x=0
                        right_close=False
                    else:
                        gesture_x=0
                    if left_close and not right_close:
                        gesture_x=-1
                    elif right_close and not left_close:
                        gesture_x=+1
                    else:
                        gesture_x=0
                    if left_closed and right_closed and time.time()-left_closed_time>5:
                        print("Both the hands are closed at the same time")
                        left_closed=False
                        right_closed=False
                        left_closed_time=time.time()
        
                        #movement of the player in y direction


                    if hand_label=="Left" and keypoint_classifier_labels[hand_sign_id]=="TUP":
                        print("Left thumb is up")
                        # gesture_y=-1
                        # up=True
                    elif hand_label=="Left" and keypoint_classifier_labels[hand_sign_id]=="TDown":
                        print("Left thumb is down")
                        gesture_y=+1
                        down=True
                    elif hand_label=="Right" and keypoint_classifier_labels[hand_sign_id]=="TDown":
                        print("Right thumb is down")
                        # gesture_y=+1
                        # down=True
                    elif hand_label=="Right" and keypoint_classifier_labels[hand_sign_id]=="TUP":
                        print("Right thumb is up")
                        gesture_y=-1
                        up=True
                    else:
                        gesture_y=0
                    # if down and not up:
                    #     gesture_y=+1
                    # elif up and not down:
                    #     gesture_y=-1
                    # else:
                    #     gesture_y=0
                    if down and up and time.time()-last_down_time>5:
                        down=False
                        up=False
                        last_down_time=time.time()

                    # deals with the shooting of the player

                    if keypoint_classifier_labels[hand_sign_id]=="Shoot":
                        print("Shooting is on")
                        gesture_shoot=True
                    elif keypoint_classifier_labels[hand_sign_id]!="Shoot":
                        print("shooting gesture is off")
                        gesture_shoot=False


                        
            else:
                point_history.append([0, 0])

            debug_image = draw_point_history(debug_image, point_history)
            debug_image = draw_info(debug_image, fps, mode, number)
            # Screen reflection #############################################################
            cv.imshow('Hand Gesture Recognition', debug_image)
        cap.release()
        cv.destroyAllWindows()
    gesture_thread=threading.Thread(target=hand_gesture_detection,daemon=True)
    gesture_thread.start()
    while running: 
        dt= clock.tick(300)/1000
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                running=False
            if event.type==meteor_events:
                x,y=randint(0,screen_width),randint(-200,-100)
                Meteor(meteor_surf,(x,y),(all_sprites,meteor_sprites))
        player.set_gesture_input(gesture_detected,gesture_x,gesture_y,gesture_shoot)
        display_surface.fill("#3a2e2f")
        all_sprites.update(dt)
        collision(player,meteor_sprites,game_over_sound,laser_sprites,AnimatedExplosion,explosion_frames,all_sprites,explosion_sound)
        #drawing the game   
        display_surface.blit(player.image,player.rect)
        display_score(font,screen_width,screen_height,display_surface)
        all_sprites.draw(display_surface)
        pygame.display.update() #pygame.diplay.flip() is also pretty much same

pygame.quit()  #opposite of pygame.init() , deinitilises everything

if __name__=="__main__":
    main()
