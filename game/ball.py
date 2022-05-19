#!/usr/bin/env python3
# Nicholas Girmes
# CPSC 386-04
# 2022-05-03
# n.girmes@csu.fullerton.edu
# @ngirmes
#
# Lab 00-05
#
# This program runs Bouncing Balls!
#

"""A Ball class for the bouncing ball demo."""

import os.path
from random import randint
from math import isclose
import pygame
from game import rgbcolors


def random_velocity(min_val=-3, max_val=3):
    """Generate a random velocity in a plane, return it as a Vector2"""
    random_x_direction = randint(min_val, max_val)
    while random_x_direction == 0:
        random_x_direction = randint(min_val, max_val)
    random_y_direction = randint(min_val, max_val)
    while random_y_direction == 0:
        random_y_direction = randint(min_val, max_val)
    return pygame.Vector2(random_x_direction, random_y_direction)


def random_color():
    """Return a random color."""
    return pygame.Color(randint(0, 255), randint(0, 255), randint(0, 255))


# This is the class we discussed in class. You can have this as a standalone
# definition of a circle's geometry or you can fold the Circle and Ball classes
# together into a single class definition. Your choice.
class Circle:
    """Class representing a circle with a bounding rect."""

    def __init__(self, center_x, center_y, radius):
        self._center = pygame.Vector2(center_x, center_y)
        self._radius = radius

    @property
    def radius(self):
        """Return the circle's radius"""
        return self._radius

    @property
    def center(self):
        """Return the circle's center."""
        return self._center

    @property
    def rect(self):
        """Return bounding Rect; calculate it and create a new Rect instance"""
        upper_left_corner = self._center - \
            pygame.Vector2(self._radius, self._radius)
        width = self._radius * 2
        return pygame.Rect(upper_left_corner, (width, width))

    @property
    def width(self):
        """Return the width of the bounding box the circle is in."""
        return self._radius * 2

    @property
    def height(self):
        """Return the height of the bounding box the circle is in."""
        return self._radius * 2

    def squared_distance_from(self, other_circle):
        """Squared distance from self to other circle."""
        return (other_circle.center - self.center).length_squared()

    def distance_from(self, other_circle):
        """Distance from self to other circle"""
        return (other_circle.center - self._center).length()

    def move_ip(self, x_point, y_point):
        """Move circle in place, update the circle's center"""
        self._center = self._center + pygame.Vector2(x_point, y_point)

    def move(self, x_point, y_point):
        """Move circle, return a new Circle instance"""
        center = self._center + pygame.Vector2(x_point, y_point)
        return Circle(center, self._radius)

    def stay_in_bounds(self, xmin, xmax, ymin, ymax):
        """Update the position of the circle so that it remains
        within the rectangle defined by xmin, xmax, ymin, ymax."""
        if self._center.x <= xmin:
            self._center.x = self._radius
        elif self._center.x >= xmax:
            self._center.x = xmax - self._radius
        elif self._center.y <= ymin:
            self._center.y = self._radius
        elif self._center.y >= ymax:
            self._center.y = ymax - self._radius


class Ball:
    """A class representing a moving ball."""

    default_radius = 25

    main_dir = os.path.split(os.path.abspath(__file__))[0]
    data_dir = os.path.join(main_dir, "data")
    # Feel free to change the sounds to something else.
    # Make sure you have permssion to use the sound effect file and document
    # where you retrieved this file, who is the author, and the terms of
    # the license.
    bounce_sound = os.path.join(data_dir, "Boing.aiff")
    reflect_sound = os.path.join(data_dir, "Monkey.aiff")

    def __init__(self, name, center_x, center_y, sound_on=True):
        """Initialize a bouncing ball."""
        # The name can be any string. The best choice is an integer.
        self._name = name
        # Yes, we could define the details about our geometry in the Ball
        # class or we can define the geometry in an instance variable.
        # It is up to you if you want to separate them out or integrate them
        # together.
        self._circle = Circle(center_x, center_y, Ball.default_radius)
        self._color = random_color()
        self._velocity = random_velocity()
        self._sound_on = sound_on
        self._bounce_count = randint(5, 10)
        self._is_alive = True
        self._draw_text = False
        font = pygame.font.SysFont(None, Ball.default_radius)
        self._name_text = font.render(str(self._name), True, rgbcolors.black)
        try:
            self._bounce_sound = pygame.mixer.Sound(Ball.bounce_sound)
            self._bounce_sound.set_volume(1)
            self._bounce_channel = pygame.mixer.Channel(2)
        except pygame.error as pygame_error:
            print(f"Cannot open {Ball.bounce_sound}")
            raise SystemExit(1) from pygame_error
        try:
            self._reflect_sound = pygame.mixer.Sound(Ball.reflect_sound)
            self._reflect_sound.set_volume(1)
            self._reflect_channel = pygame.mixer.Channel(3)
        except pygame.error as pygame_error:
            print(f"Cannot open {Ball.reflect_sound}")
            raise SystemExit(1) from pygame_error

    def toggle_draw_text(self):
        """Toggle the debugging text where each circle's name is drawn."""
        self._draw_text = not self._draw_text

    def draw(self, surface):
        """Draw the circle to the surface."""
        pygame.draw.circle(surface, self.color, self.center, self.radius)
        if self._draw_text:
            surface.blit(
                self._name_text,
                self._name_text.get_rect(center=self._circle.center),
            )

    def wall_reflect(self, xmin, xmax, ymin, ymax):
        """Reflect the ball off of a wall,
        play a sound if the sound flag is on."""
        # Condition for bottom left corner
        self._circle.stay_in_bounds(xmin, xmax, ymin, ymax)

        if (
            self._circle.center.x <= xmin + self._circle._radius
            and self._circle.center.y <= ymin + self._circle._radius
        ):
            self._velocity.x *= -1
            self._velocity.y *= -1
            if self._sound_on and self._is_alive:
                self._reflect_sound.play(0)

        # Condition for top left corner
        elif (
            self._circle.center.x <= xmin + self._circle._radius
            and self._circle.center.y + self._circle._radius >= ymax
        ):
            self._velocity.x *= -1
            self._velocity.y *= -1
            if self._sound_on and self._is_alive:
                self._reflect_sound.play(0)

        # Condition for bottom right corner
        elif (
            self._circle.center.x + self._circle._radius >= xmax
            and self._circle.center.y <= ymin + self._circle._radius
        ):
            self._velocity.x *= -1
            self._velocity.y *= -1
            if self._sound_on and self._is_alive:
                self._reflect_sound.play(0)

        # Condition for top right corner
        elif (
            self._circle.center.x + self._circle._radius >= xmax
            and self._circle.center.y + self._circle._radius >= ymax
        ):
            self._velocity.x *= -1
            self._velocity.y *= -1
            if self._sound_on and self._is_alive:
                self._reflect_sound.play(0)

        # Condition for left or right wall
        elif (
            self._circle.center.x <= xmin + self._circle._radius
            or self._circle.center.x + self._circle._radius >= xmax
        ):
            self._velocity.x *= -1
            if self._sound_on and self._is_alive:
                self._reflect_sound.play(0)

        # Condition for top or bottom wall
        elif (
            self._circle.center.y <= ymin + self._circle._radius
            or self._circle.center.y + self._circle._radius >= ymax
        ):
            self._velocity.y *= -1
            if self._sound_on and self._is_alive:
                self._reflect_sound.play(0)

    def bounce(self, other_ball):
        """Bounce the ball off of another ball,
        play a sound if the ball is no alive."""
        normal = other_ball.center - self.center
        self._velocity = self._velocity.reflect(normal)
        self._bounce_count -= 1
        other_ball._bounce_count -= 1
        if self._bounce_count == 0:
            self._is_alive = False
            self.set_velocity(0, 0)
            self._color = pygame.Color(255, 250, 250)
        if other_ball._bounce_count == 0:
            other_ball._is_alive = False
            other_ball.set_velocity(0, 0)
            other_ball._color = pygame.Color(255, 250, 250)

    def collide_with(self, other_ball):
        """Return true if self collides with other_ball."""
        return (
            self._circle.distance_from(other_ball)
            <= self._circle._radius +
            other_ball._circle._radius
        )

    def separate_from(self, other_ball, rect=0):
        """Separate a ball from the other
        ball so they are no longer overlapping."""
        distance_between = self._circle.distance_from(other_ball._circle)
        ideal_distance = (
            self._circle.radius + other_ball._circle._radius
            + (self._circle.radius / 6)
        )
        half_distance_to_change_by = (ideal_distance - distance_between) / 2

        # Move first ball
        velocity = self._velocity * -1
        scale_velocity = velocity * half_distance_to_change_by
        self._circle.move_ip(*scale_velocity)

        # Move other ball
        velocity = other_ball._velocity * -1
        scale_velocity = velocity * half_distance_to_change_by
        other_ball._circle.move_ip(*scale_velocity)

    @property
    def name(self):
        """Return the ball's name."""
        return self._name

    @property
    def rect(self):
        """Return the ball's rect."""
        return self._circle.rect

    @property
    def circle(self):
        """Return the ball's circle."""
        return self._circle

    @property
    def center(self):
        """Return the ball's center."""
        return self._circle.center

    @property
    def radius(self):
        """Return the ball's radius"""
        return self._circle.radius

    @property
    def color(self):
        """Return the color of the ball."""
        return self._color

    @property
    def velocity(self):
        return self._velocity

    @property
    def is_alive(self):
        """Return true if the ball is still alive."""
        return self._is_alive

    def toggle_sound(self):
        """Turn off the sound effects."""
        self._sound_on = not self._sound_on

    def too_close(self, x, y, min_dist):
        """Is the ball too close to some point by some min_dist?"""
        point = pygame.Vector2(x, y)
        return (point - self._circle._center).length() < min_dist

    def stop(self):
        """Stop the ball from moving."""
        self._velocity = pygame.Vector2(0, 0)

    def set_velocity(self, x, y):
        """Set the ball's velocity."""
        self._velocity = pygame.Vector2(x, y)

    def update(self):
        """Update the ball's position"""
        self._circle.move_ip(*self._velocity)

    def __str__(self):
        """Ball stringify."""
        # name, center_x, center_y, sound_on=True
        return f"Ball({self.name}, {self._circle.center})"
