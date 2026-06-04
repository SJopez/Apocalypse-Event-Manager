from modules.modules import *
from kivy.uix.filechooser import FileChooserIconView
from modules.utilities import *
from modules.ui_utils import showMessage, Message, Error
import os, sys, shutil

Builder.load_file("screens/init_menu/styles/file_selector.kv")

class Path(Label):
    """
    Etiqueta que muestra la ruta del archivo o directorio seleccionado.
    """
    def __init__(self):
        super().__init__()
       
def to_close(main, touch):
    """
    Cierra el selector de archivos si se hace clic fuera de él.
    """
    selector = main.fileSelector
    
    if selector != None and not selector.collide_point(*touch.pos):
        closeSelector(main)

class SelectionButton(Button):
    """
    Botón de selección en el selector de archivos.
    Maneja carga, guardado y selección.
    """
    def __init__(self, type):
        super().__init__()
        setup_hover(self, 3)
        self.type = type
    
    hovered = False

    def on_touch_down(self, touch):
        """
        Maneja el evento de clic en el botón de selección.
        Ejecuta la acción correspondiente según el tipo de botón (load, save, image).
        Maneja además mensajes de errores de carga incorrecta y confirmaciones.
        Aprovecha el evento de toque para comprobar si se debe cerrar el selector (to_close).        
        """
        to_close(appList().mycon, touch)
        to_close(appList().mainMenu, touch)

        if self.collide_point(*touch.pos):
            main = appList().mainMenu

            if self.type == "load":    
                path = join_child(main, "FileSelector").selection

                if len(path) > 0:
                    file = readJson(path[0])
                    response = selectFile(file)
                    
                    if not response:
                        title = "¡Error al cargar el archivo!"
                        body = "El archivo que ha intentado cargar no coincide con el formato de aventura o existen conflictos entre las aventuras existentes"
                        pos = (WindowWidth - 390, WindowHeight - 185)
                        showMessage(Error, "Error", title, body, pos, main)
                    else:
                        closeSelector(main)
                        writeJson("data/dynamic/running_events.json", file)                       
                        title = "¡Archivo cargado exitosamente!"
                        body = f"Se cargaron {len(file)} aventuras"
                        pos = (WindowWidth - 390, 0)
                        showMessage(Message, "Message", title, body, pos, main)
            
            if self.type == "save":
                file = os.path.join(os.path.dirname(sys.argv[0]), "data/dynamic/running_events.json")
                dir = os.path.join(join_child(main, "Path").text)
                running = readJson("data/dynamic/running_events.json")

                try:
                    shutil.copy(file, dir)
                except Exception as error:
                    title = "¡Error al guardar el archivo!"
                    body = "Inténtelo de nuevo o compruebe que tenga permiso para copiar archivos en el directorio seleccionado"
                    pos = (WindowWidth - 390, WindowHeight - 185)
                    showMessage(Error, "Error", title, body, pos, main)
                else:
                    title = "¡Archivo guardado exitosamente!"
                    body = f"Se guardaron {len(running)} aventuras" 
                    pos = (WindowWidth - 390, 0)
                    showMessage(Message, "Message", title, body, pos, main)
                    closeSelector(main)

            if self.type == "image":
                main = appList().mycon
                pathImage = join_child(main, "PathImage")
                pathImage.text = self.parent.path.text
                
                try:
                    img = join_child(main, "AdventureImage")
                    img.source = pathImage.text
                except:
                    title = "¡Error al cargar la imagen!"
                    body = "Inténtelo de nuevo y compruebe que la imagen exista y no esté dañada"
                    pos = (WindowWidth - 390, WindowHeight - 185)
                    showMessage(Error, "Error", title, body, pos, main)
                else:
                    title = "Imagen cargada"
                    body = f"Se cargó la imagen correctamente" 
                    pos = (WindowWidth - 390, 0)
                    showMessage(Message, "Message", title, body, pos, main)
                    closeSelector(main)

class BottomBar(BoxLayout):
    """
    Barra inferior del selector de archivos que contiene la ruta y el botón de selección.
    """
    def __init__(self, type):
        super().__init__()
        self.add_widget(Label())
        self.path = Path()
        self.add_widget(self.path)
        self.add_widget(SelectionButton(type))

class Title(Label):
    """
    Título del selector de archivos, cambia según el contexto (cargar, guardar, imagen).
    """
    def __init__(self, type):
        super().__init__()
        
        if type == "load":
            self.text = "Seleccione el archivo JSON"
        if type == "save":
            self.text = "Seleccione el directorio donde guardar su archivo"
        if type == "image":
            self.text = "Seleccione la imagen de su aventura"

def selectFile(selected):
    """
    Actualiza la lista de eventos con el archivo seleccionado.
    """
    eventList = appList().events.scrollList.running
    return eventList.update(True, selected)

class FileSelector(FileChooserIconView):
    """
    Vista de selector de archivos con iconos.
    Configura filtros y manejo de selección.
    """
    def __init__(self, type):
        super().__init__()
        self.path = '.'
        if type == "load":
            self.filters = ['*.json']
        if type == "save":
            self.filters = ["/"]
        if type == "image":
            self.filters = ["*.png", "*.jpg"]
        self.multiselect = False
        self.type = type
        self.bind(path=self.update_path)
        
        if type != "saves":
            self.bind(selection=self.update_path)
        
    def update_path(self, *args):
        """
        Actualiza la etiqueta de ruta cuando se selecciona un archivo o cambia el directorio.
        """
        main = appList().mainMenu if self.type != "image" else appList().mycon
        pathLabel = join_child(main, "Path")
        if type(pathLabel) != int:
            pathLabel.text = self.path if len(self.selection) == 0 else self.selection[0]
        
class FileSelectorWindow(BoxLayout):
    """
    Ventana contenedora del selector de archivos.
    """
    def __init__(self, type):
        super().__init__()
        self.type = type
        self.add_widget(Title(type))
        self.add_widget(FileSelector(type))
        self.add_widget(BottomBar(type))

def openSelector(main, type):
    """
    Abre el selector de archivos en la pantalla principal.
    Deshabilita otras interacciones mientras está abierto.
    """
    Disable.value = True
    Window.set_system_cursor('arrow')
    main.fileSelector = FileSelectorWindow(type)
    main.add_widget(main.fileSelector)

def closeSelector(main):
    """
    Cierra el selector de archivos y restaura la interacción.
    """
    Disable.value = False
    Window.set_system_cursor('arrow')
    main.remove_widget(main.fileSelector)
    main.fileSelector = None
    
def on_press(button, touch, type):        
    """
    Maneja la interacción de botones que abren el selector de archivos.
    """
    if button.collide_point(*touch.pos) and not Disable.value:
        main = appList().mainMenu
        openSelector(main, type)
