from modules.modules import *
from modules.utilities import *
from core.event_creation import create_adventure

class Backbutton(ButtonBehavior, Image):
    """
    Botón de retroceso que permite volver a la pantalla principal.
    Hereda de ButtonBehavior e Image para tener comportamiento de botón y apariencia de imagen.
    """
    def __init__(self):
        super().__init__()
        self.source = "assets/backbutton.png"
        self.size_hint = (None, None)
        self.width = 150
        self.pos_hint = {'x': 0.02, 'top': 0.99}
        self.hover = setup_hover(self, 1)
    
    hovered = False

    def on_touch_down(self, touch):
        """
        Maneja el evento de toque. Si se toca el botón y no está deshabilitado,
        cambia la pantalla actual a la principal ("main") con una transición hacia la derecha.
        """
        if self.collide_point(*touch.pos) and not Disable.value:
            CurrentScreen.screen = 0
            transition("main", 0.5, "right")
            
class CommandAdventure(BoxLayout):
    """
    Contenedor que agrupa los botones relacionados con la gestión de aventuras:
    - ListAdventures: Para ver la lista de eventos.
    - AdventureButton: Para crear una nueva aventura.
    """
    def __init__(self):
        super().__init__()
        self.status = False
        self.add_widget(ListAdventures())
        self.add_widget(AdventureButton())

class ListAdventures(ButtonBehavior, Image):
    """
    Botón que navega a la pantalla de lista de eventos en ejecución.
    """
    def __init__(self):
        super().__init__()
        self.source = "assets/listAdventure.png"
        setup_hover(self, 1)

    hovered = False

    def on_touch_down(self, touch):
        """
        Al presionar, actualiza la lista de eventos en ejecución y cambia
        a la pantalla de eventos ("events"). Guarda el estado anterior para poder volver.
        """
        if self.collide_point(*touch.pos):
            apps = appList()
            apps.events.scrollList.running.update()

            screenParent = appList().screenParent
            CurrentScreen.before = (CurrentScreen.screen, screenParent.current)
            CurrentScreen.screen = 2
            transition("events", 0.5, "down")

class AdventureButton(ButtonBehavior, Image):
    """
    Botón que inicia el proceso de creación de una nueva aventura.
    """
    def __init__(self):
        super().__init__()
        self.source = "assets/adventure.png"
        setup_hover(self, 1)

    hovered = False

    def on_touch_down(self, touch):
        """
        Al presionar, llama a la función `create_adventure` del núcleo
        para validar y procesar la creación del evento configurado.
        """
        if self.collide_point(*touch.pos) and not Disable.value:
            create_adventure()
