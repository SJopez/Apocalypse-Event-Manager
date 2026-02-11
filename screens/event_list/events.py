from modules.modules import *
from modules.utilities import *
from screens.event_list.graphic.plot import createGraph, plt
from core.event_manager import *
from kivy.graphics import Color, Mesh, Triangle
from kivy.utils import get_color_from_hex

class EventName(Label):
    """
    Etiqueta para mostrar el nombre del evento en la lista.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
       
    textName = StringProperty("")

class Ini(Label):
    """
    Etiqueta para mostrar la fecha/hora de inicio del evento.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    ini = StringProperty("")

class End(Label):
    """
    Etiqueta para mostrar la fecha/hora de fin del evento.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    end = StringProperty("")

class EventNum(Label):
    """
    Etiqueta para mostrar el número identificador del evento.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    enum = StringProperty("")

class DeleteButton(ButtonBehavior, Image):
    """
    Botón para eliminar un evento de la lista de eventos en ejecución.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        setup_hover(self, 2, src="assets/deleteEventIcon.png", default="assets/deleteIcon.png", scroll=True)
    
    hovered = False

    def on_touch_down(self, touch):
        """
        Maneja la eliminación del evento al hacer clic.
        Actualiza el archivo JSON y la interfaz gráfica.
        """
        if self.collide_point(*touch.pos) and not Disable.value:
            event = self.parent.parent.parent
            running = appList().events.scrollList.running
            running.remove_widget(event)
            runningEventJson = readJson("data/dynamic/running_events.json")
            runningEventJson.remove(event.eventJson)
            writeJson("data/dynamic/running_events.json", runningEventJson)
            resizeList(running)


class ShowEventWIndow(BoxLayout):
    """
    Ventana emergente que muestra los detalles completos de un evento seleccionado.
    """
    def __init__(self):
        super().__init__()
        
    name = StringProperty("")
    description = StringProperty("")
    dateini = StringProperty("")
    datend = StringProperty("")
    img = StringProperty("")
    danger = StringProperty("")
    place = StringProperty("")
    dg_color = ListProperty([0, 0, 0, 0])
    eventNum = StringProperty("")
    color = ListProperty([1, 1, 1, 1])

    def update(self, event):
        """
        Actualiza los datos mostrados en la ventana con la información del evento.
        Carga recursos, imágen, textos de horario y colores de peligro.
        """
        self.name = event["titulo"]
        self.description = event["descripcion"]
        
        if type(event["eventID"]) != int:
            self.color = event["eventID"]
        else:
            self.color = get_color_from_hex(colors[event["eventID"] - 1])
            
        # Seccion de recursos
        from screens.event_configuration.widgets.resource_widgets import ResourceP

        parent = self.ids.need
        parent.height = ((len(event["necesita"]) // 6) + (1 and (len(event["necesita"]) % 6 != 0))) * 65
        
        deleteAll(parent)

        for r in event["recursos"]:
            resource = ResourceP(r, True, False)
            resource.cuantity.text = str(event["recursos"][r])
            resource.my_color = [0.5, 0.5, 0.5, 1]
            resource.icon.size = (50, 50)
            resource.on_move = None
            resource.on_touch_down = lambda x: None
            parent.add_widget(resource)

        self.dateini = parseDate(event["fechaInicio"]) + " - " + parseHour(event["tiempoInicio"])
        self.datend = parseDate(event["fechaFin"]) + " - " + parseHour(event["tiempoFin"])
        self.eventNum = str(event["eventNum"])

        self.img = event["imagen"]
        container = self.ids.typeContainer

        deleteAll(container)

        # Información de tipo de evento, peligro y ubicación
        for tp in event["tipo"]:
            icon = Image(source=f"assets/{tp}.png", size=(50, 50))
            container.add_widget(icon)
        
        self.danger = danger_words[event["peligro"]]
        self.dg_color = dg_colors[event["peligro"]]
        self.place = event["ubicacion"]

    def on_touch_down(self, touch):
        """
        Cierra la ventana de detalles si se hace clic fuera de ella.
        Restaura la interactividad de la lista principal.
        """
        if self.collide_point(*touch.pos) and Disable.value:
            pass
        elif Disable.value:
            main = appList().events
            windowAnimation(self, main, x=-850, opacity=1)
            Disable.value = False
            main.scrollList.do_scroll = True
            Window.set_system_cursor("arrow")
        

def config(widget, special, opacity, parent):
    """
    Ajusta la opacidad de los widgets hijos para crear efecto de foco.
    Si la opacidad es baja (ventana abierta), actualiza el contenido de la ventana.
    """
    for child in widget.children:
        if child != special and type(child).__name__ != "Zombie":
            child.opacity = opacity
    
    if opacity == 0.6:
        special.update(parent.eventJson)

def windowAnimation(widget, main, parent=None, x=215, opacity=0.6):
    """
    Anima la entrada/salida de la ventana de detalles del evento.
    """
    anima = Animation(x=x, duration=0.3, t='out_quad')
    config(main, widget, opacity, parent)
    anima.start(widget)

class ShowEventButton(ButtonBehavior, Image):
    """
    Botón dentro de un evento en la lista para abrir sus detalles.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        setup_hover(self, 2, src="assets/openEventIcon.png", default="assets/openIcon.png", scroll=True)
    
    hovered = False

    def on_touch_down(self, touch):
        """
        Abre la ventana de detalles del evento al hacer clic.
        Deshabilita el scroll de la lista principal.
        """
        if self.collide_point(*touch.pos) and not Disable.value:
            main = appList().events
            window = main.window
            Disable.value = True
            main.scrollList.do_scroll = False
            Window.set_system_cursor("arrow")
            windowAnimation(window, main, parent=self.parent.parent.parent)
            

def parseDate(date):
    """Convierte una lista [D, M, Y] a string 'D/M/Y'."""
    day, month, year = date[0], date[1], date[2]
    return day + "/" + month + "/" + year

def parseHour(hour):
    """Convierte una lista [H, M] a string 'HH:MM'."""
    hour, minute = str(hour[0]), str(hour[1])
    hour = "0" + hour if len(hour) == 1 else hour
    minute = "0" + minute if len(minute) == 1 else minute
    return hour + ":" + minute

def hasChild(parent, child):
    """Verifica si un evento ya existe en la lista visual."""
    for c in parent.children:
        if c.isEvent and c.id == child.id:
            return True
    return False

class Zombie(Image):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

def resizeList(parent, value=None):
    """
    Recalcula y ajusta la altura del contenedor de la lista de eventos
    para asegurar que el scroll funcione correctamente.
    """
    childCount = len(readJson("data/dynamic/running_events.json")) if value == None else value
    childCount += 4 if childCount % 4 != 0 else 0
    childCount -= (childCount % 4)
    parent.height = (childCount / 4) * 480 + (childCount / 4) * 20 + 170

    if childCount == 0:
        events = appList().events 
        
        if events.zombie != None:
            events.zombie.opacity = 1
        else:
            events.zombie = Zombie()
            events.add_widget(events.zombie)
    else:
        events = appList().events 
        
        if events.zombie != None:
            events.zombie.opacity = 0
        else:
            print("mojon")
            events.zombie = Zombie()
            events.zombie.opacity = 0
            events.add_widget(events.zombie)
        
        

class JoinEvent(TextInput):
    """
    Campo de búsqueda para filtrar eventos por nombre.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        setup_hover(self, 2, 1, cursor='ibeam')
    
    hovered = False
    delete = []

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        """
        Maneja el borrado de caracteres (Backspace).
        Restaura eventos previamente ocultos si coinciden con el nuevo texto de búsqueda.
        """
        if keycode[0] == 8 and not Disable.value:
            running = appList().events.scrollList.running
            self.text = self.text[:-1]
            
            toDelete = []
            for child in self.delete:
                title = child.eventJson["titulo"]
                searchText = self.text
                title, searchText = title.lower(), searchText.lower()

                if title.find(searchText) != -1: 
                    running.add_widget(child)
                else:
                    toDelete.append(child)
                
                self.delete = toDelete

            resizeList(running, len(running.children))

    def keyboard_on_textinput(self, window, text):
        """
        Maneja la entrada de texto para filtrar la lista de eventos.
        Oculta los eventos que no coinciden con el texto ingresado.
        """
        if len(self.text) == 24 or Disable.value: return

        self.text += text
        running = appList().events.scrollList.running

        for child in running.children:
            if not child.isEvent:
                continue

            title = child.eventJson["titulo"]
            searchText = self.text
            title, searchText = title.lower(), searchText.lower()


            if title.find(searchText) == -1:
                self.delete.append(child)

        for child in self.delete:
            deleteChild(running, child)
        
        resizeList(running, len(running.children))

class RunningEvent(BoxLayout):
    """
    Representación visual de un evento individual en la lista.
    Contiene imagen, nombre, fechas y número de evento.
    """
    def __init__(self, event):
        super().__init__()
        self.id = event["id"]
        self.image = self.ids.image
        self.eventName = self.ids.inputName
        self.timeIni = self.ids.timeIni
        self.timeEnd = self.ids.timeEnd
        self.eventNum = self.ids.eventNum
        self.eventJson = event
        self.isEvent = True
        self.assign(event)

    def assign(self, event):
        """Asigna los valores del evento a los widgets correspondientes."""
        self.eventName.textName = event["titulo"]
        self.image.source = event["imagen"]
        self.timeIni.ini = parseDate(event["fechaInicio"]) + " - " + parseHour(event["tiempoInicio"])
        self.timeEnd.end = parseDate(event["fechaFin"]) + " - " + parseHour(event["tiempoFin"])
        self.eventNum.enum = str(event["eventNum"])

class ScrollEventList(ScrollView):
    """
    Contenedor con scroll para la lista de eventos.
    """
    def __init__(self):
        super().__init__()
        self.running = RunningEventList()
        self.add_widget(self.running)

class RunningEventList(StackLayout):
    """
    Layout que organiza los eventos en ejecución.
    Carga los eventos desde el archivo JSON al iniciarse.
    """
    def __init__(self):
        super().__init__()
        self.vis = False
        value = readJson("data/dynamic/running_events.json")
        self.update(True, value)

    def update(self, load=False, value=None):
        """
        Actualiza la lista de eventos.
        Si load=True, intenta cargar y crear los widgets para cada evento.
        Maneja errores de carga restaurando el estado anterior si es necesario.
        """
        if load:
            running = readJson("data/dynamic/running_events.json")
            writeJson("data/dynamic/running_events.json", [])
            
            flag = True
            for event in value:
                if not flag:
                    break
                try:
                    flag = createEvent(event)[0]
                except:
                    flag = False

            if flag:
               deleteAll(self)
               writeJson("data/dynamic/running_events.json", value)
               for e in value:
                   self.add_widget(RunningEvent(e))
            else:
                writeJson("data/dynamic/running_events.json", running)
                
            return flag
        
        resizeList(self)
 
class Search(Image):
    """
    Icono decorativo para la barra de búsqueda.
    """
    def __init__(self):
        super().__init__()
        self.size_hint = (None, None)
        self.pos = (285, 598)
        self.source = "assets/search.png"

class Sort(Image):
    """
    Botón para ordenar la lista de eventos.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (40, 40)
        self.pos = (360, 627)
        self.source = "assets/sort.png"
        setup_hover(self, 2)

    hovered = False

    def on_touch_down(self, touch):
        """Ordena los eventos por su numero al hacer clic."""
        if self.collide_point(*touch.pos) and not Disable.value:
            from modules.ui_utils import sortEvents
            root = self.parent
            eventList = join_child(root, "RunningEventList")
            sortEvents(eventList)

class Graphic(Image):
    """
    Botón para abrir la visualización gráfica de los eventos.
    """
    def __init__(self):
        super().__init__()
        self.size_hint = (None, None)
        self.size = (40, 40)
        self.pos = (1165, 620)
        self.source = "assets/graphic.png"
        setup_hover(self, 2)

    hovered = False

    def on_touch_down(self, touch):
        """Genera y muestra el gráfico."""
        if self.collide_point(*touch.pos) and not Disable.value:
            createGraph()
            plt.show()

class Back(Image):
    """
    Botón para regresar a la pantalla anterior.
    """
    def __init__(self):
        super().__init__()
        self.size_hint = (None, None)
        self.size = (40, 40)
        self.pos = (1205, 620)
        self.source = "assets/back.png" 
        setup_hover(self, 2)

    hovered = False   

    def on_touch_down(self, touch):
        """Gestiona la transición de regreso a la pantalla anterior."""
        if self.collide_point(*touch.pos) and not Disable.value:
            infoScreen = CurrentScreen.before
            screenParent = appList().screenParent
            CurrentScreen.screen = infoScreen[0]
            transition(infoScreen[1], 0.5, "up")
            
            if infoScreen[1] == "main":
                screenParent.transition = SlideTransition(duration=0.5, direction="left")
            else:
                screenParent.transition = SlideTransition(duration=0.5, direction="right")

class Header(BoxLayout):
    """
    Encabezado de la lista de eventos (definido visualmente en el KV).
    """
    def __init__(self):
        super().__init__()

class MainEventContainter(FloatLayout):
    """
    Contenedor principal de la pantalla de lista de eventos.
    Agrupa el fondo, la lista, la barra de búsqueda y los botones de control.
    """
    def __init__(self):
        super().__init__()
        self.zombie = None
        self.background = Image(source="assets/background_events.png")
        self.background.opacity = 0.7
        self.add_widget(self.background)
        self.add_widget(Header())
        self.scrollList = ScrollEventList()
        self.add_widget(self.scrollList)
        self.search = Search()
        self.add_widget(self.search)
        self.sort = Sort()
        self.add_widget(self.sort)
        self.graphic = Graphic()
        self.add_widget(self.graphic)
        self.back = Back()
        self.add_widget(self.back)
        self.window = ShowEventWIndow()
        self.add_widget(self.window)

Builder.load_file("screens/event_list/styles/events.kv")