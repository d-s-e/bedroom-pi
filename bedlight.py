import time
from enum import Enum, auto

from rpi_ws281x import Color, PixelStrip, ws

# LED strip low level configuration:
LED_COUNT = 120        # Number of LED pixels.
LED_PIN = 10           # LED GPIO pin (use 10 for SPI or 18 for PWM).
LED_FREQ_HZ = 800000   # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10           # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255   # Set to 0 for darkest and 255 for brightest
LED_INVERT = False     # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0
LED_STRIP = ws.SK6812_STRIP_GRBW

# LED
SECTION_SIZE = 15
COLOR_MAIN = Color(255, 86, 0, 0)
COLOR_SECTION = Color(0, 0, 0, 255)


class BedLight:
    def __init__(self, led_count, section_size):
        self.led_buffer = []
        self.led_count = led_count
        self.section_size = section_size
        self.section_left = False
        self.section_right = False
        self.section_main = False
        self.color_main = COLOR_MAIN
        self.color_section = COLOR_SECTION
        self.color_off = Color(0, 0, 0, 0)
        self.reset_lights()

    def _set_lights(self):
        if self.section_main:
            self.led_buffer = [self.color_main] * self.led_count 
        else:
            self.led_buffer = [self.color_off] * self.led_count

        if self.section_left:
            for i in range(self.section_size):
                self.led_buffer[i] = self.color_section

        if self.section_right:
            for i in range(self.section_size):
                self.led_buffer[self.led_count -1 - i] = self.color_section

        for i in range(strip.numPixels()):
            strip.setPixelColor(i, self.led_buffer[i])
        strip.show()

    def reset_lights(self):
        self.led_buffer = [self.color_off] * self.led_count
        self.section_left = False
        self.section_right = False
        self.section_main = False
        self._set_lights()

    def toggle_section_left(self):
        self.section_left = not self.section_left
        self._set_lights()

    def toggle_section_main(self):
        self.section_main = not self.section_main
        self._set_lights()

    def toggle_section_right(self):
        self.section_right = not self.section_right
        self._set_lights()


if __name__ == '__main__':
    strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
    strip.begin()

    bar = BedLight(LED_COUNT, SECTION_SIZE)

    while True:
        bar.toggle_section_main()

        input()
        bar.toggle_section_left()

        input()
        bar.toggle_section_right()

        input()
        bar.toggle_section_main()
        
        input()
        bar.toggle_section_main()
        
        input()
        bar.toggle_section_left()

        input()
        bar.toggle_section_right()

        input()
        bar.toggle_section_main()
        
        input()

