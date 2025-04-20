import pygame
import time
import sys
def collision(player,meteor_sprites,game_over_sound,laser_sprites,AnimatedExplosion,explosion_frames,all_sprites,explosion_sound):
    global running
    collision_sprites=pygame.sprite.spritecollide(player,meteor_sprites,True,pygame.sprite.collide_mask) #setting it to true means it kills the meteor_sprites
    if collision_sprites:
        game_over_sound.play()
        # time.sleep(2)
        running=True
        # pygame.quit()
        # sys.exit()
    for laser in laser_sprites:
        meteor_hit=pygame.sprite.spritecollide(laser,meteor_sprites,True) #dont use mask when not needed , becauase its very hardware intensive
        if meteor_hit: 
            laser.kill()
            AnimatedExplosion(explosion_frames,laser.rect.midtop,all_sprites)
            explosion_sound.play()
def display_score(font,screen_width,screen_height,display_surface):
    current_time=pygame.time.get_ticks()//100
    text_surf=font.render(str(current_time),True,(0,254,0))
    text_rect=text_surf.get_frect(midbottom=(screen_width/2,screen_height-80))
    display_surface.blit(text_surf,text_rect)
    pygame.draw.rect(display_surface,(0,254,0),text_rect.inflate(20,20).move(0,-5),5,5)