import heapq
import json
import os
from datetime import datetime

TASKS_FILE = "tareas.json"

class Tarea:
    def __init__(self, nombre, prioridad, dependencias=None, fecha_vencimiento=None):
        self.nombre = nombre
        self.prioridad = int(prioridad)
        self.dependencias = dependencias or []
        self.fecha_vencimiento = fecha_vencimiento

    def es_valida(self):
        if not self.nombre.strip():
            return False
        if not isinstance(self.prioridad, int):
            return False
        return True

    def to_dict(self):
        return {
            "nombre": self.nombre,
            "prioridad": self.prioridad,
            "dependencias": self.dependencias,
            "fecha_vencimiento": self.fecha_vencimiento,
        }

    @staticmethod
    def from_dict(data):
        return Tarea(
            data["nombre"],
            data["prioridad"],
            data.get("dependencias", []),
            data.get("fecha_vencimiento")
        )


class GestorTareas:
    def __init__(self):
        self.tareas = []
        self.cargar_tareas()

    def cargar_tareas(self):
        if os.path.exists(TASKS_FILE):
            with open(TASKS_FILE, "r") as f:
                datos = json.load(f)
                for tarea_dict in datos:
                    tarea = Tarea.from_dict(tarea_dict)
                    heapq.heappush(self.tareas, self._item_para_heap(tarea))

    def guardar_tareas(self):
        with open(TASKS_FILE, "w") as f:
            tareas_serializadas = [t[3].to_dict() for t in self.tareas]
            json.dump(tareas_serializadas, f, indent=4)

    def _item_para_heap(self, tarea):
        fecha = tarea.fecha_vencimiento or "9999-12-31"
        return (tarea.prioridad, fecha, tarea.nombre, tarea)

    def añadir_tarea(self, tarea):
        if not tarea.es_valida():
            raise ValueError("Tarea no válida.")
        heapq.heappush(self.tareas, self._item_para_heap(tarea))
        self.guardar_tareas()

    def mostrar_tareas(self, orden_por="prioridad"):
        tareas_ordenadas = sorted(self.tareas, key=lambda x: (x[0], x[1]) if orden_por == "prioridad" else (x[1], x[0]))
        for _, _, _, tarea in tareas_ordenadas:
            print(f"Tarea: {tarea.nombre}, Prioridad: {tarea.prioridad}, Fecha: {tarea.fecha_vencimiento}, Depende de: {tarea.dependencias}")

    def completar_tarea(self, nombre):
        nuevas_tareas = [t for t in self.tareas if t[3].nombre != nombre]
        if len(nuevas_tareas) == len(self.tareas):
            print("Tarea no encontrada.")
            return
        self.tareas = nuevas_tareas
        heapq.heapify(self.tareas)
        self.guardar_tareas()
        print(f"Tarea '{nombre}' completada.")

    def obtener_siguiente_tarea(self):
        for _, _, _, tarea in self.tareas:
            if not tarea.dependencias or all(
                dep not in [t[3].nombre for t in self.tareas] for dep in tarea.dependencias
            ):
                return tarea
        return None


# ==========================
#        MENÚ SIMPLE
# ==========================
def menu():
    gestor = GestorTareas()
    while True:
        print("\n--- GESTOR DE TAREAS ---")
        print("1. Añadir tarea")
        print("2. Mostrar tareas")
        print("3. Completar tarea")
        print("4. Siguiente tarea prioritaria")
        print("5. Salir")
        opcion = input("Elige una opción: ")

        if opcion == "1":
            nombre = input("Nombre de la tarea: ").strip()
            try:
                prioridad = int(input("Prioridad (entero, menor = más importante): "))
            except ValueError:
                print("Prioridad inválida.")
                continue
            dependencias = input("Dependencias (separadas por coma): ").split(",")
            dependencias = [d.strip() for d in dependencias if d.strip()]
            fecha = input("Fecha de vencimiento (YYYY-MM-DD) o dejar vacío: ").strip()
            if fecha:
                try:
                    datetime.strptime(fecha, "%Y-%m-%d")
                except ValueError:
                    print("Formato de fecha inválido.")
                    continue
            else:
                fecha = None

            tarea = Tarea(nombre, prioridad, dependencias, fecha)
            try:
                gestor.añadir_tarea(tarea)
                print("Tarea añadida correctamente.")
            except ValueError as e:
                print(str(e))

        elif opcion == "2":
            criterio = input("Ordenar por (prioridad/fecha): ").strip().lower()
            if criterio not in ("prioridad", "fecha"):
                criterio = "prioridad"
            gestor.mostrar_tareas(orden_por=criterio)

        elif opcion == "3":
            nombre = input("Nombre de la tarea a completar: ").strip()
            gestor.completar_tarea(nombre)

        elif opcion == "4":
            tarea = gestor.obtener_siguiente_tarea()
            if tarea:
                print(f"Siguiente tarea prioritaria: {tarea.nombre}, Prioridad: {tarea.prioridad}")
            else:
                print("No hay tareas disponibles o hay tareas bloqueadas por dependencias.")

        elif opcion == "5":
            break
        else:
            print("Opción inválida.")

if __name__ == "__main__":
    menu()
