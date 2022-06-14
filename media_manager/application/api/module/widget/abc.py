from abc import ABC, abstractmethod

from PySide2.QtCore import QEvent
from PySide2.QtWidgets import QWidget

from media_manager.application.api.events import EventPool
from media_manager.application.api.events.gui import GuiEvent


class Widget(QWidget):
    def __init__(self, widget: "ModuleWidget"):
        super().__init__()
        self.__widget = widget

    def widget(self) -> "ModuleWidget":
        return self.__widget

    def event(self, event: QEvent) -> bool:
        # Qt event must be processed first
        q_result = super().event(event)
        self.__widget.events.announce(GuiEvent(event, self))
        return q_result


class ModuleWidget(ABC):
    def __init__(self):
        # Safety for sharing
        self.events = EventPool()


    def type(self) -> str:
        return "Other"

    @abstractmethod
    def widget(self) -> Widget:
        pass
