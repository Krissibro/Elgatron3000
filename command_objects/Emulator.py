import io

from pyboy import PyBoy
from PIL import Image
from typing import List


class Emulator(PyBoy):
    def __init__(self, rom_path, **kwargs):
        super().__init__(rom_path, sound_emulated=False, sound=False, **kwargs)
        self.set_emulation_speed(0)
        self.images: List[Image] = []
        self.frame = 0

    def sim_button_time(self, button: str, frames: int):
        self.button_press(button)
        for _ in range(5):
            self.tick()
        self.button_release(button)

        for _ in range(frames):
            self.tick()

    def make_gif(self) -> io.BytesIO:
        img_byte_arr = io.BytesIO()

        self.images[0].save(img_byte_arr,
                            duration=1000//30, #1000 (full sec) divided by frames per sec (30)
                            save_all=True,
                            append_images=self.images[1:],
                            format="GIF",
                            )

        self.images = []
        self.frame = 0
        img_byte_arr.seek(0)
        return img_byte_arr

    def tick(self, count: int = 1, render: bool = True):
        self.frame += 1
        super().tick(count, True)
        if self.frame % 2 == 1:
            self.images.append(self.screen.image.copy())


if __name__ == "__main__":
    pyboy = Emulator("../data/Pokemon - Red Version (USA, Europe) (SGB Enhanced).gb")

    for i in range(10000):
        pyboy.tick()
    pyboy.stop()
