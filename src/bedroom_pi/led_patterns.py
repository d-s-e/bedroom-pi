from math import ceil
from rpi_ws281x import Color


class Pattern:
    name = "unnamed pattern"
    pattern = []
    dynamic = False

    def get_frame(self, led_count):
        return self.pattern * ceil(led_count / len(self.pattern))


class SolidOrange(Pattern):
    name = "orange"
    pattern = [Color(128, 43, 0, 0)]


class SolidBlue(Pattern):
    name = "blue"
    pattern = [Color(0, 0, 255, 0)]


class SolidRedOrange(Pattern):
    name = "red/orange"
    pattern = [Color(255, 0, 0, 0), Color(255, 86, 0, 0)]


class SolidGreen(Pattern):
    name = "green"
    pattern = [Color(0, 255, 0, 0)]


class SolidRGB(Pattern):
    name = "RGB"
    pattern = [Color(255, 0, 0, 0), Color(0, 255, 0, 0), Color(0, 0, 255, 0)]


patterns = (
    SolidOrange(),
    SolidRedOrange(),
    SolidBlue(),
    SolidGreen(),
    SolidRGB(),
)
