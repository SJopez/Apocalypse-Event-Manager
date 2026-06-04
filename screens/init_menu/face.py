from modules.modules import *
from modules.utilities import *

from screens.init_menu.file_selector import on_press

def on_start(start, touch):
    """
    Maneja el evento de inicio de la aplicación.
    Transiciona a la pantalla principal si el botón de inicio es presionado.
    """
    if start.collide_point(*touch.pos) and not Disable.value:
        screenParent = appList().screenParent
        menu = appList().menu
        nameLabel =  join_child(menu, "PlayerLayout").ids.inputName
        name = appList().mainMenu.name.ids.nameValue
        nameLabel.text = name.text
        CurrentScreen.screen = 0
        transition("main", 0.5, "left")
        screenParent.transition = SlideTransition(duration=0.5, direction="right")

def close_program(exit, touch):
    """
    Cierra la aplicación y limpia archivos temporales JSON.
    """
    if exit.collide_point(*touch.pos):
        cleanJSON()
        App.get_running_app().stop()

class Option(ButtonBehavior, Image):
    """
    Opción del menú principal (Start, Load, Save, Exit).
    Maneja animaciones de entrada y eventos de clic.
    """
    def __init__(self, src, delay):
        super().__init__()
        self.opacity = 0
        self.source = f"assets/{src}"
        InitAnimation(self, delay)
        setup_hover(self, 3, 0.8)

        if src == "start.png":
            self.on_touch_down = lambda touch: on_start(self, touch)
        if src == "load.png":
            self.on_touch_down = lambda touch: on_press(self, touch, "load")
        if src == "save.png":
            self.on_touch_down = lambda touch: on_press(self, touch, "save")
        if src == "exit.png":
            self.on_touch_down = lambda touch: close_program(self, touch)

    hovered = False

def InitAnimation(widget, delay):
    """
    Inicia la animación de aparición de los botones del menú.
    """
    anima = Animation(opacity=1, duration=0.75)
    delay = Animation(opacity=0, duration=delay)
    seq = delay + anima
    seq.start(widget)

class NameInput(TextInput):
    """
    Campo de entrada para el nombre del usuario.
    Limita la longitud del texto a 16 caracteres.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        setup_hover(self, 3, cursor="ibeam")

    def keyboard_on_textinput(self, window, text): 
        if len(self.text) < 16:
            self.text += text

class NameContainer(BoxLayout):
    """
    Contenedor para el campo de entrada del nombre.
    """
    def __init__(self):
        super().__init__()
        
class Menu(BoxLayout):
    """
    Contenedor del menú principal con las opciones.
    """
    def __init__(self):
        super().__init__()
        self.add_widget(Option("start.png", 0.25))
        self.add_widget(Option("load.png", 0.45))
        self.add_widget(Option("save.png", 0.65))
        self.add_widget(Option("exit.png", 0.85))
        self.add_widget(Label(
            size_hint_y = None,
            height = 25
        ))

class Container(FloatLayout):
    """
    Contenedor principal de la pantalla del menú.
    Incluye el fondo, el menú y el campo de nombre.
    """
    def __init__(self):
        super().__init__()
        self.background = Image(source="assets/background_face.png")
        self.add_widget(self.background)
        self.add_widget(Menu())
        self.name = NameContainer()
        self.add_widget(self.name)

    fileSelector = None

Builder.load_file("screens/init_menu/styles/face.kv")