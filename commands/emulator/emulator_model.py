import io
import os.path

import PIL
from PIL.Image import Image
from pyboy import PyBoy
from typing import List, Optional


class Emulator(PyBoy):
    def __init__(self, rom_path, **kwargs):
        super().__init__(rom_path, sound_emulated=False, sound=False, **kwargs)
        self.set_emulation_speed(5)
        self.images: List[Image] = []
        self.skipped_frames = 4
        self.state_file = "./data/pokemon.state"

        #load save state on init
        if os.path.isfile(self.state_file):
            with open(self.state_file, "rb") as f:
                self.load_state(f)

    def sim_button_time(self, button: Optional[str], frames: int) -> None:
        """
        :param button: Name of the button to press. can be 'up', 'down', 'left', 'right', 'a', 'b', 'start', 'select' or None.
        :param frames: the amount of frames to simulate.
        """
        # press a button if defined
        if button:
            self.button(button, 8)

        # run the select amount of frames
        for _ in range(frames // self.skipped_frames):
            self.tick(self.skipped_frames)

        # save the state 
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
            duration=1000 // (60//self.skipped_frames),  # 1000 (full sec) divided by frames per sec (60)
            save_all=True,
            append_images=self.images[1:],
            format="GIF",
            optimize=False # This could reduce file size at the cost of more computation
        )
        img_byte_arr.seek(0)
        self.images.clear()
        
        return img_byte_arr

    def tick(self, count: int = 3, render: bool = True, sound: bool = False) -> bool:
        result = super().tick(count=count, render=render, sound=sound)
        if self.screen.image is not None:
            image = self.screen.image.copy()
            image = image.resize((image.width* 2, image.height*2))
            self.images.append(image)
        return result


if __name__ == "__main__":
    pyboy = Emulator("../data/pokemon_red.gb")

    for i in range(10000):
        pyboy.tick()
    pyboy.stop()
