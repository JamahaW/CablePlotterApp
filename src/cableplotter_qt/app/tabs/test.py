from PyQt6.QtWidgets import QBoxLayout
from PyQt6.QtWidgets import QVBoxLayout

from cableplotter_qt.ui.tab import Tab


#
# class Demo(QGraphicsView):
#     def __init__(self):
#         super(Demo, self).__init__()
#         self.resize(300, 300)
#
#         self.scene = QGraphicsScene()
#         self.scene.setSceneRect(0, 0, 300, 300)
#
#         # 1 Вызовите методы addRect(), addEllipse() и addPixmap() сцены напрямую, чтобы добавить примитивы.
#         #   Вам нужно знать один момент здесь:
#         #   Элемент, который добавляется первым, находится ниже элемента, который добавляется позже
#         #   (направление оси Z). Вы можете запустить код самостоятельно, а затем переместить элемент.
#         #   После этого вы увидите, что элемент изображения в программе находится сверху,
#         #   затем эллипс, а прямоугольник - в Внизу.
#         #   Однако мы можем изменить верхнюю и нижнюю позиции, вызвав метод setZValue() примитива
#         #   (пожалуйста, обратитесь к документации, чтобы понять, здесь подробно не объясняется).
#         #   QGraphicsItem::setZValue(qreal z)
#         self.rect = self.scene.addRect(100, 30, 100, 30, brush=QBrush(QColor(230, 30, 230)))
#         self.ellipse = self.scene.addEllipse(100, 80, 50, 40,
#                                              brush=QBrush(QColor(230, 30, 30), Qt.BrushStyle.Dense6Pattern))
#         self.pic = self.scene.addPixmap(QPixmap('ball.png').scaled(60, 60))
#         self.pic.setOffset(100, 130)  # установить смещение изображения от начала координат сцены;
#         # По умолчанию Z-значение равно 0.
#         # self.ellipse.setZValue(1)
#
#         #   Затем установите свойство Flag примитива. Дополнительный ItemIsFocusable здесь указывает,
#         #   что графика может быть сфокусирована (значение по умолчанию не фокусируется) .
#         #   Этот атрибут связан с сигналом focusItemChanged, описанным в третьем пункте ниже;
#         self.rect.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
#                            QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
#                            QGraphicsItem.GraphicsItemFlag.ItemIsFocusable)
#         self.ellipse.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
#                               QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
#                               QGraphicsItem.GraphicsItemFlag.ItemIsFocusable)
#         self.pic.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
#                           QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
#                           QGraphicsItem.GraphicsItemFlag.ItemIsFocusable)
#
#         self.setScene(self.scene)
#
#         # 2 Вызов метода items() может вернуть все примитивы в сцене, а тип возвращаемого значения - список.
#         #   Возвращенные элементы сортируются по убыванию по умолчанию (Qt.DescendingOrder),
#         #   то есть располагаются сверху вниз (QPixmapItem, QEllipseItem, QRectItem).
#         #   Вы можете изменить значение параметра order, чтобы расположить элементы, возвращенные в списке,
#         #   в порядке возрастания.
#
#         # print(self.scene.items())
#         s = "\n\t\t".join([str(i) for i in self.scene.items()])
#         print(f'\n scene.items -> {s}')
#         # Это перечисление описывает, как элементы в виджете сортируются.
#         # print(self.scene.items(order=Qt.AscendingOrder))
#         s = "\n\t\t".join([str(i) for i in self.scene.items(order=Qt.SortOrder.AscendingOrder)])
#         print(f'\n scene.items(order) -> {s}')
#         #   itemsBoundingRect() возвращает границы всех примитивов.
#         print(f'\n scene.itemsBoundingRect -> {self.scene.itemsBoundingRect()}')
#         #   itemAt() может возвращать примитивы в указанной позиции.
#         #   Если в этой позиции есть два перекрывающихся примитива, то возвращается верхний примитив.
#         #   Переданный QTransform() связан со свойством Flag ItemIgnoresTransformations.
#         #   Так как это свойство здесь не установлено, мы можем напрямую передать QTransform()
#         #   (здесь это не детализировано, в противном случае это может сбить с толку,
#         #   вы можете сначала просто запомнить его, а потом углубиться в него);
#         print(f'\n scene.itemAt -> {self.scene.itemAt(110, 40, QTransform())}')
#         print(f' scene.itemAt -> {self.scene.itemAt(110, 90, QTransform())}')
#         print(f' scene.itemAt -> {self.scene.itemAt(110, 140, QTransform())}')
#         print(f' scene.itemAt -> {self.scene.itemAt(10, 90, QTransform())}')
#
#         # 3 Сцена имеет сигнал focusItemChanged. Этот сигнал будет излучаться,
#         #   когда мы выбираем разные объекты, при условии, что для объекта установлено свойство ItemIsFocusable.
#         #   Этот сигнал может принимать два значения:
#         #       первое (new_item) - это вновь выбранный примитив,
#         #       второе (old_item) - ранее выбранный примитив;
#
#         # noinspection PyUnresolvedReferences
#         self.scene.focusItemChanged.connect(self.my_slot)
#
#     def my_slot(self, new_item, old_item):
#         print('\n new item: {}\n old item: {}'.format(new_item, old_item))
#
#     # 4. Вызовите collidingItems() сцены, чтобы распечатать все другие объекты,
#     #    которые сталкиваются с целевым объектом при указанном условии запуска столкновения;
#
#     def mouseMoveEvent(self, event):
#         print(self.scene.collidingItems(self.ellipse, Qt.ItemFlag.IntersectsItemShape))
#         super().mouseMoveEvent(event)
#
#     # 5 Также необходимо изменить !!!
#     #   Мы можем дважды щелкнуть на примитиве, чтобы удалить его, вызвав метод removeItem().
#     #   Обратите внимание, что фактически неточно передавать event.pos() напрямую в itemAt(),
#     #   потому что event.pos() - это фактически координаты мыши в представлении, а не координаты сцены.
#     #   Вы можете увеличить окно и снова дважды щелкнуть, чтобы обнаружить, что примитивы не исчезнут,
#     #   потому что размер вида больше не соответствует размеру сцены, а координаты изменились.
#     #   Конкретные решения см. В разделе 34.4. (ниже) !!!
#
#     def mouseDoubleClickEvent(self, event):
#         item = self.scene.itemAt(event.pos(), QTransform())
#         self.scene.removeItem(item)
#         super().mouseDoubleClickEvent(event)


class TestTab(Tab):

    def __init__(self) -> None:
        super().__init__("Test")
        self.setLayout(self.makeLayout())

    def makeLayout(self) -> QBoxLayout:
        L = QVBoxLayout()

        # label = QLabel()
        # label.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        # label.setStyleSheet("image:url(%1);image-position: center;")
        # label.setPixmap(QPixmap(r"A:\Program\Python3\CablePlotter\data\in\bear.png"))
        #
        # L.addWidget(label)

        # L.addWidget(Demo())

        return L
