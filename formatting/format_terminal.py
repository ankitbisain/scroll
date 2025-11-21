import textwrap
import shutil
from pylatexenc.latex2text import LatexNodes2Text


def compile_and_center(par, margin, width):
    text_width = width - 2 * margin
    compiled_text = LatexNodes2Text().latex_to_text(par)
    wrapped_lines = textwrap.wrap(compiled_text, width=text_width)
    centered_lines = [(" " * margin + line) for line in wrapped_lines]
    return "\n".join(centered_lines)


def reset_screen(height, color):
    print(color + "\n" * height)


def jump(height):
    print(f"\033[{height};1H", end="")


def fit_to_screen(pars, margin, color):
    width, height = shutil.get_terminal_size()
    centered_pars = [compile_and_center(par, margin, width) for par in pars]
    final_text = "\n\n\n".join(centered_pars)
    bottom_margin = "\n" * max(0, (height - len(final_text.split("\n"))) // 2)
    reset_screen(height, color)
    print(final_text + bottom_margin)
    jump(height)
