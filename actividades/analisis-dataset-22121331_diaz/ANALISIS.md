# Análisis del dataset de medios de transporte

Nombre: Cesar Enrique Diaz Maldonado
Matrícula: 22121331
Equipo:

---

## Actividad 1 — El retrato del dataset

Código: `actividad1_retrato.py`. Salida completa en `salida_actividad1.txt`.

### Predicción

1. Cuando llueve creo que domina la camioneta, para que no se moje el paquete y tampoco el conductor de la bici o de la moto. El dron sería imposible.
2. Para el centro creo que domina la moto, por la practicidad y porque no esperaría tanto en el tráfico como la camioneta. También puede ser la bicicleta, pero depende del volumen del paquete. El dron no va al centro porque no está despejado.
3. La distancia más larga de una bicicleta creo que es de 7 km.
4. No creo que haya envíos con una etiqueta que rompa las reglas del negocio, porque aunque el modelo prediga algo siempre se deben seguir las reglas, y si las reglas dicen que es imposible no se hace.

### Resultado

Porcentaje de cada medio según el clima:

| clima         | bicicleta | camioneta | dron | moto |
| ------------- | --------- | --------- | ---- | ---- |
| despejado     | 32.8      | 16.6      | 13.5 | 37.1 |
| lluvia        | 8.5       | 16.7      | 0.0  | 74.8 |
| viento_fuerte | 31.7      | 18.4      | 0.0  | 49.9 |

Porcentaje de cada medio según la zona de destino:

| zona        | bicicleta | camioneta | dron | moto |
| ----------- | --------- | --------- | ---- | ---- |
| centro      | 58.4      | 13.5      | 0.0  | 28.0 |
| periferia   | 0.9       | 14.0      | 12.6 | 72.5 |
| residencial | 26.2      | 14.6      | 17.3 | 41.9 |
| rural       | 0.0       | 40.8      | 0.0  | 59.2 |

Máximos por medio:

| medio     | peso_kg | volumen_l | distancia_km |
| --------- | ------- | --------- | ------------ |
| bicicleta | 8.0     | 39.7      | 7.0          |
| camioneta | 80.0    | 400.6     | 59.1         |
| dron      | 2.5     | 12.0      | 15.0         |
| moto      | 24.9    | 90.0      | 39.9         |

Etiquetas que rompen las reglas del negocio (con `es_posible`): **0 de 10 000**.

### Comparación

1. **Fallé.** Con lluvia domina la moto (74.8 %), no la camioneta (16.7 %). La camioneta tiene el mismo porcentaje con lluvia que despejado (16.6 %). No había considerado que la camioneta es la más cara y solo se usa cuando el paquete es pesado, grande, refrigerado o va muy lejos, y eso no cambia con la lluvia. Lo que hace la lluvia es frenar a la bicicleta (baja de 32.8 % a 8.5 %), y esos envíos pasan a la moto. Lo del dron sí lo acerté, con lluvia es 0 %.
2. **Casi.** En el centro gana la bicicleta (58.4 %) y la moto es segunda (28.0 %). El dron es 0 %, pero no por el clima, sino porque el centro es espacio aéreo restringido. Además en el centro las distancias son cortas (máximo 5.9 km), por eso la bicicleta gana.
3. **Acerté.** El máximo de la bicicleta es exactamente 7.0 km.
4. **Acerté.** No hay ninguna etiqueta que rompa las reglas. Pero la razón no es que el modelo respete las reglas: este dataset no lo hizo el modelo, se generó aplicando las reglas primero.

### Preguntas

**¿En qué zonas y con qué climas el dron nunca aparece? ¿Qué regla lo explica?**
En lluvia y en viento fuerte, por la regla de que el dron solo vuela con clima despejado. En el centro, por la regla de espacio aéreo restringido. En zona rural tampoco aparece, pero ahí no es por una regla de zona: las distancias en rural empiezan en 15.9 km y el dron llega máximo a 15 km.

**La bicicleta casi no va a la periferia, aunque ninguna regla se lo prohíbe. ¿Qué otra columna lo explica?**
La distancia. Solo el 2.2 % de los envíos de periferia son de 7 km o menos (su mediana es 15.8 km) y la bicicleta llega máximo a 7 km. Por eso hay solo 18 bicicletas en periferia.

**Comparen los máximos con la tabla LIMITES. ¿Qué límites se pueden adivinar y cuál no?**
Los de bicicleta (8 kg, 40 L, 7 km), moto (25 kg, 90 L, 40 km) y dron (2.5 kg, 12 L, 15 km) se adivinan casi exactos con los máximos. El de la camioneta no: en los datos llega a 80 kg, 400 L y 59 km, pero el límite real es 1000 kg, 3000 L y 1000 km. Nadie manda un paquete tan grande, entonces los datos no lo muestran.

**Más de cien camionetas para viajes de menos de 2 km. ¿Cuántas tienen una razón clara?**
Son 107 en total. 95 tienen al menos una razón clara: 47 por peso mayor a 25 kg, 61 por volumen mayor a 90 L y 36 por ser refrigeradas (algunas cumplen más de una). Las otras 12 no tienen razón clara. Mi explicación es que el dataset cambia el 3 % de las etiquetas por otro medio que también era posible, y la camioneta siempre es posible, así que esos 12 son ruido.

### Para pensar

Sí se pueden construir reglas a partir de los datos, porque los datos siguen un patrón y eso sirve como un comienzo para tener las pautas que necesitamos. La mayoría de las reglas sí se podrían sacar, y también tomando en cuenta cosas lógicas. Las que se vieron claras fueron los límites de cada medio, en km, peso y volumen.

Lo que no se puede sacar: el límite de la camioneta, porque nadie manda paquetes tan grandes y los datos no lo muestran; la regla de que la bicicleta no va a zona rural, porque ahí las distancias ya son mayores de 7 km y la distancia lo explica sola; y los 12 casos raros de camioneta, que son ruido y no una regla.

El riesgo de dejar que el modelo descubra las reglas es que no toma en cuenta cosas lógicas si no se lo decimos, no tiene esa capacidad. Puede aprender el ruido como si fuera una regla, por ejemplo mandar una camioneta a 1 km, o encontrar patrones que son casualidad y que no nos ayudan. Además el modelo solo da probabilidades y no garantiza cumplir una restricción como que el dron no vuela de noche, mientras que una regla escrita a mano se cumple siempre.

---

## Actividad 2 — La hora y el dron

(pendiente)

## Actividad 3 — Anatomía de los errores

(pendiente)

## Actividad 4 — ¿Qué columnas usa de verdad el modelo?

(pendiente)

## Actividad 5 — El dron es minoría: ¿hay que balancear el dataset?

(pendiente)
