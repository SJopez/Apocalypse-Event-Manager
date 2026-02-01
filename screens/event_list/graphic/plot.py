import matplotlib.pyplot as plt
import matplotlib.patches as patches
from modules.utilities import *
import calendar
from datetime import datetime, timedelta
import matplotlib

def get_duration(event):
    """
    Calcula la duración de un evento en días (incluyendo fracción de tiempo).
    """
    di = event["fechaInicio"]
    df = event["fechaFin"]
    ti = event["tiempoInicio"]
    tf = event["tiempoFin"]

    dti = get_date(di[0], di[1], di[2], ti[0], ti[1])
    dtf = get_date(df[0], df[1], df[2], tf[0], tf[1])

    diff = dtf - dti

    return diff.days + diff.seconds / 60 / 60 / 24

def get_ini_sum(event):
    """
    Calcula la fracción del día en la que inicia el evento.
    Retorna un valor entre 0 y 1.
    """
    d = event["fechaInicio"]
    t = event["tiempoInicio"]

    d1 = get_date(d[0], d[1], d[2], 0, 0)
    d2 = get_date(d[0], d[1], d[2], t[0], t[1])

    diff = d2 - d1

    return diff.seconds / 60 / 60 / 24

def get_end(event):
    """
    Obtiene el día de finalización del evento.
    """
    return int(event["fechaFin"][0])

def get_date(day, month, year, hour, min):
    """
    Crea un objeto datetime a partir de los componentes de fecha y hora.
    """
    return datetime(int(year), int(month), int(day), int(hour), int(min))
    
def get_maximum(running):
    """
    Encuentra la fecha máxima de finalización entre todos los eventos en ejecución.
    Retorna la fecha máxima + 1 día para dar margen al gráfico.
    """
    ans = get_date(1, 1, 2000, 22, 22)

    for event in running:
        d = event["fechaFin"]
        t = event["tiempoFin"]
        ans = max(ans, get_date(d[0], d[1], d[2], t[0], t[1]))

    return ans + timedelta(1)

def get_max_num(running):
    """
    Obtiene el número de evento más alto (para determinar la altura del eje Y).
    """
    ans = 0
    for event in running:
        ans = max(ans, event["eventNum"])
    return ans

def createGraph():
    """
    Genera y muestra un gráfico con los eventos en ejecución usando Matplotlib.
    """
    matplotlib.rcParams['toolbar'] = 'none'
    running = readJson("data/dynamic/running_events.json")
    
    fig, ax = plt.subplots(figsize=(10, 7))
    maxDate = get_maximum(running)
    index = 1

    x_axis, label_x = [], []
    y_axis = []

    # Genera el eje X con todas las fechas desde 2077 hasta la fecha máxima encontrada
    for year in range(2077, maxDate.year + 1):
        rm = maxDate.month if year == maxDate.year else 12

        for month in range(1, rm + 1): 
            rd = maxDate.day if year == maxDate.year and month == maxDate.month else calendar.monthrange(year, month)[1]

            for day in range(1, rd + 1):
                x_axis.append(len(x_axis) + 1)
                label_x.append(f"{day}/{month}\n{year}")
    
    # Genera el eje Y basado en el número máximo de eventos simultáneos
    for count in range(1, max(8, get_max_num(running) + 2)):
        y_axis.append(count)

    # Asegura un mínimo de 10 días en el eje X si hay pocos datos
    if len(x_axis) < 10:
        x_axis = []
        label_x = []
        for x in range(1, 11):
            x_axis.append(x)
            label_x.append(f"{x}/{1}\n{2077}")
    
    # Configuración visual de los ejes
    ax.set_xticks(x_axis)
    ax.set_xticklabels(label_x)
    ax.set_yticks(y_axis)
    ax.tick_params(colors="white")

    # Dibuja cada evento como un rectángulo en el gráfico
    for event in running:
        eini = event["fechaInicio"]
        id = event["eventID"]
        ini = f"{eini[0]}/{eini[1]}\n{eini[2]}"
        # Calcula la posición X basada en la fecha y hora de inicio
        x = label_x.index(ini) + get_ini_sum(event) + 1

        r = patches.Rectangle(
            (x, event["eventNum"] - 0.3), 
            get_duration(event), 
            0.6
        )
        if type(id) == list:
            r.set_facecolor(id)
        else:
            r.set_facecolor(colors[event["eventID"] - 1])
        r.set_edgecolor([0.07, 0.07, 0.07, 0.85])
        ax.add_patch(r)
        index += 1

    # Estilización del gráfico (colores oscuros para fondo)
    fig.patch.set_facecolor([0.07, 0.07, 0.07, 1])
    fig.canvas.manager.set_window_title("Gráfico de Aventuras")
    ax.set_facecolor([0.12, 0.12, 0.12, 1])
    ax.spines["left"].set_color("white")
    ax.spines["bottom"].set_color("white")
    plt.xlim(0, 10)
    plt.ylim(0, 7)
    plt.xlabel("Fecha→",fontsize=20, fontweight='bold', color="white", loc='right')
    plt.ylabel("Aventuras→",fontsize=20, fontweight='bold', color="white", loc='top')

    def keypress(press):
        """
        Maneja eventos de teclado para navegar por el gráfico (scroll).
        """
        x = ax.get_xlim()
        y = ax.get_ylim()
        
        if press.key == 'up' and y[1] < len(y_axis):
            ax.set_ylim(y[0] + 1, y[1] + 1)
        if press.key == 'down' and y[0] > 0:
            ax.set_ylim(y[0] - 1, y[1] - 1)

        if press.key == 'right' and x[1] < len(x_axis):
            ax.set_xlim(x[0] + 1, x[1] + 1)
        if press.key == 'left' and x[0] > 0:
            ax.set_xlim(x[0] - 1, x[1] - 1)
        
        fig.canvas.draw_idle()

    
    fig.canvas.mpl_connect('key_press_event', keypress)
    