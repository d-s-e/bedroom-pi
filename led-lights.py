from time import sleep
from rpi_ws281x import Color, PixelStrip, ws

# LED strip low level configuration:
LED_PIN = 10           # LED GPIO pin (use 10 for SPI or 18 for PWM).
LED_FREQ_HZ = 800000   # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10           # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255   # Set to 0 for darkest and 255 for brightest
LED_INVERT = False     # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0
LED_STRIP = ws.SK6812_STRIP_GRBW


class LedLights:
    def __init__(self, led_count, section_size, color_main=(255, 86, 0, 0), color_section=(0, 0, 0, 255)):
        self.strip = PixelStrip(led_count, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
        self.led_buffer = []
        self.led_count = led_count
        self.section_size = section_size
        self.section_left = False
        self.section_right = False
        self.section_main = False
        self.color_main = Color(*color_main)
        self.color_section = Color(*color_section)
        self.color_off = Color(0, 0, 0, 0)
        self.strip.begin()
        self.set_all_off()

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

        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, self.led_buffer[i])
        self.strip.show()

    def set_all_off(self):
        self.section_left = False
        self.section_right = False
        self.section_main = False
        self._set_lights()

    def toggle_left(self):
        self.section_left = not self.section_left
        self._set_lights()

    def set_left_on(self):
        self.section_left = True
        self._set_lights()

    def set_left_off(self):
        self.section_left = False
        self._set_lights()

    def toggle_right(self):
        self.section_right = not self.section_right
        self._set_lights()

    def set_right_on(self):
        self.section_right = True
        self._set_lights()

    def set_right_off(self):
        self.section_right = False
        self._set_lights()

    def toggle_main(self):
        self.section_main = not self.section_main
        self._set_lights()

    def set_main_on(self):
        self.section_main = True
        self._set_lights()

    def set_main_off(self):
        self.section_main = False
        self._set_lights()


if __name__ == '__main__':
    led = LedLights(led_count=100, section_size=12)

    while True:
        led.set_main_on()
        sleep(1)

        led.set_left_on()
        led.set_right_on()
        sleep(1)

        led.set_left_off()
        led.set_right_off()
        sleep(1)

        led.set_main_off()
        sleep(1)
        
