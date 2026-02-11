from modules.modules import *
from modules.utilities import *
from screens.event_configuration.widgets.calendar_widget import TotalCalendar
from kivy.uix.dropdown import DropDown
from modules.ui_utils import *

class DateIniButton(Button):
    """
    Botón para abrir el calendario y seleccionar la fecha de inicio del evento.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        setup_hover(self, 1, scroll=True)

    hovered = False

    def on_touch_down(self, touch):
        """
        Abre el widget TotalCalendar en modo 'fecha-inicio' (0) si no está ya abierto o deshabilitado.
        """
        if self.collide_point(*touch.pos) and (appList().mycon.children[0].__class__.__name__ != "TotalCalendar") and not Disable.value:
            main = appList().mycon
            backgroundManager(main, False)
            calendar = TotalCalendar(0)
            AppearAnimation(calendar)
            main.add_widget(calendar)
            

class DateEndButton(Button):
    """
    Botón para abrir el calendario y seleccionar la fecha de fin del evento.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        setup_hover(self, 1, scroll=True)
    
    hovered = False
        
    def on_touch_down(self, touch):
        """
        Abre el widget TotalCalendar en modo 'fecha-fin' (1) si no está ya abierto o deshabilitado.
        """
        if self.collide_point(*touch.pos) and (appList().mycon.children[0].__class__.__name__ != "TotalCalendar") and not Disable.value:
            main = appList().mycon
            backgroundManager(main, False)
            calendar = TotalCalendar(1)
            AppearAnimation(calendar)
            main.add_widget(calendar)

class Date(Label):
    """
    Etiqueta simple para mostrar fechas seleccionadas.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text = "None"

class TimeInput(TextInput):
    """
    Campo de entrada de texto para horas y minutos.
    Maneja el foco automático al completar 2 dígitos.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (1, 1, 1, 0.9)
        setup_hover(self, 1, cursor="ibeam", scroll=True)
    
    hovered = False

    def keyboard_on_textinput(self, window, text):
        """
        Filtra la entrada para aceptar solo números y cambia el foco
        al campo de minutos automáticamente cuando la longitud es 2.
        """
        try:
            a = int(text)
        except:
            pass
        else: 
            if len(self.text) < 2:
                self.text += text
            elif len(self.text) == 2:
                minu = self.parent.parent.timeIni[1] if self.name == "ini" else self.parent.parent.timeEnd[1]
                self.focus = False
                minu.focus = True


class FloatContainer(FloatLayout):
    """
    Contenedor flotante que agrupa los widgets del panel inferior
    Su funcionalidad consiste en posicionar de manera absoluta los widgets hijos.
    """
    def __init__(self, child):
        super().__init__()
        self.add_widget(Show())
        self.add_widget(child)
        self.status = False   

class Show(ButtonBehavior, Image):
    """
    Icono decorativo que muestra si el panel inferior está abierto o cerrado.
    """
    def __init__(self):
        super().__init__()
        setup_hover(self, 1, 1)
        self.source = "assets/plus.png"
    
    hovered = False

class Event(FloatLayout):
    """
    Representa un elemento individual (opción de evento) dentro del menú desplegable (Selector).
    """
    def __init__(self, index, selector):
        super().__init__()
        self.index = index
        self.selector = selector
        self.hover = setup_hover(self, 1, 1, scroll=True, dropdown=self)

    title = StringProperty("")
    bg_color = ListProperty([0.18, 0.18, 0.18, 1])
    hovered = False

    def on_touch_down(self, touch):
        """
        Al seleccionar este evento, actualiza el selector principal y carga la información
        del evento correspondiente.
        """
        if self.collide_point(*touch.pos) and not Disable.value:
            self.selector.select(self.title)
            self.selector.caller.icon = "assets/minus.png"
            self.selector.evinfo.update(self.index)

class Selector(DropDown):
    """
    Menú desplegable que lista los tipos de eventos disponibles para configurar.
    """
    def __init__(self, caller, evinfo):
        super().__init__()
        self.max_height = 400
        self.bind(on_select=self.selection)
        self.caller = caller
        self.evinfo = evinfo
        
        # Opción de Aventura Personalizada
        e = Event(-1, self)
        e.title = "-Aventura Personalizada-"
        self.add_widget(e)

        # Cargar eventos predefinidos desde la configuración
        for i in range(18):
            e = Event(i, self)
            e.title = Manage.get_one(i)["titulo"]
            self.add_widget(e)
    
    def selection(self, option, value):
        """Actualiza el texto del botón que abrió el selector."""
        setattr(self.caller, 'name', value)                

class SelectorCaller(FloatLayout):
    """
    Botón principal que despliega el menú de selección de eventos (Selector).
    Maneja la apertura, cierre y cambio de icono (+/-).
    """
    def __init__(self):
        super().__init__()
        setup_hover(self, 1)
        Window.bind(mouse_pos=lambda win, pos: self.close(pos))

    def close(self, pos):
        """
        Cierra el menú desplegable si se hace clic fuera de él.
        También aprovecha la detección del mouse para gestionar las animaciones del panel inferior.
        """
        if Disable.value:
            return

        x1, x2 = self.x, self.x + 450

        if pos[0] < x1 or pos[0] > x2:
            self.selector.dismiss()

        if pos[1] > 570 or pos[1] < 130:
            self.selector.dismiss()

        configShowAnimation(appList().mycon, pos)
        configShowAnimation(appList().menu, pos)

    # Llama a la función que cambia el icono del botón al cerrar el menú desplegable.
    def set_bind(self):
        self.selector.bind(on_dismiss=self.change_icon)

    hovered = False
    name = StringProperty(Manage.get_one(0)["titulo"])
    selector = None
    icon = StringProperty("assets/minus.png")

    def change_icon(self, *args):
        """Cambia el icono a 'minus' cuando se cierra el menú desplegabale."""
        self.icon = "assets/minus.png"
        Utils.isDismiss = True

    def on_touch_down(self, touch):
        """Abre el menú desplegable al tocar el botón y cambia el icono a 'plus'."""
        if self.collide_point(*touch.pos) and not Disable.value:
            self.selector.open(self)
            self.icon = "assets/plus.png"
            Utils.isDismiss = False

