import operator

import cocos
import cocos.euclid as eu
import cocos.collision_model as cm
import cocos.director as cd
from pyglet.window import key
import random


class Actor(cocos.sprite.Sprite):
    def __init__(self, x, y, color):
        super(Actor, self).__init__('img/ball.png',
                                    color=color)
        pos = eu.Vector2(x, y)
        self.position = pos
        self.cshape = cm.CircleShape(pos, self.width / 2)

        self.speed = 200
        self.destination = pos

    def drive(self, delta_time):
        res = tuple(map(operator.sub, self.position, self.destination))
        if abs(res[0]) < 1 and abs(res[1]) < 1:
            # you have arrived!
            # pick new destination
            w, h = cd.director.get_window_size()
            new_x = random.randint(0, w)
            new_y = random.randint(0, h)
            self.destination = (new_x, new_y)
        else:
            dist_x = self.destination[0] - self.position[0]
            dist_y = self.destination[1] - self.position[1]
            self.position = (self.position[0] + dist_x * delta_time,
                             self.position[1] + dist_y * delta_time)
            self.cshape.center = eu.Vector2(self.position[0], self.position[1])
            #print(self.cshape.center)


class MainLayer(cocos.layer.Layer):
    def __init__(self):
        super(MainLayer, self).__init__()

        self.player = Actor(320, 240, (0, 0, 255))
        self.add(self.player)

        self.points = 0
        self.elapsed_game_time = 0

        self.pickups = []

        for pos in [(100, 100), (540, 380), (540, 100), (100, 300)]:
            red_ball = Actor(pos[0], pos[1], (255, 0, 0))
            self.add(red_ball)
            self.pickups.append(red_ball)

        self.schedule(self.update)

        w, h = cd.director.get_window_size()

        cell = self.player.width * 1.25
        self.collman = cm.CollisionManagerGrid(0, w, 0, h, cell, cell)


    def update(self, delta_time):
        #print(delta_time)
        if self.points < 4:
            self.elapsed_game_time += delta_time
            hud.update_time(self.elapsed_game_time)

        self.collman.clear()

        for _, actor in self.children:
            self.collman.add(actor)

        for other in self.collman.iter_colliding(self.player):
            self.remove(other)
            self.pickups.remove(other)
            self.points += 1
            hud.update_point(self.points)

        for red_ball in self.pickups:
            #print(red_ball.position)
            red_ball.drive(delta_time)

        horizontal_movement = keyboard[key.RIGHT] - keyboard[key.LEFT]
        vertical_movement = keyboard[key.UP] - keyboard[key.DOWN]

        pos = self.player.position  # (x, y)

        new_x = pos[0] + (self.player.speed * horizontal_movement * delta_time)
        new_y = pos[1] + (self.player.speed * vertical_movement * delta_time)

        w, h = cd.director.get_window_size()

        if 0 <= new_x <= w and 0 <= new_y <= h:
            self.player.position = (new_x, new_y)
            self.player.cshape.center = eu.Vector2(new_x, new_y)
            #print(self.player.cshape.center)


class HUD(cocos.layer.Layer):
    def __init__(self):
        super(HUD, self).__init__()
        w, h = cd.director.get_window_size()

        self.points_text = cocos.text.Label('Points: 0', font_size=18,
                                            anchor_x='center',
                                            anchor_y='center')
        self.points_text.position = (w / 2, h - 50)
        self.add(self.points_text)

        self.time_text = cocos.text.Label('Time: 0', font_size=18,
                                            anchor_x='center',
                                            anchor_y='center')
        self.time_text.position = (w / 2, h - 100)
        self.add(self.time_text)

    def update_point(self, points):
        self.points_text.element.text = 'Points: {}'.format(points)

    def update_time(self, time):
        self.time_text.element.text = 'Time: {:.2f}'.format(time)


if __name__ == '__main__':
    cd.director.init(caption='Cocos Demo')
    keyboard = key.KeyStateHandler()
    cd.director.window.push_handlers(keyboard)

    hud = HUD()
    layer = MainLayer()
    scene = cocos.scene.Scene()
    scene.add(hud)
    scene.add(layer)
    cd.director.run(scene)
