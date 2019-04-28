# NOTE: very very WIP
import tkinter as tk
from tkinter import ttk

# from .core import Orthogonal


# class GUIOrtho(Orthogonal):
#     def __init__(self, expr, grad):
#         super().__init__(expr, graduation=grad)


class Window(tk.Tk):
    def __init__(self):
        super().__init__()
        self.size = 500

        self.title("Function Graph")
        self.geometry("500x600")
        self.configure(bg="black")

        self.setup_screen()

        self.setup_graph_canvas()

    def setup_graph_canvas(self):
        c = self.canvas

        # Lines
        c.create_line(0, 250, 500, 250, width=4)  # NOTE: auto later
        c.create_line(250, 0, 250, 500, width=4)

        # TODO: Graduation

    def setup_screen(self):
        canvas = tk.Canvas(
            self,
            bg="grey",
            width=self.size,
            height=self.size
        )
        canvas.pack(fill=tk.Y)
        self.canvas = canvas

        ctrls_frame = ttk.Frame(
            self,
            width=500,
            height=250
        )
        ctrls_frame.pack(fill=tk.Y)
        rows = []
        for i in range(3):  # NOTE: Will change to auto later
            txt = ttk.Entry(ctrls_frame, width=25)
            but = ttk.Button(ctrls_frame, text="Desiner")
            txt.grid(row=i, column=0)
            but.grid(row=i, column=1)

            rows.append([txt, but])

        ctrls_frame.rows = rows
        self.ctrls_frame = ctrls_frame


def main():
    Window().mainloop()


if __name__ == "__main__":
    main()
