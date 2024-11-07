import os
from dataclasses import dataclass
from tkinter import *
from tkinter import filedialog
from tkinter import scrolledtext

from code_gen import PlotterCodeGenerator
from printcoder import Vector2
from printcoder import VertexGenerator


@dataclass
class ImageData:
    vertices_source = list[Vector2]()
    vertices_transformed: list[Vector2] | None = None
    pen_idle_indices = set[int]()

    def clear(self):
        self.pen_idle_indices.clear()
        self.vertices_source.clear()
        self.vertices_transformed.clear()

    def extend(self, vex: list[Vector2]):
        self.vertices_source.extend(vex)
        return self

    def transform(self, scale: Vector2, angle: float, offset: Vector2):
        if self.vertices_source is None:
            self.vertices_source = list()

        scaled = VertexGenerator.scale(self.vertices_source, scale)
        optimised = VertexGenerator.removeNear(scaled, 1.4)
        rotated = VertexGenerator.rotate(optimised, angle)
        moved = VertexGenerator.move(rotated, offset)

        self.vertices_transformed = moved

        self.pen_idle_indices = VertexGenerator.findFarIndices(moved)


class Draw:

    def __init__(self, canvas: Canvas, size_mm):
        self.canvas = canvas
        self.RES = Vector2(1000, 400)
        self.size_mm = size_mm

    def reset(self):
        self.canvas.delete("all")
        self.drawGrid()

    def toPos(self, pos):
        x, y = pos

        aspect = self.RES.y / self.size_mm.y

        x *= aspect
        y *= -aspect

        return (
            x + self.RES.x / 2,
            y + self.RES.y / 2 + 10
        )

    def line(self, pos1, pos2, color="#222", width=2):
        self.canvas.create_line(self.toPos(pos1), self.toPos(pos2), fill=color, joinstyle=ROUND, width=width, activewidth=width * 2, activefill="#3D4")

    def rect(self, pos1, pos2, color="#F33", width=5):
        x1, y1 = pos1
        x2, y2 = pos2

        self.line((x1, y1), (x2, y1), color, width)
        self.line((x2, y1), (x2, y2), color, width)
        self.line((x2, y2), (x1, y2), color, width)
        self.line((x1, y2), (x1, y1), color, width)

    def point(self, pos, color="#EB2", r=1):
        x, y = self.toPos(pos)
        self.canvas.create_oval(x - r, y - r, x + r, y + r, fill=color, activefill="#522")

    def path(self, vertices: list[Vector2], pen_idles: set[int]):
        L = len(vertices) - 1

        for i in range(L + 1):
            v = vertices[i].toTuple()
            self.point(v)

            if i != L and i in pen_idles:
                self.line(v, vertices[i + 1].toTuple(), "#88F")

    def drawGrid(self):
        w = self.size_mm.x // 2
        h = self.size_mm.y // 2

        # BOARD RECT
        self.rect((-w, -h), (w, h))

        # AXES
        axes_color = "#028"
        self.line((0, -h), (0, h), axes_color)
        self.line((-w, 0), (w, 0), axes_color)

        # GRID
        def get_col(__i: int):
            return "#888" if i & 1 else "#CCC"

        scale_mm = 100

        for i, y in enumerate(range(0, h, scale_mm)):
            self.line((-w, y), (w, y), get_col(i))
            self.line((-w, -y), (w, -y), get_col(i))

        for i, x in enumerate(range(0, w, scale_mm)):
            self.line((x, -h), (x, h), get_col(i))
            self.line((-x, -h), (-x, h), get_col(i))


class App:

    @staticmethod
    def getFont(scale: int = 16):
        return "consolas Bold", scale

    @classmethod
    def acSpinBox(cls, master, range_: int, step: int | float = 25, init_value=0, func=None, _from=0):
        var = IntVar()
        var.set(init_value)

        return Spinbox(
            master,
            from_=_from,
            to=range_,
            increment=step,
            width=5,
            font=cls.getFont(),
            justify="left",
            command=func,
            textvariable=var
        )

    @classmethod
    def acFrame(cls, master):
        return Frame(master, borderwidth=1, relief=SOLID)

    @classmethod
    def acLabel(cls, master, text: str, font: int = 16):
        return Label(
            master,
            font=cls.getFont(font),
            justify=LEFT,
            text=text
        )

    @classmethod
    def acButton(cls, master, text: str, func):
        return Button(
            master=master,
            text=text,
            command=func,
            font=cls.getFont(),
            foreground="#FFF",
            background="#006363",
            activebackground="#1D7373",
            highlightbackground="#5CCCCC",
            borderwidth=3,
            justify=CENTER
        )

    @staticmethod
    def createWindow(width: int, height: int, title: str) -> Tk:
        window = Tk()
        window.geometry(f"{width}x{height}")
        window.title(title)
        return window

    def __init__(self):
        self.canvas_size_mm = Vector2(700, 1000)

        self.cutter = PlotterCodeGenerator()
        self.image_data = ImageData()
        self.program_data = None

        # ОКНО

        self.root = self.createWindow(1280, 720, "Print Coder")
        self.createMenu()

        # ВИДЖЕТЫ

        self.image_rotate = None
        self.image_scale_y = None
        self.image_scale_x = None
        self.height_spin = None
        self.width_spin = None
        self.image_pos_y = None
        self.image_pos_x = None
        self.createRightFrame()

        self.textlog = None
        self.canvas = None
        self.drawer: Draw | None = None
        self.createLeftFrame()

    def createRightFrame(self):
        frame = self.acFrame(self.root)
        frame.pack(side=RIGHT, fill=Y)

        self.createCanvasSizeUI(frame)
        self.createImageParamsUI(frame)
        self.createRightButtons(frame)
        self.createTestUI(frame)

    def createRightButtons(self, master):
        frame = Frame(master)
        frame.pack(anchor=S, fill=X)

        def cut():
            self.update()

            if not len(self.image_data.vertices_transformed):
                self.log("Рабочая область пуста")
                return

            log = self.cutter.run(
                (v.toTuple() for v in self.image_data.vertices_transformed),
                r"A:\Program\Python3\CablePlotterApp\res\out\test.blc"
            )

            self.log(log)

        self.acButton(frame, "Подготовить", cut).pack(anchor=S, pady=5, fill=X)

        def prepare():
            if self.program_data is None:
                self.log("Сначала нужно подготовить")
                return

            self.log(f"Началась нарезка")
            ret = filedialog.asksaveasfile("wb", confirmoverwrite=False, defaultextension=".blc", title="Сохранить программу")

            if ret is None:
                self.log("Файл не был сохранён")
                return

            ret.write(self.program_data)
            ret.close()

            self.log(f"Файл сохранён: {ret.name}")

        self.acButton(frame, "Сохранить", prepare).pack(anchor=S, pady=5, fill=X)

        def clear_board():
            self.image_data.clear()
            self.update()

        self.acButton(frame, "Очистить", clear_board).pack(anchor=S, pady=5, fill=X)

    def createImageParamsUI(self, master):
        frame = self.acFrame(master)
        frame.pack(anchor=NW, pady=50)

        def update_img():
            self.image_data.transform(
                Vector2(float(self.image_scale_x.get()), float(self.image_scale_y.get())),
                int(self.image_rotate.get()),
                Vector2(int(self.image_pos_x.get()), int(self.image_pos_y.get()))
            )
            self.update()

        self.acLabel(frame, "позиция").grid(column=0, row=0)
        self.image_pos_x = self.acSpinBox(frame, 1000, func=update_img, _from=-1000)
        self.image_pos_x.grid(column=1, row=0)
        self.image_pos_y = self.acSpinBox(frame, 1000, func=update_img, _from=-1000)
        self.image_pos_y.grid(column=2, row=0)

        self.acLabel(frame, "Масштаб").grid(column=0, row=1)
        self.image_scale_x = self.acSpinBox(frame, 10, 0.05, init_value=1, func=update_img)
        self.image_scale_x.grid(column=1, row=1)
        self.image_scale_y = self.acSpinBox(frame, 10, 0.05, init_value=1, func=update_img)
        self.image_scale_y.grid(column=2, row=1)

        self.acLabel(frame, "Поворот").grid(column=0, row=2)
        self.image_rotate = self.acSpinBox(frame, 360, 5, func=update_img)
        self.image_rotate.grid(column=1, row=2)

    def createCanvasSizeUI(self, master):
        frame = self.acFrame(master)
        frame.pack(anchor=NW, pady=5)

        def __update_s():
            self.canvas_size_mm.x = int(self.width_spin.get())
            self.canvas_size_mm.y = int(self.height_spin.get())
            self.log(f"Размер холста: {self.canvas_size_mm}")
            self.update()

        self.acLabel(frame, "холст").grid(column=0, row=0)
        self.width_spin = self.acSpinBox(frame, 5000, func=__update_s, init_value=1200)
        self.width_spin.grid(column=1, row=0)
        self.height_spin = self.acSpinBox(frame, 5000, func=__update_s, init_value=1200)
        self.height_spin.grid(column=2, row=0)

    def createLeftFrame(self):
        frame = self.acFrame(self.root)
        frame.pack(side=LEFT, fill=BOTH, expand=True)

        self.canvas = Canvas(frame, background="#DDD")
        self.canvas.pack(fill=BOTH, side=TOP, expand=True, pady=5)

        self.drawer = Draw(self.canvas, self.canvas_size_mm)
        self.drawer.drawGrid()

        self.acLabel(frame, "Журнал приложения", 14).pack(anchor=W, padx=10)

        self.textlog = scrolledtext.ScrolledText(frame, height=15, background="#333", foreground="#FB0", font=self.getFont(10))
        self.textlog.pack(side=BOTTOM, fill=X)

    def createMenu(self):
        menu = Menu(self.root)
        self.root.config(menu=menu)
        self.createMenuItemFile(menu)
        self.createMenuItemEdit(menu)

    @staticmethod
    def createMenuItem(menu, title: str):
        item = Menu(menu, tearoff=0)
        menu.add_cascade(menu=item, label=title)
        return item

    def menuAddCommand(self, menu: Menu, name: str, func=None):
        menu.add_command(label=name, command=lambda: self.log(f"menu command TODO {name}") if func is None else func)

    def createMenuItemEdit(self, menu):
        edit_item = self.createMenuItem(menu, "Изменить")
        add_vex = self.createMenuItem(edit_item, "add")
        self.menuAddCommand(add_vex, "X")

    def createMenuItemFile(self, menu):
        file_item = self.createMenuItem(menu, "Файл")
        file_item.add_command(label='Открыть', command=self.selectOpenFile)
        file_item.add_command(label='Изменить')

    def createTestUI(self, master):
        frame = self.acFrame(master)
        frame.pack(anchor=SE, pady=5, padx=10, fill=X, expand=True)
        self.acLabel(frame, "Шаблоны").pack(side=TOP)

        def cross():
            self.log("cross")

            self.image_data.extend(
                VertexGenerator.line(Vector2(100, 0), Vector2(-100, 0), 1000)
            ).extend(
                VertexGenerator.line(Vector2(0, 100), Vector2(0, -100), 1000)
            )

            self.update()

        self.acButton(frame, "Крест", cross).pack(fill=X)

        def spiral():
            self.log("Спираль")
            self.image_data.extend(VertexGenerator.spiral(100, 5000, 4))
            self.update()

        self.acButton(frame, "Спираль", spiral).pack(fill=X)

        def rect():
            self.log("прямоугольник")
            self.image_data.extend(VertexGenerator.rect(100, 100, 1000))
            self.update()

        self.acButton(frame, "Прямоугольник", rect).pack(fill=X)

        def circle():
            self.log("Окружность")
            self.image_data.extend(VertexGenerator.circle(100, 1000))
            self.update()

        self.acButton(frame, "Окружность", circle).pack(fill=X)

    def update(self):
        self.drawer.reset()
        self.image_data.transform(
            Vector2(float(self.image_scale_x.get()), float(self.image_scale_y.get())),
            int(self.image_rotate.get()),
            Vector2(int(self.image_pos_x.get()), int(self.image_pos_y.get()))
        )
        self.drawer.path(self.image_data.vertices_transformed, self.image_data.pen_idle_indices)

    def selectOpenFile(self):
        target_file = filedialog.askopenfilename(initialdir=os.path.dirname(__file__), filetypes=(("images", "*.png"), ("all files", "*.*")))
        self.log(f"Выбран файл: {target_file}")
        self.image_data.extend(VertexGenerator.image(target_file))

    def log(self, message: object):
        self.textlog.insert(INSERT, str(message) + "\n")

    def todo(self):
        self.log("TODO")

    def run(self):
        self.root.mainloop()


def main():
    App().run()


main()
