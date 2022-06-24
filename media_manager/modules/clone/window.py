from weakref import ReferenceType

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QPushButton, QLabel, QVBoxLayout

from media_manager.application.api.context import Context
from media_manager.application.api.messages import Message, CallbackMessage
from media_manager.application.api.module.components import CWindow
from media_manager.application.api.module.components.window.abc import Window
from media_manager.application.api.module.features import FWindow


class CloneWindow(Window):
    def __init__(self, component: ReferenceType[CWindow]):
        super().__init__(component)
        self.__clone_title = QLabel(f'Clone #{self.component().id()}')
        self.__clone_up = QPushButton("^^^")
        self.__clone_value = QLabel("0")
        self.__clone_down = QPushButton("vvv")
        self.__layout = QVBoxLayout(self)
        self.__setup()

    def __setup(self):
        self.__layout.setContentsMargins(6, 6, 6, 6)
        self.__layout.addWidget(self.__clone_title, alignment=Qt.AlignTop)
        self.__layout.addSpacing(6)
        self.__layout.addWidget(self.__clone_up, alignment=Qt.AlignTop)
        self.__layout.addWidget(self.__clone_value, alignment=Qt.AlignTop)
        self.__layout.addWidget(self.__clone_down, alignment=Qt.AlignTop)
        # INIT SETTING
        # TODO: RECOVER CLIENT
        # client = self.__window.module().client()
        # client.send({"name": "Settings"}, Message({"action": "set", "key": f"{self.__id}-value", "value": "0"}))
        # BUTTON
        self.__clone_up.setAutoRepeat(True)
        # self.__clone_up.clicked.connect(
        #     lambda: change_value(client, self.__id, self.__clone_value, 1))
        self.__clone_down.setAutoRepeat(True)
        # self.__clone_down.clicked.connect(
        #     lambda: change_value(client, self.__id, self.__clone_value, -1))


class CCloneWindow(CWindow):
    def __init__(self, context: Context):
        super().__init__(context)
        self.__context = context
        self.__window = CloneWindow(ReferenceType(self))

    def id(self) -> str:
        return self.__context.unwrap('id', str)

    def window(self) -> Window:
        return self.__window


def change_value(client, id, label, delta):
    def update(value):
        # then change fresh value
        client.send({"name": "Settings"}, CallbackMessage(
            # and update label
            lambda reply: fetch_value(client, id, label),
            {"action": "update", "key": f"{id}-value", "value": str(value)}))
    # get fresh value
    client.send({"name": "Settings"}, CallbackMessage(
        # update after getting value
        lambda reply: update(int(reply.content().get("value")) + delta), {
            "action": "get", "key": f"{id}-value"}))


def fetch_value(client, id, label):
    client.send({"name": "Settings"}, CallbackMessage(
                lambda reply: label.setText(reply.content().get("value", label.text())), {
                    "action": "get", "key": f"{id}-value"}))
