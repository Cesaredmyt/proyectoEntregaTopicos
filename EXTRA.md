# EXTRA — Retos sobre la ruta de Django

## Integrantes

1. Cesar Enrique Díaz Maldonado
2. (nombre completo)
3. (nombre completo)
4. (nombre completo)
5. (nombre completo)

---

## Reto 1 — La ruta en todas las computadoras

Cada integrante clonó el repositorio, creó su propio entorno virtual, instaló las dependencias con `pip install -r requirements.txt` y arrancó el servidor con `python manage.py runserver`.

### Resumen

| Integrante                   | Sistema operativo | Entorno virtual activo | Captura de `/entregas/estado/`               |
| ---------------------------- | ----------------- | ---------------------- | -------------------------------------------- |
| Cesar Enrique Díaz Maldonado | Windows           | Sí                     | [captura](evidencias/reto1-cesar-estado.png) |
| (integrante 2)               | (pendiente)       | (pendiente)            | (pendiente)                                  |
| (integrante 3)               | (pendiente)       | (pendiente)            | (pendiente)                                  |
| (integrante 4)               | (pendiente)       | (pendiente)            | (pendiente)                                  |
| (integrante 5)               | (pendiente)       | (pendiente)            | (pendiente)                                  |

### Evidencias de Cesar Enrique Díaz Maldonado

Comandos usados (Windows, `cmd`):

```
git clone https://github.com/Cesaredmyt/proyectoEntregaTopicos.git
cd proyectoEntregaTopicos
py -3.12 -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
python -c "import sys; print(sys.prefix)"
python manage.py runserver
```

Salida de `python -c "import sys; print(sys.prefix)"` con el entorno activo:

```
C:\Users\dcesa\OneDrive\Documents\Tec\Topicos Web y Movil\Proyectos\proyectoEntregaTopicos\proyectoEntregaTopicos\.venv
```

El servidor arrancó y respondió `GET /entregas/estado/ HTTP/1.1 200`:

![Respuesta de /entregas/estado/](evidencias/reto1-cesar-estado.png)

### Evidencias de los demás integrantes

(Agregar aquí, por cada integrante: su nombre, la salida de `sys.prefix` y su captura de `/entregas/estado/`.)

### Diferencias entre sistemas operativos

---

## Reto 2 — Una cotización que entrega datos

(pendiente)

## Reto 3 — Dos clientes, un solo backend

(pendiente)

## Reto 4 — Réplicas: hacerlo fallar y arreglarlo

(pendiente)

## Reto 5 — Casos para pensar

(pendiente)
