from signal import pause
from gpiozero import Button

from led_lights import LedLights


LED_COUNT = 100     # count of all LEDs in strip
SECTION_SIZE = 12   # count of LEDs used for left and right section

BUTTON_MAIN = 27    # GPIO27 - Button for main LED section
BUTTON_LEFT = 17    # GPIO17 - Button for left LED section
BUTTON_RIGHT = 22   # GPIO22 - Button for left LED section


class BedControl:
    def __init__(self, led_count, section_size, button_main, button_left, button_right):
        self.lights = LedLights(led_count, section_size)
        self.button_main = Button(button_main)
        self.button_left = Button(button_left)
        self.button_right = Button(button_right)

    def run(self):
        self.button_main.when_pressed = self.lights.toggle_main
        self.button_left.when_pressed = self.lights.toggle_left
        self.button_right.when_pressed = self.lights.toggle_right
        
        pause()


if __name__ == '__main__':
    ctrl = BedControl(LED_COUNT, SECTION_SIZE, BUTTON_MAIN, BUTTON_LEFT, BUTTON_RIGHT)
    ctrl.run()

