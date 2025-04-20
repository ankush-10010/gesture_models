import pygame
from random import randint,uniform
from laser import Laser


class Player(pygame.sprite.Sprite):
    def __init__(self,groups,screen_width,screen_height,laser_surf,laser_sound,all_sprites,laser_sprites,laser_mode,laser_sound_rapid_fire):
        super().__init__(groups)
        self.first_execution_time_rapid=None
        self.last_execution_time_rapid=None
        self.first_execution_time_single=None
        self.image=pygame.image.load(r"C:\Users\ankus\Downloads\player.png").convert_alpha()
        self.rect=self.image.get_frect(center=(screen_width/2,screen_height/2))
        self.direction=pygame.Vector2() #for x and y direction , it initiates x,y direction , for xyz direction use vector3
        self.speed=300
        #cooldown attributes of laser fires
        self.can_shoot=True
        self.laser_shoot_time=0
        self.cooldown_duration=4000
        self.screen_width=screen_width
        self.screen_height=screen_height
        self.laser_surf=laser_surf
        self.laser_sound=laser_sound
        self.all_sprites=all_sprites
        self.laser_sprites=laser_sprites
        self.laser_mode="single_fire"
        self.laser_sound_rapid_fire=laser_sound_rapid_fire
        #mask
        self.mask=pygame.mask.from_surface(self.image)
    def laser_timer(self):
        if not self.can_shoot:  
            current_time=pygame.time.get_ticks() 
            if current_time-self.laser_shoot_time>=self.cooldown_duration:
                self.can_shoot=True
    def laser_timer_rapid(self):
        if not self.can_shoot:
            current_time=pygame.time.get_ticks()
            if current_time-self.last_execution_time>=5000:
                self.can_shoot=True
    def update(self,dt):
        keys=pygame.key.get_pressed()
        self.direction.x=int(keys[pygame.K_RIGHT])-int(keys[pygame.K_LEFT]) or self.gesture_x
        self.direction.y=int(keys[pygame.K_DOWN])-int(keys[pygame.K_UP]) or self.gesture_y
        self.direction=self.direction.normalize() if self.direction else self.direction
        self.rect.center+=self.direction*self.speed*dt
        keys1=pygame.key.get_just_pressed()
        if keys1[pygame.K_SPACE] and self.can_shoot==True:
            current_time=pygame.time.get_ticks()
            if self.laser_mode=="single_fire":
                Laser(self.laser_surf,self.rect.midtop,(self.all_sprites,self.laser_sprites))
                self.can_shoot=False
                self.laser_shoot_time=pygame.time.get_ticks()
                self.first_execution_time_single=self.laser_shoot_time
                self.laser_sound.play()
            elif self.laser_mode=="rapid_fire":
                Laser(self.laser_surf,self.rect.midtop,(self.all_sprites,self.laser_sprites))
                self.laser_shoot_time=pygame.time.get_ticks()
                if self.first_execution_time_rapid is None:
                    self.first_execution_time_rapid=self.laser_shoot_time
                if current_time-self.first_execution_time_rapid>=5000:
                    if self.last_execution_time_rapid is None:
                        self.last_execution_time_rapid=current_time
                    self.can_shoot=False
                self.laser_sound.play()
        if self.gesture_shoot==True and self.can_shoot==True:
            current_time=pygame.time.get_ticks()
            if self.laser_mode=="single_fire":
                Laser(self.laser_surf,self.rect.midtop,(self.all_sprites,self.laser_sprites))
                self.can_shoot=False
                self.laser_shoot_time=pygame.time.get_ticks()
                self.first_execution_time_single=self.laser_shoot_time
                self.laser_sound.play()
            elif self.laser_mode=="rapid_fire":
                    Laser(self.laser_surf,self.rect.midtop,(self.all_sprites,self.laser_sprites))
                    self.laser_shoot_time=pygame.time.get_ticks()
                    if self.first_execution_time_rapid is None:
                        self.first_execution_time_rapid=self.laser_shoot_time
                    if current_time-self.first_execution_time_rapid>=5000:
                        if self.last_execution_time_rapid is None:
                            self.last_execution_time_rapid=current_time
                        self.can_shoot=False
                    self.laser_sound.play()
        if self.laser_mode=="rapid_fire" and self.can_shoot==False:
            current_time=pygame.time.get_ticks()
            if current_time-self.last_execution_time_rapid>=5000:
                self.can_shoot=True
                self.first_execution_time_rapid=None
                self.last_execution_time_rapid=None
        if self.laser_mode=="single_fire" and self.can_shoot==False:
            current_time=pygame.time.get_ticks()
            if self.first_execution_time_single is None:
                self.first_execution_time_single=pygame.time.get_ticks()
            if current_time-self.first_execution_time_single>=400:
                self.can_shoot=True
                self.first_execution_time_single=None
        # if keys1[pygame.K_r] and self.laser_mode=="single_fire":
        #     self.laser_mode="rapid_fire"
        #     print(self.laser_mode)
        if self.gesture_detected==True and self.laser_mode=="single_fire":
            self.laser_mode="rapid_fire"
            print(self.laser_mode)
        if keys1[pygame.K_s] and self.laser_mode=="rapid_fire":
            self.laser_mode="single_fire"
            print(self.laser_mode)
    def set_gesture_input(self,gesture_detected,gesture_x,gesture_y,gesture_shoot):
        self.gesture_detected=gesture_detected
        self.gesture_x=gesture_x
        self.gesture_y=gesture_y
        self.gesture_shoot=gesture_shoot
