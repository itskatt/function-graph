import argparse
import sys

from . import Orthogonal


def get_cli_args():
    p = argparse.ArgumentParser(description="Function graph generator.")

    p.add_argument(
        "expression",
        help="The expression(s) to be drawn on the graph.",
        type=str,
        nargs="+"
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
        "-v",
        "--verbose",
        help="Give more output while generating the graph.",
        action="store_true",
        default=False
    )
    p.add_argument(
        "-f",
        "--filename",
        help="The output filename. The extention is automaticly added.",
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

    return p.parse_args()


def interactive_setup():
    print(
        "Welcome to this simple function graph generator.\n"
        "To start, please enter your expression bellow:\n"
    )
    expr = input(": ")
    ortho = Orthogonal(
        expr,
        size=500,
        animated=False,
        graduation=10
    )
    ortho.draw_graph()


def main():
    if len(sys.argv) > 1:
        args = get_cli_args()
    else:
        interactive_setup()
        sys.exit()  # Temporary

    ortho = Orthogonal(
        args.expression,
        args.size,
        graduation=args.graduation,
        animated=args.animated,
        filename=args.filename,
        verbose=args.verbose
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
