
from modules.utilities import *
from core.event_manager import validateEventInfo, checkEvent, mergeInformation, createEvent, validResources
from modules.ui_utils import *
import datetime as dt

def addToEventList(event):
    """
    Añade un evento a la lista visual de eventos en ejecución.
    """
    running = appList().events.scrollList.running
    
    from screens.event_list.events import RunningEvent

    running.add_widget(RunningEvent(event))

def manageAdventure(response, info, realTime):
    """
    Gestiona la fase final de creación de una aventura.
    Si la respuesta es True comprueba si hay información brindada por el algoritmo de búsqueda de intervalo y actualiza la plantilla del evento, muestra un mensaje de éxito
    y añade el evento a la lista de eventos en ejecución.
    También se encarga de limpiar la interfaz (eliminar popups, restaurar opacidad).
    """
    main = appList().mycon
    
    if response:
        # Obtiene la plantilla del evento actual (índice 1)
        current = readJson("data/dynamic/current_event.json")[1]

        if info != None:
            # Si hay información de tiempo proveniente de la búsqueda de intervalo, actualiza las fechas y horas del evento
            current["fechaInicio"] = [str(info[0].day), str(info[0].month), str(info[0].year)]
            current["fechaFin"] = [str(info[1].day), str(info[1].month), str(info[1].year)]
            current["tiempoInicio"] = [info[0].hour - 5, info[0].minute]
            current["tiempoFin"] = [info[1].hour - 5, info[1].minute]
            current["tiempoReal"] = [*realTime]
         
        # Asigna un número identificativo único al evento
        current["eventNum"] = findMex()
        # Muestra mensaje de éxito
        title = "Aventura creada exitosamente!"
        body = " " + current["titulo"]
        pos = (WindowWidth - 400, 0)
        showMessage(Message, "Message", title, body, pos)
        
        # Asigna un ID únicos y añade el evento a running_events.json
        from screens.event_configuration.widgets.editable_event import colorSelected
        
        current["eventID"] = current["id"] if current["id"] != -1 else colorSelected

        current["id"] = dt.datetime.now().timestamp()
        addToJson("data/dynamic/running_events.json", current)
        addToEventList(current)

    # Limpieza de la interfaz: elimina el popup (hole) y restaura la interactividad (Disable.value=False)
    if main.hole != None:
        main.remove_widget(main.hole)
        backgroundManager(main, 1)
        main.hole = None

def create_adventure():
    """
    Función principal para iniciar el proceso de creación de una aventura.
    Valida la información del evento (fechas, recursos), muestra errores si los hay,
    o procede a crear el evento si todo es válido.
    """

    eventInfo = join_child(appList().mycon, "EventInfo")

    # Valida fechas y recursos
    dateValid = checkEvent(eventInfo)
    resourceValid = validResources()
    
    # Validación adicional de la información del evento
    validDate = validateEventInfo()
    if type(validDate) != bool:
        # Muestra error si la validación de fecha falla
        pos = (WindowWidth - 400, WindowHeight - 140)
        showMessage(Error, "Error", validDate[1], validDate[2], pos, short=True)

    elif type(dateValid) != tuple or type(resourceValid) != list:
        # Muestra error si hay problemas con el rango de fechas o recursos insuficientes
        title, body = "No es posible crear la aventura!", ""

        if type(dateValid) != tuple:   
            body = "La fecha introducida no corresponde a un intervalo de tiempo valido, " + dateValid
        else:
            body = "Hay conflictos con los recursos, " + resourceValid

        pos = (WindowWidth - 400, WindowHeight - 200)
        showMessage(Error, "Error", title, body, pos)

    else:
        # Si todo es válido, fusiona la información y crea el evento
        event = mergeInformation(dateValid, resourceValid)
        response = createEvent(event)
        rawEvent = readJson("data/dynamic/current_event.json")

        # Actualiza current_event.json con el nuevo evento
        if len(rawEvent) == 1:
            addToJson("data/dynamic/current_event.json", event)
        else:
            rawEvent.pop()
            rawEvent.append(event)
            writeJson("data/dynamic/current_event.json", rawEvent)

        if response[0]:
            # Si no ocurrieron colisiones con la fecha seleccionada, finaliza la creación de la aventura
            manageAdventure(True, None, None)
        else:
            # Si hubo problemas (ej. recursos insuficientes para la fecha), muestra opciones al usuario para buscar un intervalo alternativo    
            title = "Su aventura no puede ser creada en la fecha especificada!"
            body = "La cantidad de uno o varios de los recursos seleccionados excede lo disponible en el inventario. Desea buscar un intervalo de tiempo valido para su aventura?"
            pos = (WindowWidth - 420, WindowHeight - 250)
            main = appList().mycon
            
            # Deshabilita la interfaz principal y muestra el mensaje de resolución de conflictos
            backgroundManager(main, 0)

            main.hole = JoinHole(title, body, response[1], response[2])
            main.add_widget(main.hole)
