import io

from pyboy import PyBoy
import keyboard
from PIL import Image
from typing import List


class Emulator(PyBoy):
    def __init__(self, rom_path):
        super().__init__(rom_path)
        self.set_emulation_speed(0)
        self.images: List[Image] = []

    def sim_button_time(self, button: str, frames: int):
        self.button_press(button)
        for _ in range(5):
            self.tick()
        self.button_release(button)

        for _ in range(frames):
            self.tick()

    def tick(self, count: int = 5, render: bool = True):
        super().tick(count, True)
        self.images.append(self.screen.image.copy())

    def make_gif(self):
        img_byte_arr = io.BytesIO()

        self.images[0].save(img_byte_arr,
                            duration=len(self.images) * 17,
                            save_all=True,
                            append_images=self.images[1:],
                            format="GIF",
                            loop=0)

        img_byte_arr.seek(0)
        return img_byte_arr


if __name__ == "__main__":
    pyboy = Emulator("./Pokemon - Red Version (USA, Europe) (SGB Enhanced).gb")

    for i in range(10000):
        if keyboard.is_pressed("a"):
            pyboy.sim_button_time("a", 1)
        else:
            pyboy.tick(5)
    pyboy.stop()
