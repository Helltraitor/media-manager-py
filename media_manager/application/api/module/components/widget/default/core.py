from weakref import ReferenceType

from PySide2.QtCore import Qt, QEvent
from PySide2.QtGui import QIcon, QPaintEvent, QMouseEvent
from PySide2.QtWidgets import QLabel, QVBoxLayout

from media_manager.application import utils
from media_manager.application.api.events.gui import GuiEvent
from media_manager.application.api.events.module.widget import (
    WidgetFocusedEvent,
    WidgetHoveredEvent,
    WidgetUnhoveredEvent
)

from .listeners import DefaultBackgroundListener, DefaultBackgroundPaintEventListener
from .painters import ModuleWidgetNoneBackgroundPainter

from ..abc import Widget

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..component import CDefaultWidget


class DefaultWidget(Widget):
    def __init__(self, component: ReferenceType["CDefaultWidget"]):
        super().__init__(component)  # type: ignore
        self.painter = ModuleWidgetNoneBackgroundPainter
        self.__icon = QLabel()
        self.__title = QLabel()
        self.__layout = QVBoxLayout(self)
        self.__setup()

    def __setup(self):
        # Labels
        self.__icon.setContentsMargins(0, 0, 0, 0)
        self.__icon.setPixmap(QIcon(self.component().icon()).pixmap(36, 36))  # type: ignore
        self.__title.setText(self.component().title())  # type: ignore
        # Layout
        self.__layout.setContentsMargins(6, 6, 6, 6)
        self.__layout.addWidget(self.__icon, alignment=Qt.AlignCenter)
        self.__layout.addWidget(self.__title, alignment=Qt.AlignCenter)
        # Subscriptions
        self.component().events().subscribe(DefaultBackgroundListener(self))
        self.component().events().subscribe(DefaultBackgroundPaintEventListener(self))

    def mousePressEvent(self, event: QMouseEvent):
        from media_manager.application.api.module.abc import ViewableModule

        super().mousePressEvent(event)
        if event.button() == Qt.LeftButton:
            if module := utils.dynamic_cast(self.component().module(), ViewableModule):
                self.component().events().announce(WidgetFocusedEvent(module))

    def enterEvent(self, event: QEvent):
        from media_manager.application.api.module.abc import ViewableModule

        super().enterEvent(event)
        if module := utils.dynamic_cast(self.component().module(), ViewableModule):
            self.component().events().announce(WidgetHoveredEvent(module))

    def leaveEvent(self, event: QEvent):
        from media_manager.application.api.module.abc import ViewableModule

        super().leaveEvent(event)
        if module := utils.dynamic_cast(self.component().module(), ViewableModule):
            self.component().events().announce(WidgetUnhoveredEvent(module))

    def paintEvent(self, event: QPaintEvent):
        super().paintEvent(event)
        self.component().events().announce(GuiEvent(event, self))
