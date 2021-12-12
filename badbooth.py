#!/usr/bin/env python3
#
# hacky little photobooth
# - wm
#

import os
import time
import pygame
import pygame.camera
import pygame.image
import configparser
import argparse
from pygame.locals import *

config = configparser.ConfigParser()
pygame.init()

joy = False
debug = True

CONFIG_FILE = os.path.expanduser('~/.badbooth.ini')
if not os.path.exists(CONFIG_FILE):
    print("Could not find %s" % CONFIG_FILE)
    exit(1)
else:
    config.read(CONFIG_FILE)


if config:
    dev_idx = config.getint("General","video_dev")
    outpath = config.get("General","path_photo")            # not fully supported yet
    assets = config.get("General","path_assets")            # not fully supported yet
    max_width = config.getint("Video","width")
    max_height = config.getint("Video","height")
    fullscreen = config.getint("Video","fullscreen")
    background = config.get("General","background")
    booth_title = config.get("General","title")
else:
    # paths
    dev_idx = 0
    outpath = "photos"
    assets = "assets"
    max_width = 1440
    max_height = 900
    background = 'bg.jpg'
    booth_title = "Photo Booth"

screen = pygame.display.set_mode((max_width,max_height), DOUBLEBUF)

if fullscreen == 1:
    pygame.display.toggle_fullscreen()

# default assets
font = pygame.font.SysFont("sans-serif",90)
bg_a = pygame.image.load(os.path.join(assets,background))
mod = (max_width * 1.0) / bg_a.get_width()
bg = pygame.transform.scale(bg_a, (int(bg_a.get_width() * mod), int(bg_a.get_height() * mod)))

if joy:
    icon_circle = pygame.image.load(os.path.join(assets,"circle.png"))
    icon_square = pygame.image.load(os.path.join(assets,"square.png"))
    icon_x = pygame.image.load(os.path.join(assets,"x.png"))
    icon_triangle = pygame.image.load(os.path.join(assets,"triangle.png"))
    icon_start = pygame.image.load(os.path.join(assets,"start.png"))
    take_photo_icons = [icon_circle, icon_square, icon_x, icon_triangle]
    take_newphoto_icons = [icon_start]
else:
    icon_mouse_l = pygame.image.load(os.path.join(assets,"mouse_l.png"))
    take_photo_icons = [icon_mouse_l]
    take_newphoto_icons = [icon_mouse_l]

s_photo = False

def debugout(s):
    print(s)
    return

def takephoto(dev_idx=0):
    shutter = pygame.mixer.music.load(os.path.join("assets","shutter.mp3"))
    pygame.camera.init()
    image = False
    camlist = pygame.camera.list_cameras()
    cam = pygame.camera.Camera(camlist[dev_idx],(max_width,max_height),'RGB')
    cam.start()
    pygame.mixer.music.play()
    image = cam.get_image()
    cam.stop()
    cam = False
    pygame.camera.quit()
    return image

def rendertext(t):
    return font.render(t, True, (255, 255, 255))


def countdown(seconds=3, screen=screen):
    boop = pygame.mixer.music.load(os.path.join("assets","boop.mp3"))
    text = ["Taking photo!","Hold on","Stand still","Get Ready..."]
    while seconds >= 0:
        pygame.mixer.music.play()
        draw_screen(rendertext(text[seconds]),[])
        time.sleep(1)
        seconds -= 1
    return

def system_exit():
    print("Exiting...")
    exit()
    return


def showresult(filename="photo",format="png"):
    global s_photo
    latest = pygame.image.load("%s.%s" % (filename, format))
    pygame.event.clear()
    draw_screen(latest,take_photo_icons, rendertext("Press a button to take a photo"))
    s_photo = False
    time.sleep(3)
    return

def saveimage(data, filename="photo", format="png"):
    return pygame.image.save(data, "%s.%s" % (filename, format))

def list_devices():
    pygame.camera.init()
    print("Available camera devices")
    print(" idx  camera")
    for idx, camera in enumerate(pygame.camera.list_cameras()):
        print(" %d    %s" % (idx, camera))

def draw_screen(data, icons, msg=False):
    screen.fill((255,255,255))
    ypos = ( screen.get_height() - data.get_height() ) // 2
    xpos = ( screen.get_width() - data.get_width() ) // 2
    screen.blit(bg, (0, 0))
    screen.blit(data, (xpos, ypos))
    icon_offset = 0
    icon_xpos = 0
    for loadedicon in icons:
        mod = loadedicon.get_width() * 0.0006 
        icon = pygame.transform.scale(loadedicon, (int(loadedicon.get_width() * mod), int(loadedicon.get_height() * mod)))
        icon_ypos = ( screen.get_height() - icon.get_height() - 10 )
        if len(icons) > 1:
            icon_offset += icon.get_width() + icon_xpos
            icon_xpos = ( screen.get_width() / len(icons) ) // 2
            screen.blit(icon, (icon_xpos + icon_offset, icon_ypos))
        else:
            icon_xpos = ( screen.get_width() - ( icon.get_width() * len(icons) )) // 2
            screen.blit(icon, (icon_xpos, icon_ypos))
    if msg:
        msg_xpos = ( screen.get_width() - msg.get_width() ) // 2
        msg_ypos = ( screen.get_height() - msg.get_height() - ( icon.get_height() * 1.3))
        screen.blit(msg,(msg_xpos, msg_ypos))
    update_display()
    return


def update_display():
    pygame.display.flip()
    return

def newscreen(title=""):
    draw_screen(rendertext(title),take_photo_icons, rendertext("Press a button to take a photo") )
    update_display();

def photostuff(dev_idx):
    global s_photo
    s_photo = True
    # start countdown
    countdown()
    # take photo
    outfile = time.strftime('%Y%m%d-%H%M%S', time.localtime())
    result = takephoto(dev_idx)
    outdest = os.path.join(outpath, outfile)
    saveimage(result, outdest)
    showresult(outdest)
    return


def main(args=None):

    if args:
        if args.list:
            list_devices()
            exit(0)

    pygame.mouse.set_visible(False)
    #pad = pygame.joystick.Joystick(0)
    #pad.init()
    clock = pygame.time.Clock()
    fps = 60
    s_photo = False
    newscreen(booth_title)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                system_exit()
            if event.type == pygame.KEYDOWN:
                # keyboard
                if event.key == pygame.K_ESCAPE:
                    system_exit()
                elif event.key == pygame.K_SPACE:
                    if not s_photo:
                        photostuff(dev_idx)
                elif event.key == pygame.K_RETURN:
                        newscreen(booth_title)
                else:
                    # wait
                    pass
            elif event.type == pygame.JOYBUTTONDOWN:
                # joysticks
                if event.button != 9 :
                    if not s_photo:
                        photostuff(dev_idx)
                elif event.button == 9:
                    newscreen(booth_title)
                else:
                    # wait
                    pass
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # mouse
                if event.button != 2 :
                    if not s_photo:
                        photostuff(dev_idx)
                elif event.button == 2:
                    newscreen(booth_title)
                else:
                    # wait
                    pass
        clock.tick(60)
    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--list', action='store_true', default=False, required=False)

    args = parser.parse_args()
    main(args)
