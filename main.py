# Configuración inicial de la ventana (tamaño fijo, no redimensionable)
from kivy.config import Config
Config.set('graphics', 'resizable', '0')
Config.set('graphics', 'width', '1280')
Config.set('graphics', 'height', '768')
Config.set('input', 'mouse', 'mouse,disable_multitouch')
from screens.event_configuration.configuration import MainConfig
from screens.event_configuration.widgets.configuration_widgets import FloatContainer
from screens.event_configuration.widgets.configuration_buttons import Backbutton, CommandAdventure, ListAdventures
from modules.utilities import *
from screens.event_list.events import MainEventContainter
from screens.init_menu.face import Container
from modules.modules import *
from kivymd.app import MDApp

class PlayerLayout(BoxLayout):
    """
    Layout para la información del jugador (imagen y nombre) en la pantalla de selección de recursos.
    """
    def __init__(self):
        super().__init__()

class Resource(FloatLayout):
    """
    Representa un recurso individual seleccionable en la interfaz.
    Maneja la selección, hover y visualización de información detallada.
    """
    def __init__(self, item):
        super().__init__()
        self.icon = Image(source=f"assets/{item}.png")
        self.icon.size_hint = (None, None)
        self.icon.size = (60, 60)
        self.icon.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
        self.add_widget(self.icon)
        self.selected = 0
        self.id = item
        Window.bind(mouse_pos=self.on_move)
        setup_hover(self, 0, 0.8)
    
    hovered = False

    def on_move(self, win, pos):
        """
        Maneja el evento de movimiento del mouse para mostrar información del recurso al hacer hover.
        Solo activo si la pantalla actual es la de selección de recursos (CurrentScreen.screen == 0).
        """
        if CurrentScreen.screen != 0:
            return
            
        resource = get_one(self.id)
        info = appList().menu.rInfo

        if self.collide_point(*pos):
            # Actualiza el panel de información con los datos del recurso
            info.img_source = f"assets/{self.id}.png"
            info.name = resource["nombre"]
            info.cuantity = str(resource["cantidad"])
            info.description = resource["descripcion"]
            info.complementary = resource["complementario"][0]

            infotype = ""

            for i in range(len(resource["tipo"])):
                infotype += resource["tipo"][i]

                if i < len(resource["tipo"]) - 1:
                    infotype += ", "

            info.type = infotype
            
            comp = ""
            
            for i in range(len(resource["complementario"])):
                comp += resource["complementario"][i]

                if i < len(resource["complementario"]) - 1:
                    comp += ", "

            info.complementary = comp
            info.exclude = resource["excluyente"][0]  
            info.opacity = 1
        else:
            if self.hovered:
                info.opacity = 0

    my_color = ListProperty([0.1, 0.1, 0.1, 1])

    def add_resource(self):
        """
        Añade el recurso a la lista de recursos seleccionados (JSON).
        """
        recurso = get_one(self.id)
        data = readJson("data/dynamic/selected_resources.json")
        data.append(recurso)
        writeJson("data/dynamic/selected_resources.json", data)

    def quit_resource(self):
        """
        Elimina el recurso de la lista de recursos seleccionados (JSON).
        """
        recurso = get_one(self.id)
        data = readJson("data/dynamic/selected_resources.json")
        data.remove(recurso)
        writeJson("data/dynamic/selected_resources.json", data)

    def on_touch_down(self, touch):
        """
        Maneja la selección/deselección del recurso al hacer clic.
        """
        if CurrentScreen.screen != 0:
            return
        
        if self.collide_point(*touch.pos):
            if not self.selected:
                self.my_color = [0.8, 0.8, 0.8, 0.8]
                self.selected = 1
                self.opacity = 1
                self.add_resource()              
            else:
                self.my_color = [0.1, 0.1, 0.1, 1]
                self.selected = 0
                self.opacity = 0.8
                self.quit_resource()

class ResourceList(StackLayout):
    """
    Contenedor que lista todos los recursos disponibles (del 1 al 24).
    """
    def __init__(self):
        super().__init__()
        self.orientation = 'lr-tb'
        for i in range(1, 25):
            self.add_widget(Resource(i))

class ResourceInfoLayout(StackLayout):
    """
    Panel de información detallada del recurso seleccionado o bajo el cursor.
    Utiliza propiedades de Kivy para actualizar la UI automáticamente.
    """
    def __init__(self):
        super().__init__()
    
    screen = BooleanProperty(False)
    
    img_source = StringProperty("assets/1.png")
    name = StringProperty("")
    type = StringProperty("")
    cuantity = StringProperty("")
    description = StringProperty("")
    complementary = StringProperty("")
    exclude = StringProperty("")
   
class ResourcesLayout(BoxLayout):
    """
    Layout principal de la sección de recursos, combinando la lista y etiquetas.
    """
    def __init__(self):
        super().__init__()
        self.add_widget(ResourceList(), index=0)
        self.add_widget(Label(), index=0)
        
class ConfigEvent(BoxLayout):
    """
    Contenedor principal de la pantalla de configuración de eventos.
    Agrupa el layout del jugador y el de recursos.
    """
    def __init__(self):
        super().__init__()
        self.add_widget(PlayerLayout())
        self.add_widget(ResourcesLayout())
        
class ResourceMenu(FloatLayout):
    """
    Pantalla completa del menú de selección de recursos.
    Incluye fondo, botón de regreso, configuración central, panel lateral de información de recurso y panel inferior.
    """
    def __init__(self):
        super().__init__()
        self.background = Image(source="assets/background_main.png")
        self.add_widget(self.background)
        self.add_widget(BackButtonMain())
        self.add_widget(ConfigEvent())
        self.rInfo = ResourceInfoLayout()
        self.add_widget(self.rInfo)
        self.command = FloatContainer(CommandADventureMain())
        self.add_widget(self.command)
        

class CommandADventureMain(CommandAdventure):
    """
    Panel de inferior o de comandos, específico para la pantalla principal.
    Hereda de CommandAdventure pero personaliza los botones (quita algunos, añade avance).
    """
    def __init__(self):
        super().__init__()
        # Elimina botones por defecto no necesarios en esta vista
        self.remove_widget(self.children[0])
        self.remove_widget(self.children[0])
        self.add_widget(ListAdventuresMain())
        self.add_widget(ButtonAdvance())

class ListAdventuresMain(ListAdventures):
    """
    Botón para listar aventuras en la pantalla principal.
    """
    def __init__(self):
        super().__init__()
        setup_hover(self, 0)

class BackButtonMain(Backbutton):
    """
    Botón de regreso específico para la pantalla principal.
    Vuelve al menú de inicio.
    """
    def __init__(self):
        super().__init__()
        Window.unbind(mouse_pos=self.hover)
        setup_hover(self, 0)
        
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and not Disable.value:
            CurrentScreen.screen = 3
            transition("menu", 0.5, "right")
    
class ButtonAdvance(ButtonBehavior, Image):
    """
    Botón para avanzar a la siguiente fase (configuración del evento).
    Guarda los recursos seleccionados y transiciona de pantalla.
    """
    def __init__(self):
        super().__init__()
        setup_hover(self, 0)

    hovered = False

    def on_press(self):
        # Guarda la selección actual y prepara la siguiente pantalla
        data = readJson("data/dynamic/selected_resources.json")
        writeJson("data/dynamic/selected_resources_event.json", data)

        CurrentScreen.screen = 1
        appList().mycon.layo.rlist.update("data/dynamic/selected_resources.json")
        transition("config", 0.5, "left")
       
class ScreenChild(Screen):
    """
    Clase que representa las pantallas.
    """
    def __init__(self, nombre, contenido):
        super().__init__()
        self.name = nombre
        self.add_widget(contenido)

class ScreenParent(ScreenManager):
    """
    Gestor de pantallas principal de la aplicación.
    Contiene: Menú Inicio, Selección Recursos (Main), Configuración Evento, Lista Eventos.
    """
    def __init__(self, mainMenu, menu, mycon, events):
        super().__init__()
        self.add_widget(ScreenChild("menu", mainMenu))
        self.add_widget(ScreenChild("main", menu))
        self.add_widget(ScreenChild("config", mycon))
        self.add_widget(ScreenChild("events", events))

class Main(MDApp):
    """
    Clase principal de la aplicación
    Inicializa todas las pantallas y el gestor de navegación.
    """
    def build(self):
        self.mainMenu = Container()        
        self.mycon = MainConfig()
        self.menu = ResourceMenu()
        self.events = MainEventContainter()
        self.screenParent = ScreenParent(self.mainMenu, self.menu, self.mycon, self.events)
        self.theme_cls.theme_style = "Dark"
        return self.screenParent

# Detecta el cierre de la aplicación para limpiar archivos temporales JSON.
Window.bind(on_request_close=cleanJSON)

# Carga de los archivos KV necesarios para la interfaz.
Builder.load_file("screens/event_configuration/widgets/styles/calendar_widget.kv")    
Builder.load_file("screens/event_configuration/styles/configuration.kv")
Builder.load_file("screens/event_configuration/widgets/styles/resource_widgets.kv")

Main().run()