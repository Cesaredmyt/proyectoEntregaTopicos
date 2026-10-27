# Comparación de modelos: árbol, bosque y red neuronal

# Modelos

| Modelo            | Descripción                                 | Configuración                       |
| ----------------- | ------------------------------------------- | ----------------------------------- |
| Árbol de decisión | Un solo árbol de reglas.                    | `max_depth=8`, `min_samples_leaf=5` |
| Bosque aleatorio  | 300 árboles que votan.                      | `n_estimators=300`                  |
| Red neuronal      | Perceptrón multicapa con números escalados. | capas de 64 y 32 neuronas           |

Los tres usan las mismas 14 columnas de entrada y la misma separación de datos: 80% para entrenar y 20% para probar.

# Datasets

Cada archivo tiene 10,000 envíos.

| Archivo | Moto  | Camioneta | Bicicleta | Dron  | Eskuter | Descripción                                   |
| ------- | ----- | --------- | --------- | ----- | ------- | --------------------------------------------- |
| envios1 | 25.0% | 25.0%     | 25.0%     | 25.0% | —       | Balanceado                                    |
| envios2 | 34.7% | 14.4%     | 26.2%     | 8.6%  | 16.2%   | Incluye un medio nuevo (`eskuter`)            |
| envios3 | 73.7% | 15.8%     | 7.7%      | 2.8%  | —       | Desbalanceado hacia moto                      |
| envios4 | 57.2% | 16.9%     | 18.8%     | 7.1%  | —       | Desbalance leve                               |
| envios5 | 45.8% | 16.8%     | 28.0%     | 9.5%  | —       | Distribución original                         |
| envios6 | 63.1% | 31.9%     | 4.2%      | 0.7%  | —       | Muy desbalanceado: casi sin bicicleta ni dron |

# Predicciones

1. La red neuronal será la más exacta y el árbol será el más barato de mantener, porque es un solo árbol y es ligero.
2. La red será la más afectada por el desbalance, porque no tiene suficientes datos para aprender bien.
3. El bosque podría predecir el `eskuter`, porque varios árboles deciden en conjunto.
4. Para un microservicio conviene el árbol, porque no vale la pena el gasto del bosque si la mejora es pequeña.

# Experimento 1: entrenar y probar con el mismo archivo

## Exactitud

| Archivo | Árbol | Bosque | Red   |
| ------- | ----- | ------ | ----- |
| envios1 | 99.2% | 99.8%  | 99.5% |
| envios2 | 76.0% | 81.0%  | 76.6% |
| envios3 | 94.4% | 95.2%  | 92.0% |
| envios4 | 91.9% | 92.6%  | 87.8% |
| envios5 | 92.1% | 93.2%  | 88.9% |
| envios6 | 95.4% | 95.1%  | 92.4% |

- El bosque fue el más exacto en cinco de seis archivos.
- El árbol y el bosque quedaron separados por menos de 1.2 puntos en todos los archivos, excepto en `envios2`, donde la diferencia fue de 5 puntos.
- La red quedó en último lugar en cuatro archivos (`envios3` a `envios6`) y nunca fue la mejor.

## Costo de cada modelo

|                                | Árbol            | Bosque         | Red              |
| ------------------------------ | ---------------- | -------------- | ---------------- |
| Tamaño del archivo             | 0.01 a 0.02 MB   | 8 a 82 MB      | 0.13 a 0.14 MB   |
| Tiempo de entrenamiento        | 0.1 a 0.2 s      | 0.7 a 1.6 s    | 8 a 19 s         |
| Tiempo de predicción por envío | menos de 0.02 ms | 0.04 a 0.07 ms | menos de 0.04 ms |

Los tiempos dependen de la computadora donde se midieron. Lo útil es la proporción entre modelos.

- **Tamaño:** el bosque pesa de cientos a miles de veces más que el árbol. Su tamaño también cambia con los datos: 8 MB con el dataset balanceado (`envios1`) y 82 MB con el que incluye `eskuter` (`envios2`).
- **Entrenamiento:** la red es la más lenta, aunque su archivo final es pequeño.
- **Predicción:** en los tres casos es una fracción de milisegundo, así que no es un factor de decisión.

## Recall por medio en los archivos desbalanceados

| Archivo | Medio     | Árbol | Bosque | Red   |
| ------- | --------- | ----- | ------ | ----- |
| envios6 | Bicicleta | 77.6% | 67.1%  | 63.5% |
| envios6 | Dron      | 80.0% | 53.3%  | 66.7% |
| envios4 | Dron      | 73.9% | 79.6%  | 79.6% |

En `envios6` el conjunto de prueba tiene unos 15 drones y unas 85 bicicletas, por lo que estos porcentajes cambian mucho con pocos errores.

# Experimento 2: entrenar con `envios5` y probar en todos

Los tres modelos se entrenaron con el 80% de `envios5` y se probaron en cada archivo. En `envios5` se usó el 20% que no se vio.

| Archivo | Árbol | Bosque | Red   |
| ------- | ----- | ------ | ----- |
| envios1 | 95.4% | 98.4%  | 96.4% |
| envios2 | 77.7% | 78.5%  | 75.2% |
| envios3 | 94.5% | 93.7%  | 91.5% |
| envios4 | 92.7% | 91.0%  | 89.2% |
| envios5 | 92.1% | 93.2%  | 88.9% |
| envios6 | 96.2% | 96.1%  | 93.9% |

- Ninguno de los tres puede predecir `eskuter`, porque no estaba en los datos de entrenamiento. Un modelo solo responde con las etiquetas que vio.
- Un modelo entrenado con una distribución distinta pierde exactitud. El árbol entrenado con `envios1` obtiene 99.2% en `envios1`, pero entrenado con `envios5` obtiene 95.4% en el mismo archivo.
- En tres de seis archivos (`envios3`, `envios4` y `envios6`) el árbol queda mejor que el bosque.

# Balanceado contra desbalanceado

- **Balanceado (`envios1`):** los tres modelos superan el 99%. Es el caso más fácil.
- **Desbalanceado (`envios3` y `envios6`):** la exactitud sube a 92% a 95%, pero esa cifra está inflada por la moto, que domina el archivo. El recall de los medios escasos baja: en `envios6`, el dron cae a 53% en el bosque y la bicicleta a 64% en la red.
- La exactitud sola no basta para elegir modelo. Hay que revisar el resultado de cada medio.

# Medio nuevo (`eskuter`)

- **Sin haberlo visto en el entrenamiento:** ningún modelo lo predice. En `envios2` la exactitud baja a 75% a 78% con cualquiera de los tres.
- **Habiéndolo visto (experimento 1):** sigue siendo el medio más difícil, con recall de 63% en el árbol, 56% en la red y 51% en el bosque. Sus reglas se parecen a las de la moto y la bicicleta.
- Para incorporar un medio nuevo, el modelo debe reentrenarse con datos que lo incluyan.

# ¿Se cumplieron las predicciones?

1. **La red sería la más exacta: no se cumplió.** Nunca fue la mejor. **El árbol sería el más barato: se cumplió.** Es el más pequeño y rápido de entrenar. La red, aunque pesa poco, es la que más tarda en entrenar.
2. **La red sería la más afectada por el desbalance: se cumplió en parte.** La red queda por debajo del árbol en la mayoría de los archivos, no solo en los desbalanceados. En `envios6`, el medio con peor resultado fue el dron en el bosque (53%), no en la red (67%).
3. **El bosque podría predecir el `eskuter`: no se cumplió.** Votar entre varios árboles no crea una clase que no se vio en el entrenamiento. Incluso entrenado con ella, el bosque fue el que peor la acertó (51%).
4. **El árbol conviene para el microservicio: se cumplió, con una excepción.** La mejora del bosque es de 1 punto en casi todos los archivos, con un tamaño miles de veces mayor. En `envios2` la mejora fue de 5 puntos.

# Conclusiones

- El bosque es el más exacto en la mayoría de los casos, pero por poco, y es el modelo más pesado.
- El árbol ofrece casi la misma exactitud con un archivo de 10 a 20 KB y entrenamiento casi inmediato. Para un servicio en la nube, un archivo pequeño implica menos memoria y arranque más rápido. Esta conclusión es una inferencia, no se midió el costo real en un servicio.
- La red neuronal no mejoró a los otros dos en este dataset. Con datos tabulares como estos, un modelo más complejo no garantiza mejores resultados.
- La exactitud puede ocultar fallas en los medios poco frecuentes, sobre todo en archivos desbalanceados.
- Si se agrega un medio nuevo, el modelo debe reentrenarse. Con un bosque, cada reentrenamiento produce un archivo de decenas de megas que hay que volver a desplegar.
- Todos los resultados vienen de datos sintéticos, por lo que reflejan las reglas con las que se generaron las etiquetas, no necesariamente la realidad.
