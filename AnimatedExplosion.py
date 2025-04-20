import pygame
class AnimatedExplosion(pygame.sprite.Sprite):  
    def __init__(self,frames,pos,groups):
        super().__init__(groups)
        self.frames=frames
        self.frames_index=0
        self.image=self.frames[self.frames_index]
        self.rect=self.image.get_frect(center=pos)
    def update(self,dt):
        self.frames_index+=20*dt
        if self.frames_index<len(self.frames):
            self.image=self.frames[int(self.frames_index)%len(self.frames)]
        else:
            self.kill()