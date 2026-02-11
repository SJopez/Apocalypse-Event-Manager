from modules.modules import *
from modules.utilities import * 

# Carga el archivo KV con los estilos para las utilidades de UI
Builder.load_file("modules/styles/ui_utils.kv")

def sortEvents(eventList):
    """
    Ordena la lista de eventos en ejecución basándose en su número de evento (eventNum).
    Actualiza la lista visual de eventos.
    """
    running = readJson("data/dynamic/running_events.json")
    pairList = []

    for e in running:
        pairList.append([e["eventNum"], e])

    pairList.sort(key=lambda item: item[0])
    ordered = [x[1] for x in pairList]
    eventList.update(True, ordered)

def AppearAnimation(parent):
    anima = Animation(opacity=1, duration=0.5)
    anima.start(parent)

def DisolveAnimation(parent, widget, duration, opacity, delay, flag=False):
    """
    Aplica una animación de disolución (cambio de opacidad) a un widget.
    Al finalizar, llama a CompleteAnimation para limpiar.
    """
    animaDelay = Animation(duration=delay)
    anima = Animation(opacity=opacity, duration=duration)
    sequence = animaDelay + anima
    sequence.on_complete = lambda widget: CompleteAnimation(parent, widget, flag) 
    sequence.start(widget)

def CompleteAnimation(parent, widget, flag):
    """
    Callback ejecutado al finalizar la animación de disolución.
    Elimina el widget del padre y resetea el contador de éxito si es necesario.
    """
    deleteChild(parent, widget)
    Success.value = 0

def showMessage(classMessage, name, title, body, position, alter=None, short=False):
    """
    Muestra un mensaje emergente (Popup o similar) en la interfaz.
    Maneja la posición para apilar mensajes si hay múltiples.
    """
    mainConfig = appList().mycon if alter == None else alter

    if mainConfig.children[0].__class__.__name__ == name and name != "Message":
        deleteChild(mainConfig, mainConfig.children[0])
    elif mainConfig.children[0].__class__.__name__ == name:
        position = (position[0], position[1] + Success.value * 95)
    
    Success.value += (name == "Message")

    message = classMessage(title, body)

    if short:
        message.height = 140
  
    message.opacity = 1
    message.pos = position
    mainConfig.add_widget(message)
    DisolveAnimation(mainConfig, message, 4, 0, 2, name == "Message") 

def showAnimation(parent, y_val):
    """
    Anima la posición Y de un widget (usado para mostrar/ocultar paneles).
    """
    anima1 = Animation(x=0, y=y_val, duration=0.4, t='out_quad')
    anima1.start(parent)
    
def configShowAnimation(parent, pos):
    """
    Controla la animación de mostrar/ocultar el panel de comandos basado en la posición del mouse.
    """
    command = parent.command
    c1 = command.children[0]
    c2 = command.children[1]

    if c1.collide_point(*pos) or c2.collide_point(*pos):
        if not command.status:
            showAnimation(command, 100)
            command.status = True
    elif command.status:
        showAnimation(command, 0)
        command.status = False  

class Error(Popup):
    """
    Popup personalizado para mostrar errores.
    """
    def __init__(self, title, text):
        super().__init__()
        self.title = title
        self.title_size = 24
        self.size_hint = (None, None)
        self.size = (400, 190)
        child = join_child(self.children[0].children[0], "Label")
        child.text = text
    
    def on_touch_down(self, touch):
        self.dismiss = True

class Message(Error):
    """
    Variante de Error para mensajes informativos (notificaciones).
    Más pequeño y con título más chico.
    """
    def __init__(self, title, text):
        super().__init__(title, text)
        self.size_hint = (None, None)
        self.size = (400, 100)
        self.title_size = 22

class ButtonSet(BoxLayout):
    """
    Conjunto de botones (Aceptar/Cancelar) para diálogos de confirmación.
    """
    def __init__(self, info, realTime):
        super().__init__()
        self.add_widget(DeniedJoinHole())
        self.add_widget(AceptJoinHole(info, realTime))

def errorHover(widget, pos):
    """
    Maneja el efecto hover (cambio de opacidad y cursor) para los botones de ButtonSet.
    """
    if Utils.errorHover:    
        if widget.collide_point(*pos):
            widget.hovered = True
            widget.opacity = 0.9
            Window.set_system_cursor('hand')

        elif not widget.collide_point(*pos) and widget.hovered:
            widget.hovered = False
            widget.opacity = 1
            Window.set_system_cursor('arrow')

class AceptJoinHole(Button):
    """
    Botón de 'Aceptar' en diálogo de confirmación.
    """
    def __init__(self, info, realTime):
        super().__init__()
        self.info = info
        self.realTime = realTime
        Utils.errorHover = True
        Window.bind(mouse_pos=lambda win, pos: errorHover(self, pos))
    
    hovered = False

    def on_touch_down(self, touch):
        # Al pulsarse envía la información previamente calculada a manageAdventure y confirma la creación del evento
        if self.collide_point(*touch.pos):
            Utils.errorHover = False
            
            from core.event_creation import manageAdventure
            manageAdventure(True, self.info, self.realTime)

class DeniedJoinHole(Button):
    """
    Botón de 'Cancelar' en diálogo de confirmación.
    """
    def __init__(self):
        super().__init__()
        Window.bind(mouse_pos=lambda win, pos: errorHover(self, pos))
    
    hovered = False
    
    def on_touch_down(self, touch):
        # Al pulsarse envía False a manageAdventure y cierra el diálogo de confirmación sin crear el evento
        if self.collide_point(*touch.pos):
            Utils.errorHover = False
            from core.event_creation import manageAdventure
            manageAdventure(False, None, None)

class TitleHole(Label):
    """
    Etiqueta para el título en diálogo de confirmación.
    """
    def __init__(self, content):
        super().__init__(text=content)

class BodyHole(Label):
    """
    Etiqueta para el cuerpo del mensaje en diálogo de confirmación.
    """
    def __init__(self, content):
        super().__init__(text=content)
            
class JoinHole(BoxLayout):
    """
    Contenedor principal para diálogo de confirmación (Título, Cuerpo, Botones).
    """
    def __init__(self, title, body, info, realTime):
        super().__init__()
        self.add_widget(TitleHole(title))
        self.add_widget(BodyHole(body))
        self.add_widget(ButtonSet(info, realTime))

def backgroundManager(main, flag, sum=0.6):
    """
    Funcion para activar/desactivar el fondo al cerrar/abrir mensajes emergentes
    """
    if flag:
        Disable.value = False
        Window.set_system_cursor('arrow')
        for child in main.children:
            child.opacity += sum
        scroll = join_child(main, "ScrollEventInfo")
        scroll.do_scroll = True
    else:
        Disable.value = True
        Window.set_system_cursor('arrow')
        for child in main.children:
            child.opacity -= sum
        scroll = join_child(main, "ScrollEventInfo")
        scroll.do_scroll = False

def calendar_removal(child):
    """
    Funcion de utilidad para remover el calendario cuando acaba la animacion
    """
    if Disable.value:
        main = appList().mycon
        main.remove_widget(child)
        backgroundManager(main, True, sum=0.4)

def AppearAnimation(parent):
    """
    Animacion de tipo fade-in que hace aparecer el calendario
    """
    parent.opacity = 0
    anima = Animation(duration=0.3, opacity=1)
    anima.start(parent)

def Disappear(parent):
    """
    Animacion de tipo fade-out que hace desaparecer el calendario
    """
    anima = Animation(duration=0.3, opacity=0)
    anima.on_complete = lambda parent: calendar_removal(parent)
    anima.start(parent)

#Importa la clase Error hacia el archivo.kv
Factory.register('Error', Error)