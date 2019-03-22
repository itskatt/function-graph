import argparse
import io
import math
import time

from PIL import Image, ImageDraw


class Orthogonal():
    """
    .
    """

    def __init__(self, expression, width=500, height=500, mode="static",
                 graduation=None, loop=0, save_to_buffer=False,
                 draw_out_of_bounds=False, filename="graph"):
        self.width = round(width)
        self.height = round(height)
        self.center = (round(width / 2), round(height / 2))

        self.expr = expression

        self.mode = mode
        self._graduation = graduation
        self._loop = loop
        self._save_to_buff = save_to_buffer
        self._out_of_bounds = draw_out_of_bounds
        self._filename = filename

        self._frames = []
        self._coord_list = []

        self.calculation_time = None
        self.draw_time = None
        self.save_time = None

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
        if self._graduation > self.height / 10 and \
                self._graduation > self.width / 10:
            return

        # Horizontal graduation
        hgrad = round(self.center[0] / self._graduation)

        for c in range(-self.center[0], self.center[0], hgrad):
            d.line(
                [
                    self._coords(c, 10),
                    self._coords(c, -10)
                ],
                "black",  # For a real grid look it happens here
                2
            )

        # Vertical graduation
        vgrad = round(self.center[1] / self._graduation)

        for c in range(-self.center[1], self.center[1], vgrad):
            d.line(
                [
                    self._coords(10, c),
                    self._coords(-10, c)
                ],
                "black",
                2
            )

    def _calculate_coords(self):
        if self._graduation:
            a = round(self.center[0] / self._graduation)
        else:
            a = 1

        for x in range(-self.center[0], self.center[0]):
            try:
                env = {
                    "x": x / a,

                    "sin": math.sin,
                    "cos": math.cos,
                    "tan": math.tan,

                    "asin": math.asin,
                    "acos": math.acos,
                    "atan": math.atan,

                    "deg": math.degrees,
                    "rad": math.radians,

                    "log": math.log,
                    "factorial": math.factorial,

                    "pi": math.pi,
                    "e": math.e,
                    "tau": math.tau
                }
                y = eval(self.expr, env)
            except ArithmeticError:
                self._coord_list.append(None)
            else:
                if y * a > self.height and self._out_of_bounds:  # Out of bound
                    self._coord_list.append(None)
                else:
                    self._coord_list.append(self._coords(x, y * a))

    def _draw_graph_line(self, bg, draw, size):

        for i, c in enumerate(self._coord_list):
            try:
                try:
                    line_end = self._coord_list[i + 1]
                    assert line_end is not None
                    assert c is not None
                except (AssertionError, IndexError):
                    continue

                draw.line(
                    [c, line_end],
                    "red",  # Color change
                    size
                )
                if self.mode == "animated":
                    self._frames.append(bg.copy())
            except OverflowError:
                # An OverflowError was raised (ex: Python int too large
                # to convert to C long)
                pass

    def draw_graph(self):
        """
        Calculates the coordinates, draws the graph and saves it
        """

        backgroud = Image.new("RGB", (self.width, self.height), "white")
        draw = ImageDraw.Draw(backgroud)

        self._draw_lines(draw)

        start = time.perf_counter()
        self._calculate_coords()
        self.calculation_time = time.perf_counter() - start

        start = time.perf_counter()
        self._draw_graph_line(backgroud, draw, 4)  # <-- Dot/line size
        self.draw_time = time.perf_counter() - start

        buffer = io.BytesIO()

        if self.mode == "animated":
            start = time.perf_counter()
            backgroud.save(
                f"{self._filename}.gif" if not self._save_to_buff else buffer,
                format="GIF",
                append_images=self._frames,
                save_all=True,
                duration=20,
                loop=self._loop
            )
            buffer.seek(0)
            self.buffer = buffer
            self.save_time = time.perf_counter() - start
            return

        start = time.perf_counter()
        backgroud.save(
            f"{self._filename}.png" if not self._save_to_buff else buffer,
            format="PNG"
        )
        buffer.seek(0)
        self.buffer = buffer
        self.save_time = time.perf_counter() - start


def main():
    p = argparse.ArgumentParser(description="Function graph generator.")

    p.add_argument(
        "expression",
        help="The expression to be drawn on the graph.",
        type=str,
    )
    p.add_argument(
        "-w",
        "--width",
        help="The graph's width (in pixels).",
        type=int,
        default=500
    )
    p.add_argument(
        "-hg",
        "--height",
        help="The graph's height (in pixels).",
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
        "-db",
        "--draw-out-bounds",
        help="Dots out of image will be drawn.",
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
        args.width,
        args.height,
        graduation=args.graduation,
        draw_out_of_bounds=args.draw_out_bounds,
        mode="animated" if args.animated else "static",
        filename=args.filename
    )
    ortho.draw_graph()
    if args.time:
        print(
            f"""
Calculation time: {ortho.calculation_time}
       Draw time: {ortho.draw_time}
       Save time: {ortho.save_time}
        """
        )


if __name__ == "__main__":
    main()
