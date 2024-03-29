from kivy.app import App
from kivymd.app import MDApp
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.properties import NumericProperty, ListProperty
from kivy.animation import Animation
from random import random
from kivymd.uix.button import MDFlatButton
from kivy.core.audio import SoundLoader

class Manager(ScreenManager):
    pass

class Menu(Screen):
    pass

class Intro(Screen):
    def on_enter(self, *args):
        Clock.schedule_once(self.switch_to_menu, 2)  # Mudar para o menu após 3 segundos

    def switch_to_menu(self, dt):
        Clock.schedule_once(3)
        App.get_running_app().root.current = 'menu'
        self.manager.remove_widget(self)

class Game(Screen):
    start_sound = SoundLoader.load("start.mp3")
    background_sound = SoundLoader.load("background.mp3")
    score_sound = SoundLoader.load("score.mp3")
    game_over_sound = SoundLoader.load("game_over.mp3")
    obstacles =  []
    score = NumericProperty(0)
    def on_enter(self, *args):
        Clock.schedule_interval(self.update, 1/30)
        Clock.schedule_interval(self.putObstacle, 1.5)
        
    def on_pre_enter(self, *args):
        self.ids.player.y = self.height/2
        self.ids.player.speed = 0
        self.score = 0    
        
        if self.start_sound:
            self.start_sound.play()
            self.background_sound.play()

    def update(self, *args):
        self.ids.player.speed += -self.height * 2 * 1/30
        self.ids.player.y += self.ids.player.speed * 1/30
        if self.ids.player.y > self.height or self.ids.player.y < 0:        
            self.background_sound.stop()
            self.game_over_sound.play()
            self.gameOver()
        elif self.playeCollided():
            self.start_sound.stop()
            self.game_over_sound.play()
            self.gameOver()
            
    def putObstacle(self, *args):
        gap = self.height * 0.3
        position = (self.height - gap) * random()
        width = self.width * 0.05
        obstacleLow = Obstacle(x = self.width, height = position, width = width)
        obstacleHigh = Obstacle(x = self.width, y = position + gap, height = self.height - position - gap, width = width)
        self.add_widget(obstacleLow, 3)
        self.add_widget(obstacleHigh, 3)
        self.obstacles.append(obstacleLow)
        self.obstacles.append(obstacleHigh)
            
    def gameOver(self, *args):
        Clock.unschedule(self.update, 1/30)  
        Clock.unschedule(self.putObstacle, 1.5)
        for ob in self.obstacles:
            ob.anim.cancel(ob)
            self.remove_widget(ob)   
        self.obstacles = []
        App.get_running_app().root.current = 'gameOver'
        
    def collided(self, wid1, wid2):
        if wid2.x <= wid1.x + wid1.width and \
            wid2.x + wid2.width >= wid1.x and \
            wid2.y <= wid1.y + wid1.height and \
            wid2.y + wid2.height >= wid1.y:
            return True
        return False
    
    def playeCollided(self):
        collided = False
        for obstacle in self.obstacles:
            if self.collided(self.ids.player, obstacle):
                collided = True
                break
        return collided
            
        
    def on_touch_down(self, *args):
        self.ids.player.speed = self.height*0.7
        
class Obstacle(Widget):
    color = ListProperty([0.3, 0.2, 0.2, 1])
    scored = False
    gameScreen = None
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.anim = Animation(x = -self.width, duration = 3)
        self.anim.bind(on_complete = self.vanish)
        self.anim.start(self)
        self.gameScreen = App.get_running_app().root.get_screen('game')
        
    def on_x(self, *args):
        if self.gameScreen:
            if self.x < self.gameScreen.ids.player.x and not self.scored:
                self.gameScreen.score += 1
                self.gameScreen.score_sound.play()                
                self.scored = True
        
    def vanish(self, *args):
        self.gameScreen.remove_widget(self)
        self.gameScreen.obstacles.remove(self)
        
class GameOver(Screen):
    pass
class Player(Image):
    speed = NumericProperty(0)

class HashBird(MDApp):
    pass
    
if __name__ == "__main__":
    HashBird().run()