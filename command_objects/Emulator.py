import io
import os.path

import PIL
from pyboy import PyBoy
from PIL import Image
from typing import List, Optional


class Emulator(PyBoy):
    def __init__(self, rom_path, **kwargs):
        super().__init__(rom_path, sound_emulated=False, sound=False, **kwargs)
        self.set_emulation_speed(5)
        self.images: List[Image] = []
        self.skipped_frames = 4
        self.state_file = "./data/pokemon.state"

        #load save state when bot is started
        if os.path.isfile(self.state_file):
            with open(self.state_file, "rb") as f:
                if f:
                    self.load_state(f)
        self.prev_map = self.memory[0xD35E]

    def sim_button_time(self, button: Optional[str], frames: int) -> None:
        """
        :param button: Name of the button to press. can be 'up', 'down', 'left', 'right', 'a', 'b', 'start', 'select' or None.
        :param frames: the amount of frames to simulate.
        """

        if button:
            self.button_press(button)
            # we don't want to hold the button for too long, nor too short, this is a guess
            for _ in range(8 // self.skipped_frames):
                self.tick(self.skipped_frames)
            self.button_release(button)

        for _ in range(frames // self.skipped_frames):
            self.tick(self.skipped_frames)

        current_map = self.memory[0xD35E]
        if self.prev_map != current_map:
            self.prev_map = current_map
            with open(self.state_file, "wb") as f:
                self.save_state(f)

    def make_gif(self) -> io.BytesIO:
        """
        Makes a gif from the simulated frames and empties the frame buffer.
        :return: IO of the GIF that can be used as a file.
        """
        img_byte_arr = io.BytesIO()

        self.images[0].save(
            img_byte_arr,
            duration=1000 // (60//self.skipped_frames),  # 1000 (full sec) divided by frames per sec (30)
            save_all=True,
            append_images=self.images[1:],
            format="GIF",
            optimize=False # This could reduce file size at the cost of more computation
        )

        self.images.clear()
        img_byte_arr.seek(0)
        return img_byte_arr

    def tick(self, count: int = 3, render: bool = True):
        super().tick(count=count, render=render)
        image: Image = self.screen.image.copy()
        image = image.resize((image.width* 2, image.height*2))
        self.images.append(image)


if __name__ == "__main__":
    pyboy = Emulator("../data/pokemon_red.gb")

    for i in range(10000):
        pyboy.tick()
    pyboy.stop()
