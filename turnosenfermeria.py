import numpy as np


class TurnosEnfermeria:

    def __init__(self, enfermers, preferencias,numSemanas=1):
        """
        :params 
                enfermers: lista con los nombres de cada miembro del equipo de enfermería
                preferencias: lista con las preferencias de turnos de cada uno de los miembros del equipo de enfermería.
                factorPenalizacionRestriccionDura: factor de penalización para las restricciones "duras"
                numSemanas: numero de semanas sobre las que se quiere crear el calendario.
        """
        self.factorPenalizacionRestriccionDura = 2.13
        
        '''
            Estas constantes las tiene que leer de un archivo de configuración
        '''
        # lista de enfermera/os:
        self.enfermers = enfermers

        # preferencia de cada una de la/os enfermera/os [mañana,tarde,noche]:
        self.preferenciaTurnos = preferencias

        # minimo y maximo de turnos necesarios para mantener el servicio [mañana,tarde,noche]
        self.minTurnosDia = [4, 3, 2]
        self.maxTurnosDia = [6, 5, 4]

        # máximo numero de turnos por semana de cada enfermera/o
        self.maxTurnosSemana = 5

        # número de semanas sobre las que se quiere crear el calendario:
        self.semanas = numSemanas

        # numero de turnos por día:
        self.turnosPorDia = len(self.minTurnosDia)
        
        # numero de turnos por semana:
        self.turnosPorSemana = 7 * self.turnosPorDia

    def __len__(self):
        """
        :return: el número de turnos en el calendario
        """
        return len(self.enfermers) * self.turnosPorSemana * self.semanas


    def getCoste(self, calendario):
        """
        Calcula el coste total de las infraciones que se produzcan en el calendario.
        ...
        :param calendario: lista de valores binarios que describen un calendario.
        :return: el coste total (tupla)
        """

        if len(calendario) != self.__len__():
            raise ValueError("el tamaño del calendario debe ser igual a: ", self.__len__())

        
        turnosEnfermDict = self.getTurnosEnfermeria(calendario)

        
        infracionesTurnosConsecutivos = self.countInfracionesTurnosConsecutivos(turnosEnfermDict)
        infracionesTurnosMismoDia = self.countInfracionesTurnosMismoDia(turnosEnfermDict)
        infraccionesTurnosPorSemana = self.countInfraccionesTurnosPorSemana(turnosEnfermDict)[1]
        infraccionesEnfermerPorTurno = self.countInfraccionesEnfermerPorTurno(turnosEnfermDict)[1]
        infraccionesPreferenciaTurnos = self.countInfraccionesPreferenciaTurnos(turnosEnfermDict)[1]

        
        infraccionesRestriccionesHard = infracionesTurnosConsecutivos + infracionesTurnosMismoDia + infraccionesEnfermerPorTurno + infraccionesTurnosPorSemana
        infraccionesRestriccionesSoft = infraccionesPreferenciaTurnos

        return self.factorPenalizacionRestriccionDura * infraccionesRestriccionesHard + infraccionesRestriccionesSoft,

    def getTurnosEnfermeria(self, calendario):
        """
        Convierte el calendario en un diccionario con un calendario específico para cada enfermer@
        :param calendario: lista de valores binarios en los que se encuentran los datos del calendario
        :return: un diccionario con el ID de cada enfermer@ como clave y sus turnos correspondientes como valor.
        """
        turnoPorEnfermer = self.__len__() // len(self.enfermers)
        turnosEnfermDict = {}
        indiceTurno = 0

        for enfermer in self.enfermers:
            turnosEnfermDict[enfermer] = calendario[indiceTurno:indiceTurno + turnoPorEnfermer]
            indiceTurno += turnoPorEnfermer

        return turnosEnfermDict

    def countInfracionesTurnosConsecutivos(self, turnosEnfermDict):
        
        """
        Cuenta el numero de infracciones por turnos consecutivos que se encuentrarn en un calendario
        :param turnosEnfermDict: diccionario con el turno específico de un enfermer@
        :return: numero de infracciones encontradas
        """
        infracciones = 0
        # interamos en cada enfermer@
        for turnosEnferm in turnosEnfermDict.values():
            # buscamos dos 1s consecutivos:
            for turno1, turno2 in zip(turnosEnferm, turnosEnferm[1:]):
                if turno1 == 1 and turno2 == 1:
                    infracciones += 1
        return infracciones
    
    def countInfracionesTurnosMismoDia(self, turnosEnfermDict):
        
        """
        Cuenta el numero de infracciones por turnos en el mismo día que se encuentran en un calendario
        :param turnosEnfermDict: diccionario con el turno específico de un enfermer@
        :return: numero de infracciones encontradas
        """
        infracciones = 0
        # interamos en cada enfermer@
        for enferm in turnosEnfermDict: 
            turnosTotalesEnfer=turnosEnfermDict[enferm]
            indiceTurno=0
            for _ in range((7 * self.semanas)):
                turno=turnosTotalesEnfer[indiceTurno:indiceTurno+self.turnosPorDia]
                if turno[0]==1 & turno[2]==1:
                    infracciones += 1
                indiceTurno+=self.turnosPorDia
        return infracciones
   

    def countInfraccionesTurnosPorSemana(self, turnosEnfermDict):
        """
        Cuenta el numero de infracciones debidas al maximo numero de turnos por semana 
        :param turnosEnfermDict: diccionario con el turno específico de un enfermer@
        :return: numero de infracciones encontradas
        """
        infracciones = 0
        listaTurnosSemanales = []
        for turnosEnferm in turnosEnfermDict.values():  
            for i in range(0, self.semanas * self.turnosPorSemana, self.turnosPorSemana):
                turnosSemanales = sum(turnosEnferm[i:i + self.turnosPorSemana])
                listaTurnosSemanales.append(turnosSemanales)
                if turnosSemanales > self.maxTurnosSemana:
                    infracciones += turnosSemanales - self.maxTurnosSemana

        return listaTurnosSemanales, infracciones

    def countInfraccionesEnfermerPorTurno(self, turnosEnfermDict):
        """
        Cuenta el numero de infracciones debidas al numero de enfermer@s por turno
        :param turnosEnfermDict: diccionario con el turno específico de un enfermer@
        :return: numero de infracciones encontradas
        """
        # sumamos los turnos de todas las enfermeras:
        listaTotalPorTurno = [sum(turno) for turno in zip(*turnosEnfermDict.values())]

        infracciones = 0
        # iteramos en los turnos y obtenemos las infracciones:
        for indiceTurno, numDeEnfermer in enumerate(listaTotalPorTurno):
            indiceTurnoDiario = indiceTurno % self.turnosPorDia  # -> 0, 1, o 2 para los tres turnos al dia
            if (numDeEnfermer > self.maxTurnosDia[indiceTurnoDiario]):
                infracciones += numDeEnfermer - self.maxTurnosDia[indiceTurnoDiario]
            elif (numDeEnfermer < self.minTurnosDia[indiceTurnoDiario]):
                infracciones += self.minTurnosDia[indiceTurnoDiario] - numDeEnfermer

        return listaTotalPorTurno, infracciones

    def countInfraccionesPreferenciaTurnos(self, turnosEnfermDict):
        """
        Cuenta el numero de infracciones debidas a las preferencias de turno de cada enfermer@
        :param turnosEnfermDict: diccionario con el turno específico de un enfermer@
        :return: numero de infracciones encontradas
        """
        listaInfraccionesPreferencias = []
        infracciones = 0
        for indiceEnfermer, turnoPreferencia in enumerate(self.preferenciaTurnos):
            # se incluye la preferencia de turnos a lo largo de todo el calendario
            preferencia = turnoPreferencia * (self.turnosPorSemana // self.turnosPorDia)
            turnos = turnosEnfermDict[self.enfermers[indiceEnfermer]]
            listaInfraccionesPreferencias.append(0)
            for pref, turno in zip(preferencia, turnos):
                if pref == 0 and turno == 1:
                    infracciones += 1
                    listaInfraccionesPreferencias[indiceEnfermer]+=1

        return listaInfraccionesPreferencias, infracciones

    def mostrarInfoCalendario(self, calendario):
        """
        Imprime los detalles del calendario y las infracciones de ese calendario
        :param calendario: lista de valores binarios que describen un calendario.
        """
        diccionarioEnfermers = self.getTurnosEnfermeria(calendario)

        print("Calendario de cada enfermer@:")
        for enferm in diccionarioEnfermers: 
            turnosTotalesEnfer=diccionarioEnfermers[enferm]
            indiceTurno=0
            cadenaTurnos=""
            for _ in range((7 * self.semanas)):
                turno=turnosTotalesEnfer[indiceTurno:indiceTurno+self.turnosPorDia]
                if turno[0]==1:
                    if turno[2]==1:
                        cadenaTurnos=cadenaTurnos+"D "
                    else:
                        cadenaTurnos=cadenaTurnos+"M "
                elif turno[1]==1:
                    cadenaTurnos=cadenaTurnos+"T "
                elif turno[2]==1:
                    cadenaTurnos=cadenaTurnos+"N "
                else:
                    cadenaTurnos=cadenaTurnos+"L "
                indiceTurno+=self.turnosPorDia
            print(enferm, ":", cadenaTurnos)
        print()
        print("Infracciones por turnos consecutivos = ", self.countInfracionesTurnosConsecutivos(diccionarioEnfermers))
        print()

        print()
        print("Infracciones por turnos el mismo día = ", self.countInfracionesTurnosMismoDia(diccionarioEnfermers))
        print()

        listaInfraccionesTurnosPorSemana, infracciones = self.countInfraccionesTurnosPorSemana(diccionarioEnfermers)
        print("Turnos por semana = ", listaInfraccionesTurnosPorSemana)
        print("Infracciones de turnos por semana = ", infracciones)
        print()

        listaInfraccionesEnfermerPorTurno, infracciones = self.countInfraccionesEnfermerPorTurno(diccionarioEnfermers)
        print("Enfermer@ por turno = ", listaInfraccionesEnfermerPorTurno)
        print("Infracciones por enfermer@ por turno = ", infracciones)
        print()

        listaInfraccionesPreferenciaTurnos, infracciones = self.countInfraccionesPreferenciaTurnos(diccionarioEnfermers)
        print("Preferencias no cumplidas: ",listaInfraccionesPreferenciaTurnos)
        print("Infracciones por preferencias de turnos = ", infracciones)
        print()