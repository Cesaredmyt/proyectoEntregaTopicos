# Actividad — Monolito con API frente a microservicios

Nombre: Adrián Martínez Ortiz
Matrícula:22121308
Equipo:

## 1. Clasificar la plataforma actual

```
 CLIENTES (piden por HTTP y reciben JSON)
 +-----------------------------------+   +-----------------------------------+
 | Navegador                         |   | App móvil (cliente_movil.py)      |
 | abre /entregas/cliente/           |   | GET http://127.0.0.1:8000         |
 | su JS hace fetch a la URL         |   |     /entregas/cotizar/?km=..&kg=..|
 | /entregas/cotizar/?km=..&kg=..    |   |                                   |
 +-----------------+-----------------+   +-----------------+-----------------+
                   |                                       |
                   +-------------------+-------------------+
                                       |  HTTP, localhost:8000
                                       v
                        +-------------------------------+
                        | balanceador: nginx            |
                        | puerto 8000 -> 80             |
                        | proxy_pass http://django      |
                        +---------------+---------------+
                                        |  reparte entre 3 copias
                                        v
 +----------------------------------------------------------------------+
 | web x3  (replicas: 3, la MISMA imagen "plataforma-entregas")         |
 |                                                                      |
 | proceso: gunicorn plataforma.wsgi:application --workers 2            |
 |                                                                      |
 | un solo programa Django:                                             |
 |   urls.py -> views.py --+--> reglas.py        (/cotizar/)            |
 |                         +--> recomendador.py  (/recomendar/)         |
 |                         |      +--> modelo_medios.joblib (en RAM)    |
 |                         +--> models.py        (/ultimo/, /visitas/)  |
 +----------------------------------+-----------------------------------+
                                    |  psycopg (POSTGRES_HOST=db)
                                    v
                      +-------------------------------+
                      | db: postgres:16 (una sola)    |
                      +-------------------------------+
```

- **Cliente:** el navegador `/entregas/cliente/` y la app móvil `cliente_movil.py`. Ninguno tiene reglas de negocio, solo mandan km y kg y muestran lo que contesta el servidor.
- **Proceso en el servidor:** `gunicorn plataforma.wsgi:application --bind 0.0.0.0:8000` (CMD del `Dockerfile`), corriendo en cada una de las 3 copias de `web`, con nginx adelante y Postgres atrás. En desarrollo es `python manage.py runserver` con SQLite, un solo proceso.
- **URL que usa el front:** una URL relativa, `/entregas/cotizar/?km=..&kg=..` (`cliente.html`, `fetch`), o sea el mismo origen que le entregó la página. Con docker-compose eso es `http://localhost:8000/...`, que entra por nginx. La app móvil usa la absoluta `http://127.0.0.1:8000/entregas/cotizar/` (`cliente_movil.py`, `BASE`).

**Clasificación**: es un monolito + API, porque todo el backend es un solo proyecto Django que se despliega como una unidad y expone sus reglas y el modelo como endpoints JSON que consumen la web y la móvil.

**Evidencia:**

1. **Un solo comando de arranque y una sola imagen.** El Dockerfile termina en `CMD ["gunicorn", "plataforma.wsgi:application", ...]` y en `docker-compose.yml` tanto `web` como `migrar` salen de la misma imagen. Las 3 réplicas son copias idénticas del mismo código que comparten la misma base Postgres.
2. **El modelo se llama como una función, no como un servicio.** views.recomendar hace `obtener_recomendador().sugerir(paquete)` y  carga el modelo con `joblib.load` desde `entregas/modelo/modelo_medios.joblib`. No hay ninguna petición HTTP a otro servicio, y en `plataforma/` y `entregas/` no se importa requests.
3. **Por qué "con API" y no monolito clásico.** El servidor contesta JsonResponse, y `cliente.html` solo hace fetch y pinta el JSON (hasta tiene el comentario "la regla vive en el backend"). El mismo endpoint `/entregas/cotizar/` lo consumen la web y la app móvil. Un monolito clásico armaría el HTML completo en el servidor con el resultado ya puesto.

## 2. La trampa de los endpoints

Según la laectura y con respecto a la respuesta anterior tener varios endpoints no es tener microservicios. `/entregas/hola/` y `/entregas/recomendar/` son dos vistas de views.py y dos rutas de `entregas/urls.py` del mismo proyecto Django, atendidas por el mismo gunicorn, con la misma imagen y la misma Postgres: si se redespliega una, se redespliega la otra. Que el HTML esté aparte (aunque lo sigue sirviendo el mismo Django) solo muestra que hay una API, que separa a quien pide (navegador, móvil) de quien contesta. Los microservicios parten el servidor en varios programas, cada uno con su proceso, su despliegue y sus datos, que se hablan entre sí por red. Para que `recomendar` lo fuera tendría que correr aparte y que otro servidor lo llamara por HTTP, y aquí es una función que se llama dentro del mismo proceso.

## 3. La misma operación en dos mundos

Caso: el paquete sale a las 3:00. El modelo prefiere dron, pero las reglas no dejan que el dron salga de noche, así que al final se queda con moto.

**Hoy, con monolito + API**

```
POST /entregas/recomendar/
  -> nginx -> una copia de web (gunicorn)
  -> views.recomendar
       -> recomendador  (import)
            -> reglas   (import)
       -> medios        (import)
  <- JSON {medio, motivo, plan}
```

El cliente manda un POST a `/entregas/recomendar/` con los datos del paquete en JSON. La petición pasa por nginx, pas a Django y este busca la ruta en `plataforma/urls.py` y luego en `entregas/urls.py`, y llega a la vista `recomendar` de `views.py`, que revisa que vengan todos los campos y que los números sean números.

Ahí la vista llama al `recomendador`: el árbol pone primero al dron, pero antes de aceptarlo le pregunta a `reglas` (`es_posible`), que lo rechaza porque son las 3 de la mañana. Sigue con la moto, que sí cumple, y esa es la que se queda, con el motivo "se descartó dron por las reglas del negocio". Luego la vista le pide a `medios` (`crear_medio`) que calcule los minutos y la indicación de la moto, y regresa todo en un JSON con `medio`, `motivo` y `plan`.

Todo ese trabajo pasa en memoria, dentro del mismo proceso, porque son import y llamadas a funciones. Entre `views`, `recomendador`, `reglas` y `medios` no hay ninguna llamada de red. Los únicos saltos de red son los de la petición que entra y la respuesta que sale.

**Si `recomendador` fuera otro servicio**

```
POST /entregas/recomendar/
  -> nginx -> Pedidos
       -> (HTTP) servicio recomendador, otro servidor
       <- (HTTP) respuesta, o error, o nada
  <- JSON
```

Pedidos sería lo que hoy es la vista: recibe la petición igual, pero ya no tiene el árbol. Tendría que hacer una llamada HTTP a otro servidor y esperar a que le conteste. Eso son saltos de red nuevos, de ida y vuelta, y más lentos que un `import`. Además, como `reglas` es lo que descarta al dron, o se copia dentro del servicio nuevo o se pide a otro servicio más, que sería otro salto.

Lo más importante es que ahora puede pasar que Pedidos esté bien y el recomendador no: que se tarde, se caiga o regrese un error. Pedidos tendría que decidir qué hacer: ponerle un tiempo máximo de espera, reintentar una vez, usar un plan B (por ejemplo las reglas simples de `elegir_medio`, sin IA, o mandar una camioneta por defecto) o contestar un error claro tipo 503 pidiendo que intenten de nuevo. En el monolito nada de eso existe, porque con un `import` no hay a quién esperarle: si algo falla, falla todo junto.

## 4. Decisión de la empresa

Recomiendo extraer solo el servicio de IA y dejar todo lo demás como está.

1. **Cambian a distinto ritmo.** El modelo se reentrena cada semana y los pedidos casi no cambian. Hoy cada modelo nuevo obliga a reconstruir la imagen y redesplegar  aunque pedidos no haya cambiado. Con el servicio aparte solo se actualiza la IA.
2. **El modelo es lo más pesado.** Con 50 MB cargados por cada worker de gunicorn (3 copias × 2 workers) serían unos 300 MB, más scikit-learn y pandas en la imagen, y pedidos no necesita nada de eso. Aparte, se le da a la IA la memoria que pide sin inflar lo demás.
3. **Partir todo no se justifica.** Si pedidos es estable, separarlo (y notificaciones, etc.) solo trae más red, más cosas que desplegar y más fallas a medias, sin ninguna ganancia.

## 5. Un solo corte

El microservicio es el servicio de recomendación (IA).

- **Se lleva:** `recomendador.py`, el modelo `entregas/modelo/modelo_medios.joblib` y las librerías que solo usa él (scikit-learn, pandas, joblib). Contestaría solo el ranking de medios con su confianza, sin el ciclo que filtra con `es_posible`, que se pasa a la vista.
- **Se queda en pedidos:** `views.py`, `urls.py`, `models.py`, la base de datos, `medios.py` y `reglas.py` completo. La vista recibe el ranking y aplica `es_posible` para quedarse con el primer medio que sí se pueda. `reglas.py` se queda porque son reglas del negocio (límites de cada medio) que cambian cuando cambia el negocio y no cuando se reentrena el modelo, y porque `elegir_medio` es el plan B si la IA no responde. `medios.py` solo calcula el plan cuando el medio ya está decidido.
- **Por qué este corte y no un servicio por archivo:** se corta por lo que sí es distinto, que es el modelo (pesado, cambia cada semana y trae sus propias librerías), no por archivos. `reglas.py` y `medios.py` son funciones chicas que cambian junto con pedidos, y volverlas servicios haría que una sola petición diera varios saltos de red por algo que hoy es un `import`.