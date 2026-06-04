from modules.modules import *

# Conjunto para almacenar ubicaciones únicas de eventos
Places = set()

# Alturas predefinidas para descripciones (usado para ajustar correctamente las descripciones predefinidas)
HeightDescription = [0, 108, 130, 108, 86, 130, 108, 108, 86, 86, 130, 108, 130, 108, 130, 108, 108, 108, 108]

# Dimensiones de la ventana de la aplicación
WindowWidth, WindowHeight = 1280, 768

# Mapeo de niveles de peligro a descripciones textuales
danger_words = {
    1: "Pan comido",
    2: "Vigila tus espaldas",
    3: "Huele a peligro",
    4: "Sal corriendo",
    5: "Muerte segura"
}

# Mapeo inverso de descripciones a niveles de peligro
danger_words_inverse = {
    "Pan comido": 1,
    "Vigila tus espaldas": 2,
    "Huele a peligro": 3,
    "Sal corriendo": 4,
    "Muerte segura": 5
}

# Colores asociados a cada nivel de peligro (RGBA)
dg_colors = {
    1: [0.18,0.80,0.44,1], 
    2: [0.60,0.88,0.60,1],  
    3: [1.00,0.82,0.40,1],  
    4: [1.00,0.48,0.27,1],  
    5: [0.90,0.30,0.20,1]  
}

# Paleta de colores para la gráfica de eventos
colors = [
    "#4E79A7", "#F28E2B", "#E15759", "#76B7B2", "#59A14F",
    "#EDC948", "#B07AA1", "#FF9DA7", "#9C755F", "#BAB0AC",
    "#6A9FB5", "#F4A259", "#D95F02", "#66A61E", "#E6AB02",
    "#8E6C8A", "#17BECF", "#BCBD22", "#8A2BE3", "#2A9BE7"
]

def deleteAll(parent):
    """
    Elimina todos los widgets hijos de un widget padre.
    """
    while len(parent.children):
        parent.remove_widget(parent.children[0])

def getOneByName(name, src):
    """
    Busca un elemento por su nombre en un archivo JSON.
    Retorna el elemento si lo encuentra, o False si no.
    """
    with open(src, 'r') as file:
        for item in json.load(file):
            if item["nombre"] == name:
                return item
    return False

def readJson(src):
    """
    Lee y retorna el contenido de un archivo JSON.
    """
    with open(src, 'r') as file:
        return json.load(file)

def writeJson(src, value):
    """
    Escribe datos en un archivo JSON con indentación.
    """
    with open(src, 'w') as file:
        json.dump(value, file, indent=4)

def getPlaces():
    """
    Carga las ubicaciones únicas de los eventos estáticos en el conjunto Places.
    """
    events = readJson("data/static/events.json")

    if not len(Places):
        for event in events:
            Places.add(event["ubicacion"])

def addToJson(src, value):
    """
    Añade un nuevo elemento a una lista en un archivo JSON.
    """
    data = readJson(src)
    data.append(value)
    writeJson(src, data)

def findMex():
    """
    Encuentra el primer número de evento (ID) disponible en la secuencia.
    Útil para asignar IDs únicos a nuevos eventos.
    """
    running = readJson("data/dynamic/running_events.json")
    visited = {}

    for event in running:
        visited[event["eventNum"]] = True
    
    for i in range(1, len(running) + 1):
        vis = visited.get(i, False)

        if not vis:
            return i
    
    return len(running) + 1

def get_all():
    """
    Obtiene todos los recursos estáticos.
    """
    with open("data/static/resources.json") as file:
        return json.load(file)
    
def get_one(id):
    """
    Obtiene un recurso específico por su ID (ajustado por índice 0).
    """
    with open("data/static/resources.json") as file:
        return json.load(file)[id - 1]
    
def appList():
    """
    Retorna la instancia de la aplicación en ejecución.
    """
    return App.get_running_app()

class Success:
    """
    """
    value = 0

class finded:
    """
    Clase utilitaria para almacenar el resultado de búsquedas recursivas de widgets.
    """
    ans = 0

class Utils:
    """
    Clase contenedora de variables de estado globales y utilidades varias.
    """
    isSelected = False
    isDismiss = True
    spinner = False
    eventCounter = 1
    errorHover = False

class Disable:
    """
    Controla el estado de deshabilitación global de los eventos de hover y click en la interfaz
    Si es True entonces todos los eventos de hover y click deben estar desactivados.
    """
    value = False

class CurrentScreen:
    """
    Rastrea la pantalla actual y la anterior para la navegación.
    """
    screen = 3
    before = 0

class Manage:
    """
    Gestor de acceso a datos de eventos estáticos.
    """
    def get_all():
        with open("data/static/events.json") as file:
            return json.load(file)
        
    def get_one(id):
         with open("data/static/events.json") as file:
            return json.load(file)[id]

def join_child(child, joined):
    """
    Busca recursivamente un widget hijo por su nombre de clase.
    """
    if child.__class__.__name__ == joined:
        finded.ans = child
        return child

    for x in child.children:
        join_child(x, joined)

    if finded.ans != 0:
        return finded.ans

def deleteChild(parent, child):
    """
    Elimina un widget hijo de su padre.
    """
    parent.remove_widget(child)

def transition(target, duration, direction):
    """
    Realiza una transición de pantalla con animación.
    """
    Window.set_system_cursor("arrow")
    screenParent = appList().screenParent
    screenParent.transition = SlideTransition(duration=duration, direction=direction)
    screenParent.current = target

def cleanJSON(*args):
    """
    Limpia los archivos JSON temporales de recursos seleccionados.
    """
    writeJson("data/dynamic/selected_resources.json", [])
    writeJson("data/dynamic/selected_resources_event.json", [])

def on_hover(widget, pos, opacity, screen, src, default, cursor, scroll, dropdown):
    """
    Maneja la lógica de hover (pasar el mouse por encima) para widgets.
    Cambia el cursor, opacidad, imagen o color de fondo según corresponda.
    """
    if screen != CurrentScreen.screen or Disable.value:
        return
    
    if dropdown != None and Utils.isDismiss:
        return
  
    if not Utils.isDismiss and cursor == "ibeam":
        return

    if hasattr(widget, "selected") and widget.selected:
        opacity = 1
    
    pos = widget.to_widget(*pos) if scroll else pos
   
    if widget.collide_point(*pos):
        widget.hovered = True
        widget.opacity = opacity
        
        if cursor == None: 
            Window.set_system_cursor('hand')
        else: 
            Window.set_system_cursor(cursor)
        if src != None: 
            widget.source = src
        if dropdown != None:
            widget.bg_color = [0.2, 0.2, 0.2, 1]

    elif not widget.collide_point(*pos) and widget.hovered:
        widget.hovered = False
        widget.opacity = 1
        Window.set_system_cursor('arrow')

        if src != None:
            widget.source = default
        if dropdown != None:
            widget.bg_color = [0.18, 0.18, 0.18, 1]

def setup_hover(widget, flag, opacity=0.9, src=None, default=None, cursor=None, scroll=False, dropdown=None):
    """
    Configura el comportamiento de hover para un widget.
    Vincula la función on_hover al evento de movimiento del mouse.
    """
    l = lambda win, pos: on_hover(widget, pos, opacity, flag, src, default, cursor, scroll, dropdown)

    Window.bind(mouse_pos=l)

    return l
    