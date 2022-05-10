import logging
import signal
from time import sleep
from threading import Event, Thread
from rpi_ws281x import Color, PixelStrip, ws

from led_patterns import patterns


logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


# LED strip low level configuration:
LED_PIN = 10  # LED GPIO pin (use 10 for SPI or 18 for PWM).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10  # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False  # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0
LED_STRIP = ws.SK6812_STRIP_GRBW

# LED color presets:
COLOR_SECTION = (0, 0, 0, 255)


class LedThread(Thread):
    def __init__(self, led_count, section_size):
        super().__init__()
        self._section_left = False
        self._section_right = False
        self._section_main = False
        self._current_main_pattern = 0
        self._led_buffer = []
        self._led_count = led_count
        self._section_size = section_size
        self._strip = PixelStrip(
            self._led_count,
            LED_PIN,
            LED_FREQ_HZ,
            LED_DMA,
            LED_INVERT,
            LED_BRIGHTNESS,
            LED_CHANNEL,
            LED_STRIP,
        )

        self.color_section = Color(*COLOR_SECTION)
        self._strip.begin()
        self.reset_lights()
        self.stop_flag = Event()

    def run(self):
        while not self.stop_flag.is_set():
            sleep(1)
        self.reset_lights()

    @property
    def section_left(self):
        return self._section_left

    @section_left.setter
    def section_left(self, value):
        self._section_left = value
        self._set_lights()

    @property
    def section_right(self):
        return self._section_right

    @section_right.setter
    def section_right(self, value):
        self._section_right = value
        self._set_lights()

    @property
    def section_main(self):
        return self._section_main

    @section_main.setter
    def section_main(self, value):
        self._section_main = value
        self._set_lights()

    def reset_main(self):
        self._section_main = False
        self._current_main_pattern = 0
        self._set_lights()

    def select_next_main_pattern(self):
        if self._current_main_pattern >= len(patterns) - 1:
            self._current_main_pattern = 0
        else:
            self._current_main_pattern += 1
        self._set_lights()

    def reset_lights(self):
        """Switch all lights off and reset selected patterns"""
        self._section_left = False
        self._section_right = False
        self._section_main = False
        self._current_main_pattern = 0
        self._set_lights()

    def _set_lights(self):
        log.debug(
            f'Left: {"On " if self._section_left else "Off"} | Right: {"On " if self._section_right else "Off"} | Main: {patterns[self._current_main_pattern].name if self._section_main else "Off"}'
        )

        if self._section_main:
            self._led_buffer = patterns[self._current_main_pattern].get_frame(
                self._led_count
            )
        else:
            self._led_buffer = [Color(0, 0, 0, 0)] * self._led_count

        if self._section_left:
            for i in range(self._section_size):
                self._led_buffer[i] = self.color_section

        if self._section_right:
            for i in range(self._section_size):
                self._led_buffer[self._led_count - 1 - i] = self.color_section

        for i in range(self._strip.numPixels()):
            self._strip.setPixelColor(i, self._led_buffer[i])
        self._strip.show()


class LedLights:
    """Class to handle the setup and direct control of the LED strip in a convenient way"""

    def __init__(
        self,
        led_count,
        section_size,
    ):
        signal.signal(signal.SIGINT, self.stop)
        signal.signal(signal.SIGTERM, self.stop)
        self.led_count = led_count
        self.section_size = section_size
        self.led_thread = LedThread(self.led_count, self.section_size)

    def run(self):
        self.led_thread.start()

    def stop(self, *args):
        self.led_thread.stop_flag.set()
        self.led_thread.join()

    def toggle_left(self):
        """Toggle the left light section"""
        self.led_thread.section_left = not self.led_thread.section_left

    def toggle_right(self):
        """Toggle the right light section"""
        self.led_thread.section_right = not self.led_thread.section_right

    def toggle_main(self):
        """Toggle the main lights"""
        self.led_thread.section_main = not self.led_thread.section_main

    def set_main_off(self):
        """Switch the main lights off and reset the main pattern"""
        self.led_thread.reset_main()

    def change_main_pattern(self):
        """Selct the next pattern for the main lights and switch the main lights on"""
        if self.led_thread.section_main:
            self.led_thread.select_next_main_pattern()
        else:
            self.led_thread.section_main = True
