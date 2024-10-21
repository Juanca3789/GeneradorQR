def init_tables():
    # Inicializamos las tablas de logaritmos y antilogaritmos para GF(2^8)
    exp_table = [0] * 512
    log_table = [0] * 256

    x = 1
    for i in range(255):
        exp_table[i] = x
        log_table[x] = i
        x <<= 1
        if x & 0x100:
            x ^= 0x11d

    # Copiamos la primera parte de exp_table para soportar la multiplicación módulo 255
    for i in range(255, 512):
        exp_table[i] = exp_table[i - 255]

    return exp_table, log_table

def gf_mul(x, y, exp_table, log_table):
    # Multiplicación en GF(2^8) usando tablas de logaritmos y antilogaritmos
    if x == 0 or y == 0:
        return 0
    return exp_table[(log_table[x] + log_table[y]) % 255]

def gf_poly_mul(p, q, exp_table, log_table):
    # Multiplicar dos polinomios en GF(2^8)
    result = [0] * (len(p) + len(q) - 1)
    for i in range(len(p)):
        for j in range(len(q)):
            result[i + j] ^= gf_mul(p[i], q[j], exp_table, log_table)
    return result

def gf_poly_div(dividend, divisor, exp_table, log_table):
    # Dividir dos polinomios en GF(2^8)
    result = list(dividend)
    for i in range(len(dividend) - len(divisor) + 1):
        coeff = result[i]
        if coeff != 0:
            for j in range(1, len(divisor)):
                result[i + j] ^= gf_mul(divisor[j], coeff, exp_table, log_table)
    separator = -(len(divisor) - 1)
    return result[:separator], result[separator:]

def reed_solomon_encode(data, nsym, exp_table, log_table):
    # Codificar usando Reed-Solomon para añadir nsym bytes de corrección
    generator = [1]
    for i in range(nsym):
        generator = gf_poly_mul(generator, [1, exp_table[i]], exp_table, log_table)

    # Multiplicamos el polinomio de datos por x^nsym
    data_padded = data + [0] * nsym

    # Calculamos el resto de la división del polinomio de datos por el generador
    _, remainder = gf_poly_div(data_padded, generator, exp_table, log_table)

    # Los bytes de corrección son el residuo de la división
    return data + remainder

# Inicialización de tablas de logaritmos y antilogaritmos
exp_table, log_table = init_tables()