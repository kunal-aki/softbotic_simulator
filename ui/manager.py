from ui.menu import MenuBar
from ui.toolbar import Toolbar
from ui.properties import PropertiesPanel
from ui.statusbar import StatusBar


class UIManager:

    def __init__(self):

        self.menu=MenuBar()

        self.toolbar=Toolbar()

        self.properties=PropertiesPanel()

        self.status=StatusBar()


    def draw(self,screen,font):

        self.menu.draw(
            screen,
            font
        )

        self.toolbar.draw(
            screen,
            font
        )

        self.properties.draw(
            screen,
            font
        )

        self.status.draw(
            screen,
            font
        )

