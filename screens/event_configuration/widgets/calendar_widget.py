from modules.modules import *
from modules.utilities import *
from modules.ui_utils import *

# Lista de nombres de meses para mostrar en la interfaz. El índice 0 es un marcador de posición.
months = [0, "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

def getCalendar():
    """
    Obtiene la instancia actual del widget TotalCalendar desde la interfaz principal.
    """
    return join_child(appList().mycon, "TotalCalendar")

class AdvanceMonth(ButtonBehavior, Image):
    """
    Botón para avanzar al siguiente mes en el calendario.
    """
    def __init__(self):
        super().__init__()
        self.source = "assets/right.png"
        self.size_hint: None
        self.size = (40, 40)

    def on_touch_down(self, touch):
        """
        Maneja el evento de toque. Si se toca el botón, actualiza el calendario al siguiente mes.
        """
        if self.collide_point(*touch.pos):
            getCalendar().update(1)

class PreviousMonth(ButtonBehavior, Image):
    """
    Botón para retroceder al mes anterior en el calendario (solo se activa si el mes actual no es el primero de la fecha origen).
    """
    def __init__(self, flag):
        super().__init__()
        self.source = "assets/left.png"
        self.size_hint: None
        self.size = (40, 40)

    def on_touch_down(self, touch):
        """
        Maneja el evento de toque. Si se toca el botón, actualiza el calendario al mes anterior.
        """
        if self.collide_point(*touch.pos):
            getCalendar().update(0)

class Day(Label):
    """
    Representa un día individual en la cuadrícula del calendario.
    """
    def __init__(self, text):
        super().__init__()
        self.text = text
        
    def on_touch_down(self, touch):
        """
        Maneja la selección de un día.
        Actualiza la fecha de inicio o fin en EventInfo y cierra el calendario.
        """
        calendar = getCalendar()
        if self.collide_point(*touch.pos):
            evinfo = join_child(appList().mycon, "EventInfo")
            day = self.text
            month = calendar.currentMonth
            year = calendar.currentYear
            
            # Si flag es True, estamos seleccionando fecha de fin, si no, fecha de inicio.
            if calendar.flag:
                evinfo.updateEnd(f"{day}/{month}/{year}")
            else:
                evinfo.updateIni(f"{day}/{month}/{year}")

            Disappear(calendar)
        elif not calendar.collide_point(*touch.pos):
            # Cierra el calendario si se toca fuera de él.
            Disappear(calendar)

class Calendar(StackLayout):
    """
    Contenedor que muestra los días del mes seleccionado.
    """
    def __init__(self, month, year):
        super().__init__()
        self.month = month
        self.year = year

        # Genera widgets Day para cada día del mes.
        for i in range(1, calendar.monthrange(self.year, self.month)[1] + 1):
            self.add_widget(Day(str(i)))

class Info(BoxLayout):
    """
    Muestra el mes y año actuales en la parte superior del calendario.
    """
    def __init__(self):
        super().__init__()

class ButtonContainer(BoxLayout):
    """
    Contenedor para los botones de navegación (mes anterior/siguiente).
    """
    def __init__(self, flag=True):
        super().__init__()
        self.previous = PreviousMonth(flag)
        # Oculta el botón de anterior si estamos en el mes inicial de la fecha origen (flag=True).
        self.previous.opacity = 0 if flag else 1
        self.advance = AdvanceMonth()
        self.add_widget(self.previous)
        self.add_widget(Label())
        self.add_widget(self.advance)

class TotalCalendar(BoxLayout):
    """
    Widget principal del calendario que ensambla la información, la cuadrícula de días y los controles.
    """
    def __init__(self, flag):
        super().__init__()
        self.currentMonth = 1
        self.currentYear = 2077
        self.calendar = Calendar(1, 2077)
        self.info = Info()
        self.buttons = ButtonContainer()
        self.flag = flag # Indica si se está seleccionando fecha de inicio o fin.
        self.add_widget(self.info)
        self.add_widget(self.calendar)
        self.add_widget(self.buttons)
        self.add_widget(Label())

    def update(self, type):
        """
        Actualiza el calendario al cambiar de mes.
        type: 1 para avanzar mes, 0 para retroceder.
        """
        # Límite superior de selección de año
        if type and self.currentYear == 2222:
            return
        
        if type:
            # Avanzar mes
            self.currentMonth %= 12
            self.currentMonth += 1
            self.currentYear += (self.currentMonth == 1)
        elif not (self.currentMonth == 1 and self.currentYear == 2077):
            # Retroceder mes (si no estamos en el mes inicial de la fecha origen)
            self.currentMonth -= 1
            self.currentYear -= (self.currentMonth == 0)
            self.currentMonth = 12 if self.currentMonth == 0 else self.currentMonth
        
        # Determina si estamos en el mes/año inicial para deshabilitar el botón "anterior"
        flag = True if self.currentMonth == 1 and self.currentYear == 2077 else False
        
        # Actualiza etiquetas de texto
        self.info.ids.month.text = months[self.currentMonth]
        self.info.ids.year.text = str(self.currentYear)

        # Actualiza la cuadrícula del calendario
        self.remove_widget(self.calendar)
        self.calendar = Calendar(self.currentMonth, self.currentYear)
        self.add_widget(self.calendar)
        
        # Actualiza los botones de navegación
        self.remove_widget(self.buttons)
        self.buttons = ButtonContainer(flag)
        self.add_widget(self.buttons)
