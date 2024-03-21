import io

from pyboy import PyBoy
from PIL import Image
from typing import List


class Emulator(PyBoy):
    def __init__(self, rom_path, **kwargs):
        super().__init__(rom_path, **kwargs)
        self.set_emulation_speed(0)
        self.images: List[Image] = []

    def sim_button_time(self, button: str, frames: int):
        self.button_press(button)
        for _ in range(5):
            self.tick()
        self.button_release(button)

        for _ in range(frames):
            self.tick()

    def make_gif(self):
        img_byte_arr = io.BytesIO()

        self.images[0].save(img_byte_arr,
                            duration=len(self.images)//3,
                            save_all=True,
                            append_images=self.images[1:],
                            format="GIF",
                            loop=1)

        self.images = []
        img_byte_arr.seek(0)
        return img_byte_arr

    def tick(self, count: int = 1, render: bool = True):
        super().tick(count, True)
        self.images.append(self.screen.image.copy())


if __name__ == "__main__":
    pyboy = Emulator("./Pokemon - Red Version (USA, Europe) (SGB Enhanced).gb")

    for i in range(10000):
        pyboy.tick()
    pyboy.stop()
