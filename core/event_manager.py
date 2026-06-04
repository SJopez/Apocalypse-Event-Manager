import datetime as dt
from modules.utilities import *
from screens.event_list.graphic.plot import get_date

sg1 = "por favor verifique que los valores seleccionados sean correctos!"
sg2 = "su aventura debe tener una duracion de al menos 24 horas!"

def setEvent(event, isEditable = False):
    """
    Configura el evento actual en el archivo de evento correspondiente.

    Args:
        event: El diccionario del evento a guardar.
        isEditable: Si el evento es editable (predefinido o personalizado).
    """
    if isEditable:
        # Si es editable, se marca con un id especial y sin requisitos predefinidos
        event["id"] = -1
        event["necesita"] = []

    writeJson('data/dynamic/current_event.json', [event])

def getChar(s):
    """
    Verifica si una cadena contiene caracteres que no sean espacios.

    Args:
        s: La cadena a verificar.
    """
    for c in s.split(" "):
        if c != "":
            return True
    return False

def validateEventInfo():
    """
    Lee y valida la información básica del evento actual (título, descripción, recursos).

    Returns:
        bool | tuple: True si es válido, o una tupla (False, título_error, cuerpo_error) si falla.
    """
    current = readJson("data/dynamic/current_event.json")[0]
    resources = readJson("data/dynamic/selected_resources_event.json")
    title, body = "Error al crear la aventura", ""

    # Comprueba que el título, contiene caracteres que no sean espacios 
    if getChar(current["titulo"]) == False:
        body = "Debe escoger un nombre no vacio para su aventura"
        return (False, title, body)
    
    # Comprueba que la descripción, contiene caracteres que no sean espacios
    if getChar(current["descripcion"]) == False:
        body = "Debe escoger una descripcion no vacia para su aventura"
        return (False, title, body)
    
    # Comprueba que haya al menos un recurso seleccionado
    if len(resources) == 0:
        body = "Su aventura debe tener al menos un recurso asignado"
        return (False, title, body)

    return True


def validDate(Ini, End, TimeIni, TimeEnd):
    """
    Valida la lógica de las fechas y horas (inicio < fin, duración mínima).

    Args:
        Ini: Fecha de inicio "DD/MM/YYYY".
        End: Fecha de fin "DD/MM/YYYY".
        TimeIni: Hora de inicio (HH, MM).
        TimeEnd: Hora de fin (HH, MM).

    Returns:
        tuple | str: Tupla con timestamps y datos originales si es válido, o mensaje de error.
    """

    Ini = Ini.split("/")
    End = End.split("/")
    hi, mi = TimeIni[0], TimeIni[1]
    he, me = TimeEnd[0], TimeEnd[1]
    start, end = 0, 0
    td = 0
    try:
        # Crear timestamps(convertir fecha a segundos) para inicio y fin
        start = dt.datetime(int(Ini[2]), int(Ini[1]), int(Ini[0]), hi, mi).timestamp()
        end = dt.datetime(int(End[2]), int(End[1]), int(End[0]), he, me).timestamp()
     
        # Calcular timestamp de inicio + 24 horas (duración mínima)
        td = dt.datetime(int(Ini[2]), int(Ini[1]), int(Ini[0]) + 1, hi, mi).timestamp()
        
        # Validar que inicio < fin y duración mínima
        if td > end:
             raise Exception()
          
    except Exception as e:
        # Manejo de errores específicos
        return sg1 if type(e) == IndexError or type(e) == ValueError else sg2    
    else:
        # Información horaria del evento lista para ser procesada
        return ((start, end), (Ini, End), ((hi, mi), (he, me)))


def checkEvent(eventInfo):
    """
    Valida las fechas y horas del evento desde la interfaz gráfica.
    Si el evento es editable, actualiza la información en el JSON.

    Args:
        eventInfo: Objeto que contiene los widgets con la información del evento proporcionada por el usuario.

    Returns:
        tuple | str: Resultado de validDate (timestamps, fechas, horas) o mensaje de error.
    """
    dateValid = None

    if eventInfo.editable == None:
        # Caso: Evento no editable (basta tomar la información que ya se tiene del evento con la de los widgets proporcionada por el usuario)
        dateIni = eventInfo.dateIni.text
        dateEnd = eventInfo.dateEnd.text
        timeIni = (eventInfo.time[0].hour, eventInfo.time[0].minute)
        timeEnd = (eventInfo.time[1].hour, eventInfo.time[1].minute)
        dateValid = validDate(dateIni, dateEnd, timeIni, timeEnd)
    else:
        # Caso: Evento editable (se toma toda la información de los widgets proporcionada por el usuario y se actualiza el JSON)                                
        edit = eventInfo.editable
        dateIni = edit.dateIni.text
        dateEnd = edit.dateEnd.text
        timeIni = (edit.time[0].hour, edit.time[0].minute)
        timeEnd = (edit.time[1].hour, edit.time[1].minute)
        dateValid = validDate(dateIni, dateEnd, timeIni, timeEnd)
        
        # Actualizar el evento actual con los datos del formulario(widgets de la interfaz)
        current = readJson("data/dynamic/current_event.json")[0]
        current["titulo"] = edit.ids.name.text
        current["tipo"] = [edit.ids.type.text]
        current["descripcion"] = edit.ids.description.text
        current["peligro"] = danger_words_inverse[edit.ids.danger.text]
        current["ubicacion"] = edit.ids.place.text
        
        writeJson("data/dynamic/current_event.json", [current])

    return dateValid

def validResources():
    """
    Valida los recursos seleccionados para el evento.
    Verifica requisitos, exclusiones, complementos y cantidades disponibles.

    Returns:
        list | str: Lista de tuplas (id_recurso, cantidad) si es válido, o mensaje de error con sugerencia.
    """
    event = readJson("data/dynamic/current_event.json")[0]
    resources = readJson("data/dynamic/selected_resources_event.json")

    # Verificar que todos los recursos necesarios estén presentes
    for need in event["necesita"]:
        res_need = get_one(need)

        if not (res_need in resources):
            return "uno de los recursos necesarios para el evento no se encuentra entre los seleccionados!"

    for resource in resources:
        # Verificar exclusiones (recursos que no pueden ir juntos)
        for exclud in resource["excluyente"]:
            value = getOneByName(exclud, "data/dynamic/selected_resources_event.json")

            if value != False:
                return "verifique para cada recurso que su excluyente no se encuentre seleccionado!"
        
        flag = False

        # Verificar complementarios (al menos uno debe estar presente si se requiere)
        for complement in resource["complementario"]:
            value = getOneByName(complement, "data/dynamic/selected_resources_event.json")
         
            if value != False:
                flag = True
                break
        
        if not flag:
            return "verifique que cada recurso este seleccionado junto con su complementario!"
 

    resorceList = appList().mycon.layo.rlist
    answer = []

    # Verificar cantidades disponibles en el inventario
    for child in resorceList.children:
        cuantity = int(child.cuantity.text)
        resource = get_one(child.id)
        
        if cuantity > resource["cantidad"]:
            return "verifique que la cantidad seleccionada de cada recurso no exceda la cantidad disponible en el inventario!"            

        answer.append((child.id, cuantity))

    return answer

def interception(l1, r1, l2, r2):
    """
    Verifica si dos intervalos de tiempo se superponen.

    Args:
        l1, r1: Inicio y fin del primer intervalo.
        l2, r2: Inicio y fin del segundo intervalo.

    Returns:
        bool: True si hay intersección, False en caso contrario.
    """
    if (l1 <= l2 and l2 <= r1) or (l2 <= l1 and l1 <= r2):
        return True
    
    return False

def verifyInterval(event, ini, end):
    """
    Verifica si es posible programar el evento en el intervalo dado,
    considerando la disponibilidad de recursos compartidos con otros eventos en curso.

    Args:
        event: El evento a verificar.
        ini: Timestamp de inicio.
        end: Timestamp de fin.

    Returns:
        bool: True si el intervalo es válido (recursos suficientes), False si no.
    """
    resources = {}

    for runEvent in readJson("data/dynamic/running_events.json"):
        timeEvent = runEvent["tiempoReal"]

        # Si hay intersección temporal con otro evento
        if interception(timeEvent[0], timeEvent[1], ini, end):
            for type in runEvent["recursos"]:
                # Sumar recursos usados por eventos que colisionen
                cuantity = resources.get(type, 0)
                resources.update({type: cuantity + runEvent["recursos"][type]})
                
                # Verificar si la suma excede el total disponible
                myCuantity = event["recursos"].get(int(type), 0)
                total = get_one(int(type))["cantidad"]
                if myCuantity and myCuantity + resources[type] > total:
                    return False
                
    return True

def toDate(value):
    """Convierte un timestamp a objeto datetime UTC."""
    return dt.datetime.fromtimestamp(value, tz=dt.timezone.utc)

def getDate(day, month, year):
    """Obtiene el timestamp para una fecha dada."""
    return dt.datetime(year, month, day).timestamp() 

def joinTime(event):
    """
    Busca el intervalo de tiempo disponible MÁS CERCANO.
    Comienza en 2077 (inicio del calendario) y busca huecos cronológicamente.

    Args:
        event: El evento a reprogramar.

    Returns:
        tuple: (timestamp_inicio, timestamp_fin) del nuevo intervalo encontrado.
    """
    ini = event["tiempoReal"][0]
    end = event["tiempoReal"][1]
    time = end - ini
    default = getDate(1, 1, 2077)
    
    # 1. Intentar en el inicio del calendario (2077)
    if verifyInterval(event, default, default + time):
        return (default, default + time)

    # 2. Buscar el mejor hueco entre eventos existentes
    ans = getDate(1, 1, 2222)
    for e in readJson("data/dynamic/running_events.json"):
        tr = e["tiempoReal"]
        
        if verifyInterval(event, tr[1] + 60, tr[1] + 60  + time):
            curr = tr[1] + 60
            ans = min(ans, curr)

    return (ans, ans + time)     

def mergeInformation(Date, Resources):
    """
    Combina la información de fecha y recursos validados en el objeto del evento.
    También asigna la imagen correspondiente.

    Args:
        Date: Tupla con ((start, end), (Ini, End), ((hi, mi), (he, me))) (información de fecha y hora listas para ser procesadas).
        Resources: Lista de recursos seleccionados.

    Returns:
        dict: El evento actualizado con toda la información lista para procesar.
    """
    event = readJson("data/dynamic/current_event.json")[0]

    event["recursos"] = dict(Resources)
    event["tiempoReal"] = Date[0]
    event["fechaInicio"] = Date[1][0]
    event["fechaFin"] = Date[1][1]
    event["tiempoInicio"] = Date[2][0]
    event["tiempoFin"] = Date[2][1]
    
    if event["id"] == -1:
        # Si es evento de tipo personalizable, obtiene el link de la imagen asignado por el usuario
        main = appList().mycon
        event["imagen"] = join_child(main, "PathImage").text
    else:
        # Si es predefinido, usa la imagen por defecto asignada al evento
        event["imagen"] = f"assets/event_running_images/{event['id']}.png"
    
    return event    

def createEvent(event):
    """
    Intenta crear el evento en el intervalo solicitado.
    Si no es posible, busca un intervalo alternativo.

    Args:
        event: El evento a crear.

    Returns:
        tuple: (Exito, FechaInicio, FechaFin).
               Exito es True si se pudo crear en el tiempo original, False si se reprogramó.
    """
    if verifyInterval(event, event["tiempoReal"][0], event["tiempoReal"][1]):
        return (True, toDate(event["tiempoReal"][0]), toDate(event["tiempoReal"][1]))
    else:
        # Buscar tiempo alternativo si el original está ocupado
        hole = joinTime(event)
        dateIni = toDate(hole[0])
        dateEnd = toDate(hole[1])
        event["tiempoReal"] = (hole[0], hole[1])
        return (False, (dateIni, dateEnd), (hole[0], hole[1]))
    