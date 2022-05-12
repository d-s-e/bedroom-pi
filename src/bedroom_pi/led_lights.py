import logging
import signal
from collections import defaultdict
from enum import Enum
from time import sleep
from threading import Event, Thread
from rpi_ws281x import Color, PixelStrip, ws

from led_patterns import patterns_main, patterns_section


logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


# LED strip low level configuration:
LED_PIN = 10  # LED GPIO pin (use 10 for SPI or 18 for PWM).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10  # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 128  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False  # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0
LED_STRIP = ws.SK6812_STRIP_GRBW


class LedSection(Enum):
    LEFT = ("left",)
    RIGHT = ("right",)
    MAIN = ("main",)


class LedThread(Thread):
    def __init__(self, led_count, section_size):
        super().__init__()
        self._section_left = False
        self._section_right = False
        self._section_main = False
        self._current_patterns = defaultdict(lambda: 0)
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

    def select_next_pattern(self, section: LedSection):
        if (
            self._current_patterns[section]
            >= len(patterns_main if section == LedSection.MAIN else patterns_section) - 1
        ):
            self._current_patterns[section] = 0
        else:
            self._current_patterns[section] += 1
        self._set_lights()

    def reset_lights(self):
        """Switch all lights off and reset selected patterns"""
        self._section_left = False
        self._section_right = False
        self._section_main = False
        self._current_patterns = defaultdict(lambda: 0)
        self._set_lights()

    def _set_lights(self):
        if self._section_main:
            self._led_buffer = patterns_main[self._current_patterns[LedSection.MAIN]].get_frame(
                self._led_count
            )
        else:
            self._led_buffer = [Color(0, 0, 0, 0)] * self._led_count

        if self._section_left:
            for i in range(self._section_size):
                self._led_buffer[i] = patterns_section[
                    self._current_patterns[LedSection.LEFT]
                ].get_frame(self._section_size)[i]

        if self._section_right:
            for i in range(self._section_size):
                self._led_buffer[self._led_count - 1 - i] = self._led_buffer[i] = patterns_section[
                    self._current_patterns[LedSection.RIGHT]
                ].get_frame(self._section_size)[i]

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

    @property
    def led_status(self):
        return {
            LedSection.LEFT: self.led_thread.section_left,
            LedSection.MAIN: self.led_thread.section_main,
            LedSection.RIGHT: self.led_thread.section_right,
        }

    def toggle_left(self):
        """Toggle the left light section"""
        self.led_thread.section_left = not self.led_thread.section_left

    def toggle_right(self):
        """Toggle the right light section"""
        self.led_thread.section_right = not self.led_thread.section_right

    def toggle_main(self):
        """Toggle the main lights"""
        self.led_thread.section_main = not self.led_thread.section_main

    def set_section_off(self, section: LedSection):
        """Switch a light section off"""
        if section == LedSection.MAIN:
            self.led_thread.section_main = False
        elif section == LedSection.LEFT:
            self.led_thread.section_left = False
        elif section == LedSection.RIGHT:
            self.led_thread.section_right = False

    def change_pattern(self, section: LedSection):
        """Selct the next pattern for a section and/or switch the section on"""
        if self.led_status[section]:
            self.led_thread.select_next_pattern(section)
        elif section == LedSection.MAIN:
            self.led_thread.section_main = True
        elif section == LedSection.LEFT:
            self.led_thread.section_left = True
        elif section == LedSection.RIGHT:
            self.led_thread.section_right = True
