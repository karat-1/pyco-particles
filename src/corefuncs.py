import pygame
import math
from typing import Union

"""
A collection of global all purpose functions
"""


def load_img(path: str, colorkey=None, retain_alpha=False) -> pygame.Surface:
    if retain_alpha:
        img = pygame.image.load(path).convert_alpha()
    else:
        img = pygame.image.load(path).convert()
    if colorkey:
        img.set_colorkey(colorkey)
    return img


def sign(val: int) -> int:
    if val > 0:
        return 1
    elif val < 0:
        return -1
    else:
        return 0


def clamp(n, smallest, largest):
    """
    :param n: current number
    :param smallest: the smallest number n is allowed to be
    :param largest: the largest number n is allowed to be
    :return: if n is smaller than largest and larger than smallest then n gets returned, otherwise one of the caps
    """
    return max(smallest, min(n, largest))


def itr(l: list):
    """
    :param l: a list
    :return: a sorted enumerated list
    """
    return sorted(enumerate(l), reverse=True)


def lerp(initial_value: Union[int, float], target_value: Union[int, float], increment: Union[int, float]) -> Union[
    int, float]:
    """
    :param initial_value: the current value you want to change
    :param target_value:  the value you want to have
    :param increment: the step size you want to value to increment or decrement
    :return: an increased or decreased value
    """
    return initial_value * (1.0 - increment) + (target_value * increment)


def approach(start, end, shift):
    if start < end:
        return min(start + shift, end)
    else:
        return max(start - shift, end)


def oscillating_lerp(min_val, max_val, speed, time, smoothness=2):
    """
        Lerp function that oscillates between two values.
        :param min_val: The minimum value.
        :param max_val: The maximum value.
        :param speed: The oscillation speed (higher = faster).
        :param time: The current time (in seconds or ticks).
        :return: The interpolated value between min_val and max_val.
    """
    factor = (math.sin(time * speed) + 1) / 2
    smoothed_factor = factor ** smoothness if factor < 0.5 else 1 - ((1 - factor) ** smoothness)
    return min_val + (max_val - min_val) * smoothed_factor
