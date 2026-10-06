def elegir_medio(km, kg):
    if kg > 25:
        return "camioneta", "paquete pesado (más de 25 kg)"
    if km >= 40:
        return "camioneta", "distancia larga (40 km o más)"
    if km <= 15 and kg < 8:
        return "bicicleta", "distancia corta y paquete ligero"
    return "moto", "distancia media o paquete de peso medio"