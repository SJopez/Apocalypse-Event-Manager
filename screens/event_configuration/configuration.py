from modules.modules import *
from screens.event_configuration.widgets.resource_widgets import ResourcesLayoutP, ResourceInfoLayoutP, ResourceP
# from modules import *
from core.event_manager import *
from modules.ui_utils import *
from modules.utilities import *
from screens.event_configuration.widgets.editable_event import *
from screens.event_configuration.widgets.configuration_widgets import *
from screens.event_configuration.widgets.configuration_buttons import *
from kivymd.uix.pickers import MDTimePickerDialHorizontal
from datetime import time

class NeedResources(StackLayout):
    """
    Contenedor para mostrar los recursos necesarios para un evento.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.padding = (30, 0, 30, 0)

class AddNeedButton(Button):
    """
    Botón que añade automáticamente los recursos necesarios del evento actual
    a la lista de recursos seleccionados por el usuario.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        setup_hover(self, 1, scroll=True)
    
    hovered = False

    def on_touch_down(self, touch):
        """
        Al presionar, lee los requisitos del evento actual y añade los recursos faltantes
        a la selección del usuario, actualizando la vista.
        """
        if self.collide_point(*touch.pos) and not Disable.value:
            e = Manage.get_one(self.parent.current)
            setEvent(e)
            
            for x in e["necesita"]:
                recurso = get_one(x)
                data = readJson("data/dynamic/selected_resources_event.json")
                ignore = False

                # Evitar duplicados
                for i in data:
                    if i["id"] == recurso["id"]:
                        ignore = True             

                if ignore: continue

                data.append(recurso)
                writeJson("data/dynamic/selected_resources_event.json", data)
        
            # Actualizar la lista visual de recursos
            child = join_child(appList().mycon, "ResourceListP")
            child.update("data/dynamic/selected_resources_event.json")
        
    hovered = False      

class TimePicker(MDTimePickerDialHorizontal):
    """
    Widget de tipo reloj para eleccion de hora
    """
    def __init__(self, button, **kwargs):
        super().__init__(**kwargs)

        self.button = button
        title = join_child(self, "MDLabel")
        title.text = "Seleccione la hora"
        container = join_child(self, "MDTimePickerButtonsContainer")
        container.children[0].children[0].text = "Aceptar"
        container.children[1].children[0].text = "Cancelar"

    #Activa el fondo al remover el widget
    def on_dismiss(self, *args):
        main = appList().mycon
        backgroundManager(main, True, sum=0)
    
    #Remover al pulsar Cancelar
    def on_cancel(self, *args):
        self.dismiss()
    
    #Envia la informacion al padre para guardarla y procesarla y remueve el widget
    def on_ok(self, *args):
        main = appList().mycon
        parent = join_child(main, "EventInfo")
        
        t = [self.time.hour, self.time.minute]
        
        if self.button.type:
            parent.updateHourIni(t)
        else:
            parent.updateHourEnd(t)

        self.dismiss()

class TimePickerButton(Button):
    """
    Clase para los botones que abren el TimePicker
    """
    def __init__(self, type, **kwargs):
        super().__init__(**kwargs)
        self.value = None
        self.type = type

    #Abre el TimePicker al pulsar y desactiva el fondo
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            main = appList().mycon
            backgroundManager(main, False, sum=0)
            clock = TimePicker(self)
            clock.open()

class TimePickerButtonIni(TimePickerButton):
    """
    Boton para elegir la hora de inicio
    """
    def __init__(self, **kwargs):
        super().__init__(True, **kwargs)
        setup_hover(self, 1, scroll=True)
    
    hovered = False
    
class TimePickerButtonEnd(TimePickerButton):
    """
    Boton para elegir la hora de fin
    """
    def __init__(self, **kwargs):
        super().__init__(False, **kwargs)
        setup_hover(self, 1, scroll=True)
    
    hovered = False

def parse(value):
    """
    Pone ceros delante si es necesario para mejorar la visualizacion
    """
    if value[0] < 10:
        value[0] = "0" + str(value[0])
    if value[1] < 10:
        value[1] = "0" + str(value[1])

    return str(value[0]) + ":" + str(value[1])

class EventInfo(BoxLayout):
    """
    Panel principal que muestra la información detallada del evento seleccionado.
    Maneja tanto la visualización de eventos predefinidos como el formulario de eventos personalizados.
    """
    def __init__(self):
        super().__init__()
        self.orientation = "vertical"
        self.need = self.ids.need
        self.dateIni = self.ids.dateini
        self.dateEnd = self.ids.datend
        self.hourIni = self.ids.hourini
        self.hourEnd = self.ids.hourend
        self.time = [time(0, 0), time(0, 0)]
        self.current = 0
        self.childs = []
        self.editable = None

    img = StringProperty("")
    type = StringProperty("")
    danger = StringProperty("")
    danger_color = ListProperty([0, 0, 0, 0])
    place = StringProperty("")

    danger_words = {
        1: "Pan comido",
        2: "Vigila tus espaldas",
        3: "Huele a peligro",
        4: "Sal corriendo",
        5: "Muerte segura"
    }

    def update(self, i):
        """
        Actualiza la vista con la información del evento seleccionado (índice i).
        Si i es -1, cambia al modo de edición para crear un evento personalizado.
        """
        e = Manage.get_one(i)

        # Restaurar widgets originales si se vuelve de modo edición
        if self.current == -1:
            for child in self.childs:
                self.add_widget(child)

        self.current = i

        # Limpiar lista de recursos necesarios
        for x in list(self.need.children):
            self.need.remove_widget(x)
   
        if i == -1:
            # Modo edición: Crear el formulario de evento personalizado
            createEditableAdventure(self)
            setEvent(e, True)
        else:
            # Modo visualización: Mostrar datos del evento predefinido
            setEvent(e)
            if self.editable != None:
                self.remove_widget(self.editable)
                self.editable = None

            # Mostrar recursos necesarios
            for x in e["necesita"]:
                resource = ResourceP(x, False, False)
                resource.my_color = [0.5, 0.5, 0.5, 1]
                resource.icon.size = (50, 50)
                resource.on_move = None
                resource.on_touch_down = lambda x: None
                self.need.add_widget(resource)

            # Ajustar altura y textos
            self.need.height = ((len(e["necesita"]) // 6) + (1 and (len(e["necesita"]) % 6 != 0))) * 65
            self.ids.description.text = e["descripcion"]
            self.img = f"assets/event_images/{i + 1}.png"
            self.type = ""
            
            for i in e["tipo"]:
                if i == "Defensa":
                    self.type += "• ⛨ Defensa \n"
                if i == "Refugio":
                    self.type += "• 🏠Refugio \n"
                if i == "Supervivencia":
                    self.type += "• 🏕️ Supervivencia \n"

            dg = e["peligro"]
            self.danger = "-" + danger_words[dg] + "-"
            self.danger_color = dg_colors[dg]
            self.place = "• " + e["ubicacion"]
            self.height = 500 + self.need.height + HeightDescription[e["id"]] + 75
    
    def updateHourIni(self, value):
        """
        Actualiza la hora de inicio en el widget correspondiente.
        """
        self.time[0] = time(value[0], value[1])
        value = parse(value)

        if self.editable != None:
            self.editable.hourIni.text = value
        else:
            self.hourIni.text = value

    def updateHourEnd(self, value):
        """
        Actualiza la fecha de fin en el widget correspondiente. 
        """
        self.time[1] = time(value[0], value[1])
        value = parse(value)
        
        if self.editable != None:
            self.editable.hourEnd.text = value
        else:
            self.hourEnd.text = value

    def updateIni(self, value):
        """
        Actualiza la fecha de inicio en el widget correspondiente.
        """
        if self.editable != None:
            self.editable.dateIni.text = value
        else:
            self.dateIni.text = value

    def updateEnd(self, value):
        """
        Actualiza la fecha de fin en el widget correspondiente.
        """
        if self.editable != None:
            self.editable.dateEnd.text = value
        else:
            self.dateEnd.text = value

class ScrollEventInfo(ScrollView):
    """
    Contenedor con desplazamiento para la información del evento.
    """
    def __init__(self):
        super().__init__()
        self.evinfo = EventInfo()
        self.add_widget(self.evinfo)
       
class EventHandler(BoxLayout):
    """
    Manejador principal de la sección de eventos.
    Combina el selector de eventos (SelectorCaller) y la vista de información (ScrollEventInfo).
    """
    def __init__(self):
        super().__init__()
        self.scevinfo = ScrollEventInfo()
        self.scevinfo.evinfo.update(0)
        self.selcal = SelectorCaller()
        self.selcal.selector = Selector(self.selcal, self.scevinfo.evinfo)
        self.selcal.set_bind()
        self.add_widget(self.selcal, index=0)
        self.add_widget(self.scevinfo, index=0)
        
class ConfiEvent(BoxLayout):
    """
    Layout que divide la pantalla de configuración en dos:
    - Izquierda: Información y selección del evento (EventHandler).
    - Derecha: Selección de recursos (ResourcesLayoutP).
    """
    def __init__(self):
        super().__init__()
        self.eventHandler = EventHandler()
        self.add_widget(self.eventHandler)
        self.layo = ResourcesLayoutP()
        self.add_widget(self.layo)

class MainConfig(FloatLayout):
    """
    Pantalla principal de configuración de eventos.
    Estructura general que incluye fondo, botón de retroceso, panel de configuración
    y botones de acción (crear aventura).
    """
    def __init__(self):
        super().__init__()
        self.hole = None
        self.color = None
        self.fileSelector = None
        self.img = Image(source="assets/background_config.png")
        self.add_widget(self.img)
        self.backbutton = Backbutton()
        self.add_widget(self.backbutton)
        self.cefi = ConfiEvent()
        self.add_widget(self.cefi)
        self.reso = ResourceInfoLayoutP()
        self.layo = self.cefi.layo
        self.add_widget(self.reso)
        self.command = FloatContainer(CommandAdventure())
        self.add_widget(self.command)

