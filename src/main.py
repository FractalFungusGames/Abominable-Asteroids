#!/usr/bin/env python3

#    LICENSE INFORMATION: GNU GPLv3.0-or-later

#    Abominable Asteroids is a clone of the classic Asteroids video game.

#    Copyright (C) 2026 Fractal Fungus Games <FractalFungusGames@proton.me>

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

#    < --- PROGRAM BEGINS BELOW --- >

version = 'v1.0'

import pygame
import random
import time
import os
import sys

# define constants
UP = pygame.math.Vector2(0,-1)
RESOLUTION = (1280, 720)
CENTER = (RESOLUTION[0]/2, RESOLUTION[1]/2)
BACKGROUND_POSITION = (0,0)
FRAME_RATE = 60
SPLASH_TIME = 5.9

# customizable parameters
MANEUVERABILITY = 3
SHIP_ACCELERATION = 0.18
FUEL_BURN = 1
BULLET_SPEED = 15
BULLET_MOMENTUM = 0.1
NUMBER_OF_ASTEROIDS = 2
MIN_ASTEROID_SPEED = 0.5
MAX_ASTEROID_SPEED = 2.5
STARTING_AMMO = 40
STARTING_FUEL = 650
MAX_FUEL = 800
MAX_AMMO = 50
FONT_COLOR = 'orange'
DROP_FREQUENCY = 5
AMMO_DROP_SIZE = 25
FUEL_DROP_SIZE = 250
POPUP_TIME = 1

KEY_MAP = {
    'shoot': [pygame.K_SPACE],
    'select': [pygame.K_RETURN],
    'pause': [pygame.K_ESCAPE],
    'accelerate': [pygame.K_UP, pygame.K_w],
    'up': [pygame.K_UP, pygame.K_w],
    'down': [pygame.K_DOWN, pygame.K_s],
    'left': [pygame.K_LEFT, pygame.K_a],
    'right': [pygame.K_RIGHT, pygame.K_d],
}

JOYSTICK_MAP = {
    'Xbox': {
        'shoot': [0],
        'select': [0],
        'pause': [11, 7],
        'accelerate': [(0, 1)],
        'up': [(0, 1)],
        'down': [(0, -1)],
        'left': [(-1, 0)],
        'right': [(1, 0)],
        'accelerate_left': [(-1,1)],
        'accelerate_right': [(1,1)],
    },
    'PS4': {
        'shoot': [0],
        'select': [0],
        'pause': [6],
        'accelerate': [11],
        'up': [11],
        'down': [12],
        'left': [13],
        'right': [14],
    },
    'PS5': {
        'shoot': [0],
        'select': [0],
        'pause': [9],
        'accelerate': [(0, 1)],
        'up': [(0, 1)],
        'down': [(0, -1)],
        'left': [(-1, 0)],
        'right': [(1, 0)],
        'accelerate_left': [(-1,1)],
        'accelerate_right': [(1,1)],
    },
    'Switch': {
        'shoot': [0],
        'select': [0],
        'pause': [6],
        'accelerate': [11],
        'up': [11],
        'down': [12],
        'left': [13],
        'right': [14],
    },
}

# game objects
class AbominableAsteroids:

    def __init__(self):

        pygame.init()

        self.screen = pygame.display.set_mode(RESOLUTION, pygame.SCALED | pygame.DOUBLEBUF)
        pygame.display.toggle_fullscreen()
        pygame.display.set_caption('Abominable Asteroids')

        self.icon = loadAsset('spaceship_flames', 'image')
        pygame.display.set_icon(self.icon)

        pygame.mouse.set_visible(False)

        self.clock = pygame.time.Clock()
        self.startTime = 0
        self.winTime = 0
        self.time = 0

        pygame.joystick.init()
        self.joystick = None
        self.joystickName = ''
        self.joystickID = ''

        self.backgroundImages = {
            1: loadAsset('background1', 'image', False),
            2: loadAsset('background2', 'image', False),
            3: loadAsset('background3', 'image', False),
            4: loadAsset('background4', 'image', False),
            5: loadAsset('background5', 'image', False),
            6: loadAsset('background6', 'image', False),
            7: loadAsset('background7', 'image', False),
            8: loadAsset('background8', 'image', False),
            9: loadAsset('background9', 'image', False),
            10: loadAsset('background10', 'image', False),
            }

        self.menuBackground = loadAsset('menu_background', 'image', False)
        self.background = self.menuBackground
        self.fullscreen = 1

        self.explosionSounds = {
            1: loadAsset('explosion1', 'sound'),
            2: loadAsset('explosion2', 'sound'),
            }

        self.laserSounds = {
            1: loadAsset('laser1', 'sound'),
            2: loadAsset('laser2', 'sound'),
            3: loadAsset('laser3', 'sound'),
            4: loadAsset('laser4', 'sound'),
            }

        self.menuMusic = 'menu'
        self.gameMusic = 'game'

        self.timeMessage = TimeMessage(self)
        self.ammoMessage = AmmoMessage(self)
        self.fuelMessage = FuelMessage(self)
        self.message = Message(self)
        self.fuelBar = FuelBar(self)
        self.ammoBar = AmmoBar(self)
        self.stats = Stats(self)

        self.music = 1
        self.soundEffects = 1
        self.playingMenuMusic = 0
        self.playingGameMusic = 0
        self.play = 0
        self.unlimitedFuel = 0
        self.unlimitedAmmo = 0
        self.win = 0
        self.lose = 0

        self.asteroidCount = NUMBER_OF_ASTEROIDS
        self.dropFrequency = DROP_FREQUENCY
        self.asteroids = []
        self.bullets = []
        self.spaceship = None
        self.drops = []
        self.popUps = []
        self.gameObjects = []
        self.messageObjects = []

        self.speed = 0
        self.angularVelocity = 0
        self.shotsFired = 0
        self.ammo = 0
        self.fuel = 0
        self.deaths = 0
        self.wins = 0

        self.splash = None

        self.pauseMenu = None
        self.mainMenu = None
        self.activeMenu = None
        self.title = None
        self.titleImage = None
        self.controls = None
        self.credits = None
        self.menuObjects = []

        self.bottomMenu = BottomMenu(self)

    def showSplash(self):

        self.splash = Splash()

        while self.splash:
            self.screen.blit(self.background, BACKGROUND_POSITION)

            if self.splash.counter:
                self.splash.update()
                self.splash.draw(self.screen)
            else:
                self.splash = None
                pygame.event.clear()
                self.refreshMenu()

            self.flipNTick()

    def showMainMenu(self):

        self.refreshMenu()

        while not self.play:
            self.screen.blit(self.background, BACKGROUND_POSITION)

            self.handleInput()

            for menuObject in self.menuObjects:
                menuObject.update()

            for menuObject in self.menuObjects:
                menuObject.draw(self.screen)

            self.flipNTick()

    def showPauseMenu(self):

        self.pauseMenu = PauseMenu(self)
        self.activeMenu = self.pauseMenu

        while self.pauseMenu:
            self.screen.blit(self.background, BACKGROUND_POSITION)
            self.pauseMenu.update()
            self.pauseMenu.draw(self.screen)
            self.flipNTick()
            self.handleInput()

    def playGame(self):

        self.play = 1

        self.clearGame()

        self.mainMenu = None
        self.pauseMenu = None
        self.title = None
        self.titleImage = None
        self.controls = None
        self.credits = None
        self.menuObjects = []

        self.shotsFired = 0
        self.ammo = STARTING_AMMO
        self.fuel = STARTING_FUEL

        self.startTime = time.time()

        self.background = getRandomFromDict(self.backgroundImages)

        if not self.playingGameMusic:
            playMusic(self.gameMusic)
            self.playingGameMusic = 1
            self.playingMenuMusic = 0

        self.spaceship = Spaceship(CENTER, self)

        for _ in range(self.asteroidCount):
            while 1:
                position = getRandomPosition(self.screen)
                if position.distance_to(self.spaceship.position) > 300:
                    break
            self.asteroids.append(Asteroid(position))

    def createDrop(self):
        if self.spaceship:
            while 1:
                position = getRandomPosition(self.screen)
                if (position.distance_to(self.spaceship.position) > 300):
                    break
            try:
                self.drops.append(Drop(position))
            except ValueError:
                pass

    def refreshMenu(self):

        self.background = self.menuBackground

        if self.playingMenuMusic == 0:
            playMusic(self.menuMusic)
            self.playingMenuMusic = 1
            self.playingGameMusic = 0

        self.clearGame()

        self.mainMenu = MainMenu(self)
        self.activeMenu = self.mainMenu
        self.title = Title()
        self.titleImage = TitleImage()
        self.controls = Controls()
        self.credits = Credits()

        self.menuObjects = [self.mainMenu, self.title, self.titleImage, self.controls, self.credits]

    def clearGame(self):
        self.asteroids = []
        self.bullets = []
        self.spaceship = None
        self.drops = []
        self.popUps = []
        self.gameObjects = []
        self.messageObjects = []
        self.message.text = ''
        self.timeMessage.hide()
        self.fuelMessage.hide()
        self.ammoMessage.hide()
        self.win = 0
        self.lose = 0

    def toggleSoundEffects(self):
        if self.soundEffects:
            pygame.mixer.pause()
            self.soundEffects = 0
        else:
            self.soundEffects = 1

    def toggleMusic(self):
        if self.music:
            pygame.mixer.music.pause()
            self.music = 0
        else:
            pygame.mixer.music.unpause()
            self.music = 1

    def toggleFullscreen(self):
        pygame.display.toggle_fullscreen()
        if not self.fullscreen:
            self.fullscreen = 1
        else:
            self.fullscreen = 0

    def mainLoop(self):
        while 1:

            if not self.play: self.showMainMenu()

            self.gameObjects = self.getGameObjects()
            self.messageObjects = self.getMessageObjects()

            self.handleInput()
            self.update()
            self.draw()

            self.flipNTick()

    def incrementDropFrequency(self):
        self.dropFrequency += 1
        if self.dropFrequency == 13: self.dropFrequency = 0

    def getDropFrequency(self):
        return self.dropFrequency

    def incrementAsteroidCount(self):
        self.asteroidCount += 1
        if self.asteroidCount == 10: self.asteroidCount = 1

    def getAttribute(self, attribute):
        if hasattr(self, attribute): return getattr(self, attribute)
        else: return ''

    def toggleUnlimitedFuel(self):
        if self.unlimitedFuel == 0:
            self.unlimitedFuel = 1
        else:
            self.unlimitedFuel = 0

    def toggleUnlimitedAmmo(self):
        if self.unlimitedAmmo == 0:
            self.unlimitedAmmo = 1
        else:
            self.unlimitedAmmo = 0

    def handleInput(self):

        updateJoystick()

        actionPressedStack = []
        actionDownStack = []

        keyboardPresses = pygame.key.get_pressed()
        for action, binding in KEY_MAP.items():
            for binding in binding:
                if keyboardPresses[binding]:
                    actionPressedStack.append(action)

        if self.joystick:
            joystickPresses = [i for i in range(self.joystick.get_numbuttons()) if self.joystick.get_button(i)]
            joystickPresses.extend([self.joystick.get_hat(i) for i in range(self.joystick.get_numhats())])

            for action, binding in JOYSTICK_MAP[self.joystickID].items():
                for binding in binding:
                    if binding in joystickPresses:
                        actionPressedStack.append(action)

        for event in pygame.event.get():

            if event.type == pygame.QUIT: raise SystemExit

            if event.type == pygame.KEYDOWN:
                for action, binding in KEY_MAP.items():
                    for binding in binding:
                        if binding == event.key:
                            actionDownStack.append(action)

            if event.type == pygame.JOYHATMOTION:
                for action, binding in JOYSTICK_MAP[self.joystickID].items():
                    if event.value in binding:
                        actionDownStack.append(action)

            if event.type == pygame.JOYBUTTONDOWN:
                for action, binding in JOYSTICK_MAP[self.joystickID].items():
                    if event.button in binding:
                        actionDownStack.append(action)

        if self.play and not self.pauseMenu:

            if self.spaceship:

                if  ('accelerate' in actionPressedStack or
                    'accelerate_left' in actionPressedStack or
                    'accelerate_right' in actionPressedStack):
                    self.spaceship.accelerateOn()
                else: self.spaceship.accelerateOff()

                if  (('left' in actionPressedStack or
                    'accelerate_left' in actionPressedStack) and
                    'right' not in actionPressedStack):
                    self.spaceship.rotateOn(False)
                elif (('right' in actionPressedStack or
                    'accelerate_right' in actionPressedStack) and
                    'left' not in actionPressedStack):
                    self.spaceship.rotateOn()
                else: self.spaceship.rotateOff()

                if 'shoot' in actionDownStack: self.spaceship.shoot()

            if 'pause' in actionDownStack: self.showPauseMenu()

        if self.pauseMenu or not self.play:

            if 'up' in actionDownStack: self.activeMenu.decrementFocusIndex()
            if 'down' in actionDownStack: self.activeMenu.incrementFocusIndex()
            if 'select' in actionDownStack: self.activeMenu.select()

    def potentialDrop(self):
        if self.time > 8:
            if random.randint(1,5000) <= self.dropFrequency and len(self.drops) < 3:
                self.createDrop()

    def gameOver(self):
        self.spaceship.die()
        self.message.show()
        self.lose = 1
        self.deaths += 1

    def missionAccomplished(self):
        self.message.show()
        self.timeMessage.show()
        if not self.win:
            self.wins += 1
            self.winTime = self.time
            self.win = 1

    def update(self):

        if self.spaceship:

            self.time = round(time.time() - self.startTime, 1)

            if self.asteroids:
                self.potentialDrop()

                for bullet in self.bullets[:]:
                    for asteroid in self.asteroids[:]:
                        if asteroid.collidesWith(bullet):
                            bullet.die()
                            asteroid.die()
                            break

                for asteroid in self.asteroids[:]:
                    if asteroid.collidesWith(self.spaceship):
                        self.gameOver()
                        break

        if not self.asteroids and self.spaceship:
            self.missionAccomplished()

        if self.spaceship:
            self.speed = game.spaceship.velocity.magnitude()

            for drop in self.drops[:]:
                if drop.collidesWith(self.spaceship):
                    drop.activate()

        for gameObject in self.gameObjects:
            gameObject.update(self.screen)

        for messageObject in self.messageObjects:
            messageObject.update()

    def draw(self):
        self.screen.blit(self.background, BACKGROUND_POSITION)

        for gameObject in self.gameObjects:
            gameObject.draw(self.screen)

        for messageObject in self.messageObjects:
            messageObject.draw(self.screen)

    def getGameObjects(self):

        gameObjects = [*self.asteroids, *self.bullets, *self.drops]

        if self.spaceship: gameObjects.append(self.spaceship)
        if self.fuelBar: gameObjects.append(self.fuelBar)
        if self.ammoBar: gameObjects.append(self.ammoBar)

        return gameObjects

    def getMessageObjects(self):

        messageObjects = [*self.popUps]

        if self.bottomMenu: messageObjects.append(self.bottomMenu)
        if self.stats: messageObjects.append(self.stats)
        if self.message: messageObjects.append(self.message)
        if self.fuelMessage: messageObjects.append(self.fuelMessage)
        if self.ammoMessage: messageObjects.append(self.ammoMessage)
        if self.timeMessage: messageObjects.append(self.timeMessage)

        return messageObjects

    def flipNTick(self):
        pygame.display.flip()
        self.clock.tick(FRAME_RATE)

class Splash:

    def __init__(self):
        self.sprite = pygame.transform.rotozoom(loadAsset('splash', 'image'), 0, 0.8)
        self.size = self.sprite.get_size()
        self.position = (CENTER[0] - self.size[0]/2, CENTER[1]-self.size[1]/2)
        self.alpha = 0
        self.fade = 0
        self.counter = 60 * SPLASH_TIME

    def draw(self, surface):
        surface.blit(self.sprite, self.position)

    def update(self):
        self.sprite.set_alpha(self.alpha)

        if self.alpha >= 255: self.fade = 1

        if self.fade: self.alpha -= 1.5
        else: self.alpha += 2

        self.counter -= 1

class Menu:

    def __init__(self):
        self.items = []
        self.focusItem = None
        self.focusIndex = 0
        self.font = pygame.font.Font(getPath('font', 'UbuntuMono-Regular', '.ttf'), 28)
        self.focusFont = pygame.font.Font(getPath('font', 'UbuntuMono-Regular', '.ttf'), 35)

    def update(self):
        self.focusItem = self.items[self.focusIndex]

    def incrementFocusIndex(self):
        self.focusIndex += 1
        if self.focusIndex > len(self.items)-1:
            self.focusIndex = 0

    def decrementFocusIndex(self):
        self.focusIndex -= 1
        if self.focusIndex < 0:
            self.focusIndex = len(self.items)-1

    def select(self):
        self.focusItem.activate()

    def addItem(self, name, action, value=None, kind=None):
        self.items.append(MenuItem(name, action, value, kind))

    def draw(self, surface):
        i = 0
        for item in self.items:
            if i == self.focusIndex:
                printText(surface, item.getName(), self.focusFont, (self.position[0],self.position[1]+35*i), color=pygame.Color(255,195,65))
            else:
                printText(surface, item.getName(), self.font, (self.position[0],self.position[1]+35*i))
            i+=1

class MainMenu(Menu):

    def __init__(self, game):
        super().__init__()
        self.position = (690,250)
        self.addItem('New Game', self.newGame)
        self.addItem('Asteroid Count', self.incrementAsteroidCount, 'asteroidCount')
        self.addItem('Supply Drop Frequency', self.incrementDropFrequency, 'dropFrequency')
        self.addItem('Unlimited Fuel', self.toggleUnlimitedFuel, 'unlimitedFuel', 'toggle')
        self.addItem('Unlimited Ammo', self.toggleUnlimitedAmmo, 'unlimitedAmmo', 'toggle')
        self.addItem('Fullscreen', self.toggleFullscreen, 'fullscreen', 'toggle')
        self.addItem('Sound Effects', self.toggleSoundEffects, 'soundEffects', 'toggle')
        self.addItem('Music', self.toggleMusic, 'music', 'toggle')
        self.addItem('Show Splash Screen', self.showSplashScreen)
        self.addItem('Quit', self.quit)
        if self.items: self.focusItem = self.items[0]

    def newGame(self):
        game.playGame()

    def incrementAsteroidCount(self):
        game.incrementAsteroidCount()

    def incrementDropFrequency(self):
        game.incrementDropFrequency()

    def toggleUnlimitedFuel(self):
        game.toggleUnlimitedFuel()

    def toggleUnlimitedAmmo(self):
        game.toggleUnlimitedAmmo()

    def toggleFullscreen(self):
        game.toggleFullscreen()

    def toggleSoundEffects(self):
        game.toggleSoundEffects()

    def toggleMusic(self):
        game.toggleMusic()

    def showSplashScreen(self):
        game.showSplash()

    def quit(self):
        raise SystemExit

class PauseMenu(Menu):

    def __init__(self, game):
        super().__init__()
        self.position = CENTER
        self.addItem('Resume', self.resume)
        self.addItem('Restart Game', self.restart)
        self.addItem('Sound Effects', self.toggleSoundEffects, 'soundEffects', 'toggle')
        self.addItem('Music', self.toggleMusic, 'music', 'toggle')
        self.addItem('Fullscreen', self.toggleFullscreen, 'fullscreen', 'toggle')
        self.addItem('Back to Main Menu', self.backToMainMenu)
        self.addItem('Quit Game', self.quitGame)
        if self.items: self.focusItem = self.items[0]

    def resume(self):
        game.pauseMenu = None

    def restart(self):
        game.playGame()

    def toggleSoundEffects(self):
        game.toggleSoundEffects()

    def toggleMusic(self):
        game.toggleMusic()

    def toggleFullscreen(self):
        game.toggleFullscreen()

    def backToMainMenu(self):
        game.pauseMenu = None
        game.play = 0

    def quitGame(self):
        raise SystemExit

class MenuItem:

    def __init__(self, name, action, value=None, kind=None):
        self.name = name
        self.action = action
        self.value = value
        self.kind = kind

    def getName(self):

        if self.value:
            value = ''
            if self.kind == 'toggle':
                if game.getAttribute(self.value):
                    value = 'X'
                else:
                    value = ' '
            else:
                value = game.getAttribute(self.value)
            return f'{self.name} [{value}]'
        else: return self.name

    def activate(self):
        self.action()

class Title:

    def __init__(self):
        self.position = (40,90)
        self.sprite = loadAsset('title', 'image')

    def update(self):
        pass

    def draw(self, surface):
        surface.blit(self.sprite, self.position)

class TitleImage:

    def __init__(self):
        self.angularVelocity = random.uniform(-1.2,1.2)
        self.direction = pygame.math.Vector2(UP).rotate(random.randrange(0,360))
        self.position = (250,430)
        self.sprite = pygame.transform.rotozoom(loadAsset('spaceship_big', 'image'), 0, 0.7)

    def update(self):
        self.direction.rotate_ip(self.angularVelocity)

    def draw(self, surface):
        angle = self.direction.angle_to(UP)
        rotatedSurface = pygame.transform.rotozoom(self.sprite, angle, 1)
        rotatedSurfaceSize = pygame.math.Vector2(rotatedSurface.get_size())
        blitPosition = self.position - rotatedSurfaceSize * 0.5
        surface.blit(rotatedSurface, blitPosition)

class Controls:

    def __init__(self):
        self.position = (970, 120)
        self.sprite = loadAsset('controls', 'image')

    def update(self):
        pass

    def draw(self, surface):
        surface.blit(self.sprite, self.position)

class GameObject:

    def __init__(self, position, sprite, velocity):
        self.position = pygame.math.Vector2(position)
        self.sprite = sprite
        self.radius = sprite.get_width() / 2
        self.velocity = pygame.math.Vector2(velocity)

    def draw(self, surface):
        blit_position = self.position - pygame.math.Vector2(self.radius)
        surface.blit(self.sprite, blit_position)

    def update(self, surface):
        self.position = wrapPosition(self.position + self.velocity, surface)
        self.direction.rotate_ip(self.angularVelocity)

    def collidesWith(self, target):
        return self.position.distance_to(target.position) < self.radius + target.radius

class Spaceship(GameObject):

    def __init__(self, position, game):

        self.direction = pygame.math.Vector2(UP)
        self.angularVelocity = 0
        self.rotating = 0
        self.accelerating = 0
        self.sprites = {
            'normal':loadAsset('spaceship', 'image'),
            'flames':loadAsset('spaceship_flames', 'image'),
            'left':loadAsset('spaceship_left', 'image'),
            'right':loadAsset('spaceship_right', 'image'),
            'flames_left':loadAsset('spaceship_flames_left', 'image'),
            'flames_right':loadAsset('spaceship_flames_right', 'image'),
            }
        super().__init__(position, self.sprites['normal'], pygame.math.Vector2(0))

    def rotateOn(self, clockwise=True):
        if game.fuel > 0:
            if clockwise == True: self.rotating = 1
            if clockwise == False: self.rotating = -1

    def rotateOff(self):
        self.rotating = 0

    def rotate(self, clockwise=True):
        sign = 1 if clockwise else -1
        angle = MANEUVERABILITY * sign
        self.direction.rotate_ip(angle)
        if not game.unlimitedFuel: game.fuel -= FUEL_BURN/2
        game.angularVelocity = MANEUVERABILITY * 60 * sign

    def update(self, surface):

        if self.rotating == 1: self.rotate()
        if self.rotating == -1: self.rotate(clockwise=False)
        if self.rotating == 0: game.angularVelocity = 0

        if self.accelerating: self.accelerate()

        if game.fuel <= 0:
            game.fuel = 0
            self.rotateOff()
            self.accelerateOff()

        self.updateSprite()
        self.position = wrapPosition(self.position + self.velocity, surface)

    def updateSprite(self):
        if self.accelerating:
            if self.rotating == 1: self.sprite = self.sprites['flames_right']
            if self.rotating == -1: self.sprite = self.sprites['flames_left']
            if self.rotating == 0: self.sprite = self.sprites['flames']
        else:
            if self.rotating == 1: self.sprite = self.sprites['right']
            if self.rotating == -1: self.sprite = self.sprites['left']
            if self.rotating == 0: self.sprite = self.sprites['normal']

    def draw(self, surface):
        angle = self.direction.angle_to(UP)
        rotatedSurface = pygame.transform.rotozoom(self.sprite, angle, 1.0)
        rotatedSurfaceSize = pygame.math.Vector2(rotatedSurface.get_size())
        blitPosition = self.position - rotatedSurfaceSize * 0.5
        surface.blit(rotatedSurface, blitPosition)

    def accelerateOn(self):
        if game.fuel > 0:
            self.accelerating = 1

    def accelerateOff(self):
        self.accelerating = 0

    def accelerate(self):
        self.velocity += self.direction * SHIP_ACCELERATION
        if not game.unlimitedFuel: game.fuel -= FUEL_BURN

    def accelerateAngular(self, clockwise=True):
        sign = 1 if clockwise else -1
        self.angularVelocity += MANEUVERABILITY * sign
        if not game.unlimitedFuel: game.fuel -= FUEL_BURN/2

    def shoot(self):

        if game.ammo > 0 or game.unlimitedAmmo:
            bulletVelocity = self.direction * BULLET_SPEED + self.velocity
            game.bullets.append(Bullet(self.position, bulletVelocity, game))
            self.velocity[0] += self.direction[0] * -1 * BULLET_MOMENTUM
            self.velocity[1] += self.direction[1] * -1 * BULLET_MOMENTUM
            game.shotsFired += 1
            if not game.unlimitedAmmo: game.ammo -= 1
            playSound(game.laserSounds[2])

        else:
            playSound(game.laserSounds[1])

    def die(self):
        playSound(game.explosionSounds[1])
        game.spaceship = None
        game.speed = 0
        game.angularVelocity = 0
        if game.joystick:
            game.joystick.rumble(0.3, 0.1, 500)

class Asteroid(GameObject):

    def __init__(self, position, size = 3):
        self.size = size
        self.angularVelocity = random.randrange(1,5)
        self.direction = pygame.math.Vector2(UP)

        scale = {
            3: 1,
            2: 0.5,
            1: 0.25,
        }

        sprite = pygame.transform.rotozoom(loadAsset('asteroid', 'image'), 0, scale[size])

        super().__init__(position, sprite, getRandomVelocity(MIN_ASTEROID_SPEED, MAX_ASTEROID_SPEED))

    def die(self):
        playSound(game.explosionSounds[2])
        if game.joystick:
            game.joystick.rumble(0.1, 0.1, 60)

        if self.size > 1:
            for _ in range(2):
                asteroid = Asteroid(self.position, self.size - 1)
                game.asteroids.append(asteroid)

        game.asteroids.remove(self)

    def draw(self, surface):
        angle = self.direction.angle_to(UP)
        rotatedSurface = pygame.transform.rotozoom(self.sprite, angle, 1.0)
        rotatedSurfaceSize = pygame.math.Vector2(rotatedSurface.get_size())
        blitPosition = self.position - rotatedSurfaceSize * 0.5
        surface.blit(rotatedSurface, blitPosition)

class Drop(GameObject):

    def __init__(self, position):
        self.angularVelocity = random.randrange(1,3)
        self.direction = pygame.math.Vector2(UP)
        self.label = ['ammo','fuel'][random.randint(0,1)]
        self.sprite = pygame.transform.rotozoom(loadAsset('ammo_drop' if self.label == 'ammo' else 'fuel_drop', 'image'), 0, 0.7)
        if game.unlimitedFuel and self.label == 'fuel': raise ValueError
        if game.unlimitedFuel and self.label == 'ammo': raise ValueError
        super().__init__(position, self.sprite, getRandomVelocity(0.5,2.5))

    def activate(self):

        game.popUpPosition = self.position

        if game.joystick:
            game.joystick.rumble(0.1,0.1,60)

        if self.label == 'ammo':
            playSound(game.laserSounds[3])
            game.ammo += AMMO_DROP_SIZE
            if game.ammo >= MAX_AMMO: game.ammo = MAX_AMMO
        else:
            playSound(game.laserSounds[4])
            game.fuel += FUEL_DROP_SIZE
            if game.fuel >= MAX_FUEL: game.fuel = MAX_FUEL

        game.popUps.append(PopUp(self.label, self.position))
        game.drops.remove(self)

    def draw(self, surface):
        angle = self.direction.angle_to(UP)
        rotatedSurface = pygame.transform.rotozoom(self.sprite, angle, 1.0)
        rotatedSurfaceSize = pygame.math.Vector2(rotatedSurface.get_size())
        blitPosition = self.position - rotatedSurfaceSize * 0.5
        surface.blit(rotatedSurface, blitPosition)

class Bullet(GameObject):

    def __init__(self, position, velocity, game):
        super().__init__(position, pygame.transform.rotozoom(loadAsset('bullet', 'image'), 0, 0.6), velocity)

    def update(self, surface):
        self.position = self.position + self.velocity
        if not game.screen.get_rect().collidepoint(self.position):
            if self in game.bullets: game.bullets.remove(self)

    def die(self):
        game.bullets.remove(self)

class FuelBar:

    def __init__(self, game):
        self.position = (10, 460)

        self.spriteFrame = loadAsset('fuel_bar_frame', 'image')
        self.spriteFill = loadAsset('fuel_bar_fill', 'image')

        w, h = self.spriteFrame.get_size()
        horOffset = w + 18

        self.maxText = '800'
        self.maxTextPosition = (self.position[0] + horOffset, self.position[1])
        self.midText = '400'
        self.midTextPosition = (self.position[0] + horOffset, self.position[1] + h/2)

        self.font = pygame.font.Font(getPath('font', 'UbuntuMono-Regular', '.ttf'), 16)

    def update(self, surface):
        pass

    def draw(self, surface):

        printText(surface, self.maxText, self.font, self.maxTextPosition)
        printText(surface, self.midText, self.font, self.midTextPosition)

        surface.blit(self.spriteFrame, self.position)

        if game.unlimitedFuel: game.fuel = MAX_FUEL
        limit = round((game.fuel/MAX_FUEL)*200)

        for i in range(limit):
            surface.blit(self.spriteFill, (self.position[0] + 3, self.position[1] + 202 - 1*i))

class AmmoBar:

    def __init__(self, game):
        self.position = (10, 675)
        self.frame = loadAsset('ammo_bar_frame', 'image')
        self.bullet = loadAsset('ammo_bar_bullet', 'image')
        self.maxText = '50'
        self.midText = '25'
        self.font = pygame.font.Font(getPath('font', 'UbuntuMono-Regular', '.ttf'), 16)
        self.maxTextPosition = (self.position[0] + 380, self.position[1] - 11)
        self.midTextPosition = (self.position[0] + 190, self.position[1] - 11)

    def update(self, surface):
        pass

    def draw(self, surface):
        surface.blit(self.frame, self.position)
        printText(surface, self.maxText, self.font, self.maxTextPosition)
        printText(surface, self.midText, self.font, self.midTextPosition)

        x, y = self.position[0] + 4, self.position[1] + 4

        limit = (50 if game.unlimitedAmmo else game.ammo)

        for i in range(0, min(limit, 50)):
            surface.blit(self.bullet, (x, y))
            if i % 2 == 1:
                surface.blit(self.bullet, (x, y + 15))
                x += 15

class PopUp:

    def __init__(self, label, position):
        self.position = position
        self.font = pygame.font.Font(None, 18)
        if label == 'ammo':
            self.text = '+' + str(AMMO_DROP_SIZE) + ' Ammo!'
        else:
            self.text = '+' + str(FUEL_DROP_SIZE) + 'L Fuel!'

        self.counter = 60 * POPUP_TIME

    def update(self):
        self.counter -= 1
        if self.counter <= 0: game.popUps.remove(self)

    def draw(self, surface):
        printText(surface, self.text, self.font, self.position)

class BottomMenu:

    def __init__(self, game):
        self.position = (1190,705)
        self.font = pygame.font.Font(getPath('font', 'UbuntuMono-Regular', '.ttf'), 15)
        self.text = '[Escape/Start] Pause'

    def update(self):
        pass

    def draw(self, surface):
        printText(surface, self.text, self.font, self.position)

class Stats:

    def __init__(self, game):
        self.position = (640,15)
        self.font = pygame.font.Font(getPath('font', 'UbuntuMono-Regular', '.ttf'), 18)
        self.stats = ''

    def update(self):
        self.stats = ('Speed: ' + constDigits(game.speed*10, 3) + 'm/s' +
                '    Angular Speed: ' + constDigits(game.angularVelocity, 4) + '°/s' +
                '    Shots Fired: ' + constDigits(game.shotsFired, 3) +
                '    Ammo: ' + (constDigits(game.ammo, 3) if not game.unlimitedAmmo else '∞') +
                '    Fuel: ' + (constDigits(game.fuel, 3) + 'L' if not game.unlimitedFuel else '∞') +
                '    Deaths: ' + constDigits(game.deaths, 2) +
                '    Wins: ' + constDigits(game.wins, 2) +
                '    Time: ' + constDigits(game.time, 3) + 's')

    def draw(self, surface):
        printText(surface, self.stats, self.font, self.position)

class Message:

    def __init__(self, game):
        self.position = CENTER
        self.font1 = pygame.font.Font(None, 100)
        self.font2 = pygame.font.Font(getPath('font', 'UbuntuMono-Bold', '.ttf'), 18)
        self.visible = 0
        self.text = ''

    def hide(self):
        self.visible = 0

    def show(self):
        self.visible = 1

    def update(self):
        if game.win: self.text = 'Mission Accomplished'
        elif game.lose: self.text = 'Mission Failed'
        else: self.text = ''

    def draw(self, surface):
        if self.visible: printText(surface, self.text, self.font1, self.position)

class TimeMessage:

    def __init__(self, game):
        self.font = pygame.font.Font(None, 30)
        self.text = ''
        self.position = (640,420)
        self.visible = 0

    def show(self):
        self.visible = 1

    def hide(self):
        self.visible = 0

    def update(self):
        self.text = 'Time: ' + str(round(game.winTime,1)) + ' seconds'

    def draw(self, surface):
        if self.visible: printText(surface, self.text, self.font, self.position)

class AmmoMessage:

    def __init__(self, game):

        self.font = pygame.font.Font(getPath('font', 'UbuntuMono-Bold', '.ttf'), 18)
        self.position = (640,600)
        self.text = 'Out of Ammo!'
        self.visible = 0

    def hide(self):
        self.visible = 0

    def show(self):
        self.visible = 1

    def update(self):
        if game.play == 0 and self.visible: self.hide()

        if game.play:
            if game.ammo <= 0 and not self.visible: self.show()
            if game.ammo > 0 and self.visible: self.hide()

    def draw(self, surface):
        if self.visible: printText(surface, self.text, self.font, self.position)

class FuelMessage:

    def __init__(self, game):

        self.font = pygame.font.Font(getPath('font', 'UbuntuMono-Bold', '.ttf'), 18)
        self.position = (640,640)
        self.text = 'Out of Fuel!'
        self.visible = 0

    def hide(self):
        self.visible = 0

    def show(self):
        self.visible = 1

    def update(self):
        if game.play == 0 and self.visible: self.hide()

        if game.play:
            if game.fuel <= 0 and not self.visible: self.show()
            if game.fuel > 0 and self.visible: self.hide()

    def draw(self, surface):
        if self.visible: printText(surface, self.text, self.font, self.position)

class Credits:

    def __init__(self):
        self.position = (1095, 510)
        self.font = pygame.font.Font(getPath('font', 'UbuntuMono-Regular', '.ttf'), 18)
        self.text = ['Fractal Fungus Games', 'FractalFungusGames@proton.me', version, '', 'Programming and Art by Matt', 'Music by Jay']

    def update(self):
        pass

    def draw(self, surface):
        i = 0
        for item in self.text:
            printText(surface, item, self.font, (self.position[0],self.position[1]+18*i))
            i+=1

# utility functions
def updateJoystick():

    if pygame.joystick.get_count() > 0:
        if not game.joystick:
            game.joystick = pygame.joystick.Joystick(0)
            game.joystickName = game.joystick.get_name()

            print('Joystick detected: ', game.joystickName)

            if 'PS4' in game.joystickName:
                game.joystickID = 'PS4'

            if 'Sony Interactive Entertainment Wireless Controller' in game.joystickName:
                game.joystickID = 'PS5'

            if 'Switch Pro' in game.joystickName:
                game.joystickID = 'Switch'

            else:
                game.joystickID = 'Xbox'

    else:
        game.joystick = None

def constDigits(number, digits):

    number = round(number)

    length = len(str(number))

    if digits > length:
        number_of_spaces = digits - length
        if number_of_spaces == 3: return '   ' + str(number)
        if number_of_spaces == 2: return '  ' + str(number)
        if number_of_spaces == 1: return ' ' + str(number)
    else: return str(number)

def getPath(kind, name, extension):

    if not hasattr(getPath, 'assetsPath'):

        if hasattr(sys, '_MEIPASS'):
            basePath = sys._MEIPASS
            getPath.assetsPath = os.path.abspath(os.path.join(basePath, 'assets'))

        else:
            basePath = os.path.dirname(os.path.abspath(__file__))
            getPath.assetsPath = os.path.abspath(os.path.join(basePath, '..', 'assets'))

    return os.path.join(getPath.assetsPath, kind, name + extension)

def loadAsset(name, kind, withAlpha=True):

    path = getPath(kind, name, ('.png' if kind == 'image' else ('.wav' if kind == 'sound' else '.ogg')))

    if kind == 'image':
        sprite = pygame.image.load(path)
        if withAlpha: return sprite.convert_alpha()
        else: return sprite.convert()
    elif kind == 'sound':
        return pygame.mixer.Sound(path)
    elif kind == 'music':
        pygame.mixer.music.load(path)
        return

def playSound(name):
    if game.soundEffects:
        pygame.mixer.Sound.play(name)

def playMusic(name):
    loadAsset(name, 'music')
    pygame.mixer.music.play(loops=-1)
    if not game.music:
        pygame.mixer.music.pause()

def wrapPosition(position, surface):
    x, y = position
    w, h = surface.get_size()
    return pygame.math.Vector2(x % w, y % h)

def getRandomFromDict(dictionary):
    key = random.choice(list(dictionary.keys()))
    return dictionary[key]

def getRandomFromList(array):
    return random.choice(array)

def getRandomPosition(surface):
    return pygame.math.Vector2(random.randrange(surface.get_width()), random.randrange(surface.get_height()))

def getRandomVelocity(min_speed, max_speed):
    speed = random.uniform(min_speed, max_speed)
    angle = random.randrange(0, 360)
    return pygame.math.Vector2(speed, 0).rotate(angle)

def printText(surface, text, font, position, color=pygame.Color(FONT_COLOR)):
    text_surface = font.render(text, True, color)

    rect = text_surface.get_rect()
    rect.center = (pygame.math.Vector2(position))

    surface.blit(text_surface, rect)

if __name__ == '__main__':
    try:
        game = AbominableAsteroids()
        game.showSplash()
        game.mainLoop()
    except KeyboardInterrupt:
        pass
