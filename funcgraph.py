import argparse
import io
import math
import time
from contextlib import contextmanager

from PIL import Image, ImageDraw


class Orthogonal():
    """
    .
    """

    def __init__(self, expression, size=500, mode="static", graduation=None, loop=0, save_to_buffer=False,
                 filename="graph"):
        self.width = round(size)
        self.height = round(size)
        self.center = (round(size / 2), round(size / 2))

        self.expr = expression

        self.mode = mode
        self._graduation = graduation
        self._loop = loop
        self._save_to_buff = save_to_buffer
        self._filename = filename

        self._frames = []
        self._coord_list = []

        self.stats = {
            "calculation_time": None,
            "draw_time": None,
            "save_time": None
        }

    @contextmanager
    def _mesure_time(self, val):
        start = time.perf_counter()
        yield
        self.stats[val] = time.perf_counter() - start

    def _coords(self, x, y):
        """
        Helper that onverts normal coordinates in an orthogonal...
        to image ones. Does round
        """
        return (
            # Coordinates must be integer, so we must round
            round(self.center[0] + x),
            round(self.center[1] - y)
        )

    def _draw_lines(self, d):
        """
        d: An ImageDraw instance
        """
        # Horizontal line
        d.line(
            [
                self._coords(-self.center[0], 0),
                self._coords(self.center[0], 0)
            ],
            "black",
            self.height // 100
        )
        # Vertical line
        d.line(
            [
                self._coords(0, self.center[1]),
                self._coords(0, -self.center[1])
            ],
            "black",
            self.width // 100
        )
        # We don't draw the graduation if there is no graduation and
        # if it will look bad
        if not self._graduation:
            return
        if self._graduation > self.height / 10 and self._graduation > self.width / 10:
            return

        # Horizontal graduation
        hgrad = round(self.center[0] / self._graduation)

        for c in range(-self.center[0], self.center[0], hgrad):
            d.line(
                [
                    self._coords(c, self.width // 50),
                    self._coords(c, -(self.width // 50))
                ],
                "black",  # For a real grid look it happens here
                self.width // 250
            )

        # Vertical graduation
        vgrad = round(self.center[1] / self._graduation)

        for c in range(-self.center[1], self.center[1], vgrad):
            d.line(
                [
                    self._coords(self.height // 50, c),
                    self._coords(-(self.height // 50), c)
                ],
                "black",
                self.height // 250
            )

    def _calculate_coords(self):
        if self._graduation:
            a = round(self.center[0] / self._graduation)
        else:
            a = 1
        env = {
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,

            "asin": math.asin,
            "acos": math.acos,
            "atan": math.atan,

            "deg": math.degrees,
            "rad": math.radians,

            "log": math.log,
            "log10": math.log10,
            "log2": math.log2,
            "factorial": math.factorial,

            "ceil": math.ceil,
            "floor": math.floor,
            "trunc": math.trunc,

            "exp": math.exp,
            "expm1": math.expm1,

            "gamma": math.gamma,
            "lgamma": math.lgamma,

            "pi": math.pi,
            "e": math.e,
            "tau": math.tau
        }
        for x in range(-self.center[0], self.center[0]):
            env.update({"x": x / a})
            try:
                y = eval(self.expr, env)
            except ArithmeticError:
                self._coord_list.append(None)
            else:
                self._coord_list.append(self._coords(x, y * a))

    def _draw_graph_line(self, bg, draw, size):

        for i, c in enumerate(self._coord_list):
            try:
                line_end = self._coord_list[i + 1]
                assert line_end is not None
                assert c is not None
            except (AssertionError, IndexError):
                try:
                    if c[1] < self.height and line_end[1] > self.height:
                        pass
                    else:
                        continue
                except TypeError:
                    continue
            try:
                draw.line(
                    [c, line_end],
                    "red",  # Color change
                    size
                )
            except OverflowError:
                # An OverflowError was raised (ex: Python int too large
                # to convert to C long)
                pass
            else:
                if self.mode == "animated":
                    self._frames.append(bg.copy())

    def draw_graph(self):
        """
        Calculates the coordinates, draws the graph and saves it
        """

        backgroud = Image.new("RGB", (self.width, self.height), "white")
        draw = ImageDraw.Draw(backgroud)

        self._draw_lines(draw)

        with self._mesure_time("calculation_time"):
            self._calculate_coords()

        with self._mesure_time("draw_time"):
            self._draw_graph_line(backgroud, draw, self.width // 125)  # <-- Dot/line size

        buffer = io.BytesIO()

        if self.mode == "animated":
            with self._mesure_time("save_time"):
                backgroud.save(
                    f"{self._filename}.gif" if not self._save_to_buff else buffer,
                    format="GIF",
                    append_images=self._frames[::2],
                    save_all=True,
                    duration=20,
                    loop=self._loop
                )
                buffer.seek(0)
                self.buffer = buffer
            return

        with self._mesure_time("save_time"):
            backgroud.save(
                f"{self._filename}.png" if not self._save_to_buff else buffer,
                format="PNG"
            )
            buffer.seek(0)
            self.buffer = buffer


def main():
    p = argparse.ArgumentParser(description="Function graph generator.")

    p.add_argument(
        "expression",
        help="The expression to be drawn on the graph.",
        type=str,
    )
    p.add_argument(
        "-s",
        "--size",
        help="The graph's size (width and height, in pixels).",
        type=int,
        default=500
    )
    p.add_argument(
        "-g",
        "--graduation",
        help="The graph's graduation.",
        type=int,
        default=10
    )
    p.add_argument(
        "-f",
        "--filename",
        help="The output filename. The extention is automaticly added",
        default="graph"
    )
    p.add_argument(
        "-a",
        "--animated",
        help="Output will be an animated gif.",
        action="store_true",
        default=False
    )
    p.add_argument(
        "-t",
        "--time",
        help="Print time information",
        action="store_true",
        default=False
    )

    args = p.parse_args()

    ortho = Orthogonal(
        args.expression,
        args.size,
        graduation=args.graduation,
        mode="animated" if args.animated else "static",
        filename=args.filename
    )
    ortho.draw_graph()
    if args.time:
        print(
            f"""
Calculation time: {ortho.stats["calculation_time"]}
       Draw time: {ortho.stats["draw_time"]}
       Save time: {ortho.stats["save_time"]}
        """
        )


if __name__ == "__main__":
    main()
