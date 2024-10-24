import tkinter

from prueba import exp_table, log_table, reed_solomon_encode

TABLA_FORMATO = {
    "00000" : "101010000010010",
    "00001" : "101000100100101",
    "00010" : "101111001111100",
    "00011" : "101101101001011",
    "00100" : "100010111111001",
    "00101" : "100000011001110",
    "00110" : "100111110010111",
    "00111" : "100101010100000",
    "01000" : "111011111000100",
    "01001" : "111001011110011",
    "01010" : "111110110101010",
    "01011" : "111100010011101",
    "01100" : "110011000101111",
    "01101" : "110001100011000",
    "01110" : "110110001000001",
    "01111" : "110100101110110",
    "10000" : "001011010001001",
    "10001" : "001001110111110",
    "10010" : "001110011100111",
    "10011" : "001100111010000",
    "10100" : "000011101100010",
    "10101" : "000001001010101",
    "10110" : "000110100001100",
    "10111" : "000100000111011",
    "11000" : "011010101011111",
    "11001" : "011000001101000",
    "11010" : "011111100110001",
    "11011" : "011101000000110",
    "11100" : "010010010110100",
    "11101" : "010000110000011",
    "11110" : "010111011011010",
    "11111" : "010101111101101"
}

MASCARAS_QR = {
    "000" : lambda i, j : (i + j) % 2 == 0,
    "001" : lambda i, _ : i % 2 == 0,
    "010" : lambda _, j : j % 3 == 0,
    "011" : lambda i, j : (i + j) % 3 == 0,
    "100" : lambda i, j : ((i//2) + (j//3)) % 2 == 0,
    "101" : lambda i, j : (i * j) % 2 + (i * j) % 3 == 0,
    "110" : lambda i, j : ((i * j) % 2 + (i * j) % 3) % 2 == 0,
    "111" : lambda i, j : ((i + j) % 2 + (i * j) % 3) % 2 == 0
}

def mostrar_qr(root: tkinter.Tk, qr: list[list]):
    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(0, weight=1)
    for i in range(len(qr)):
        for j in range(len(qr)):
            root.grid_rowconfigure(i, weight=1)
            root.grid_columnconfigure(j, weight=1)
            bit = tkinter.Frame(root, bg= "black" if qr[i][j] == "1" else "white")
            bit.grid(row= i, column= j, sticky= "nsew")

def marcadores_posicion(qr: list[list]):
    for i in range(len(qr) - 7, len(qr)):
        qr[0][-i + len(qr) - 1] = "1"
        qr[-i + len(qr) - 1][6] = "1"
        qr[6][-i + len(qr) - 1] = "1"
        qr[-i + len(qr) - 1][0] = "1"
        qr[0][i] = "1"
        qr[len(qr) - (i + 1)][len(qr) - 1] = "1"
        qr[6][i] = "1"
        qr[len(qr) - (i + 1)][len(qr) - 7] = "1"
        qr[i][0] = "1"
        qr[len(qr) - 1][len(qr) - (i + 1)] = "1"
        qr[i][6] = "1"
        qr[len(qr) - 7][len(qr) - (i + 1)] = "1"
    for i in range(len(qr) - 5, len(qr) - 2):
        for j in range(2, 5):
            qr[j][i] = "1"
            qr[i][j] = "1"
            qr[-i + len(qr) - 1][j] = "1"

def marcador_alineacion(qr: list[list]):
    for i in range(len(qr) - 9, len(qr) - 4):
        qr[len(qr) - 9][i] = "1"
        qr[i][len(qr) - 5] = "1"
        qr[len(qr) - 5][i] = "1"
        qr[i][len(qr) - 9] = "1"
    qr[len(qr) - 7][len(qr) - 7] = "1"

def patrones_temporizacion(qr: list[list]):
    for i in range(8, len(qr) - 8, 2):
        qr[6][i] = "1"
        qr[i][6] = "1"

def esquina_formato(qr: list[list], medio_byte: str):
    indice_byte = 0
    for i in range(len(qr) - 1, len(qr) - 3, -1):
        for j in range(len(qr) - 1, len(qr) - 3, -1):
            qr[i][j] = medio_byte[indice_byte]
            indice_byte += 1

def tam_mensaje(qr: list[list], byte: str):
    indice_byte = 0
    for i in range(len(qr) - 3, len(qr) - 7, -1):
        for j in range(len(qr) - 1, len(qr) - 3, -1):
            qr[i][j] = byte[indice_byte]
            indice_byte += 1

def range_bidimensional(start_i, stop_i, step_i, start_j, stop_j, step_j):
    for i in range(start_i, stop_i, step_i):
        for j in range(start_j, stop_j, step_j):
            yield i, j


def mensaje(qr: list[list], mensaje: list[str], mascara : str):
    restriccion_sup_izq = [(i, j) for i, j in range_bidimensional(0, 9, 1, 0, 9, 1)]
    restriccion_inf_izq = [(i, j) for i, j in range_bidimensional(len(qr) - 8, len(qr), 1, 0, 9, 1)]
    restriccion_sup_der = [(i, j) for i, j in range_bidimensional(0, 9, 1, len(qr) - 8, len(qr), 1)]
    restriccion_inf_der = [(i, j) for i, j in range_bidimensional(len(qr) - 9, len(qr) - 4, 1, len(qr) - 9, len(qr) - 4, 1)]
    restriccion_hor = [(6, i) for i in range(10, len(qr) - 8, 1)]
    restriccion_vert = [(i, 6) for i in range(10, len(qr) - 8, 1)]
    restriccion_total = restriccion_sup_izq + restriccion_inf_izq + restriccion_sup_der + restriccion_inf_der + restriccion_vert + restriccion_hor
    mensaje_en_bits = ''.join(mensaje)
    posicion = (len(qr) - 7, len(qr) - 1)
    maxCol = len(qr) - 1
    cambio = False
    direccion = -1
    for bit in mensaje_en_bits:
        #print(posicion)
        if posicion[1] >= 0:
            if(posicion[0] < 0 or posicion[0] >= len(qr)):
                #print("Cambio de direccion")
                direccion *= -1
                posicion_edit = list(posicion)
                posicion_edit[0] += direccion
                maxCol -= 2
                posicion_edit[1] = maxCol
                posicion = tuple(posicion_edit)
                #print(posicion)
            if posicion not in restriccion_total:
                qr[posicion[0]][posicion[1]] = bit
            elif posicion in restriccion_sup_der:
                #print("Choque superior derecho")
                direccion *= -1
                posicion_edit = list(posicion)
                posicion_edit[0] += direccion
                maxCol -= 2
                posicion_edit[1] = maxCol
                posicion = tuple(posicion_edit)
                #print(posicion)
                qr[posicion[0]][posicion[1]] = bit
            elif posicion in restriccion_inf_der:
                #print("Choque inferior derecho")
                if posicion[1] != len(qr) - 9:
                    #print("Choque con filas dobles")
                    posicion_edit = list(posicion)
                    posicion_edit[0] += (direccion * 5)
                    posicion = tuple(posicion_edit)
                    #print(posicion)
                else:
                    #print("Choque con filas individuales")
                    posicion_edit = list(posicion)
                    posicion = tuple(posicion_edit)
                    posicion_edit[1] -= 1
                    cambio = not cambio
                    posicion = tuple(posicion_edit)
                    #print(posicion)
                qr[posicion[0]][posicion[1]] = bit
            elif posicion in restriccion_hor:
                #print("Choque con restriccion horizontal")
                posicion_edit = list(posicion)
                posicion_edit[0] += direccion
                posicion = tuple(posicion_edit)
                #print(posicion)
                qr[posicion[0]][posicion[1]] = bit
            elif posicion in restriccion_inf_izq:
                #print("Choque con restriccion inferior izquierda")
                if(posicion[0] == len(qr) - 1):
                    #print("Choque inicial")
                    posicion_edit = list(posicion)
                    posicion_edit[0] += (direccion * 8)
                    posicion = tuple(posicion_edit)
                    #print(posicion)
                else:
                    #print("Choque interno")
                    direccion *= -1
                    posicion_edit = list(posicion)
                    posicion_edit[0] += direccion
                    maxCol -= 2
                    posicion_edit[1] = maxCol
                    posicion = tuple(posicion_edit)
                    #print(posicion)
                qr[posicion[0]][posicion[1]] = bit
            elif posicion in restriccion_vert:
                #print("Choque con restriccion vertical")
                posicion_edit = list(posicion)
                maxCol -= 1
                posicion_edit[1] = maxCol
                posicion = tuple(posicion_edit)
                #print(posicion)
                qr[posicion[0]][posicion[1]] = bit
            elif posicion in restriccion_sup_izq:
                #print("Choque con restriccion superior izquierda")
                direccion *= -1
                posicion_edit = list(posicion)
                posicion_edit[0] += direccion
                maxCol -= 2
                posicion_edit[1] = maxCol
                if posicion_edit[1] == 6:
                    posicion_edit[1] -= 1
                posicion = tuple(posicion_edit)
                #print(posicion)
                qr[posicion[0]][posicion[1]] = bit
            
            posicion_edit = list(posicion)
            if cambio:
                posicion_edit[0] += direccion
                posicion_edit[1] = maxCol
            else:
                posicion_edit[1] -= 1
            cambio = not cambio
            posicion = tuple(posicion_edit)
    def mascara_qr(qr: list[list], mascara: str):
        for i in range(len(qr)):
            for j in range(len(qr[0])):
                if (tuple([i, j]) not in restriccion_total) and MASCARAS_QR[mascara](i, j):
                    qr[i][j] = "0" if qr[i][j] == "1" else "1"
    mascara_qr(qr, mascara)

def lineas_formato(qr: list[list], combinacion: str):
    mascaraFormatop = "100000001111100"
    mascaraFormato = TABLA_FORMATO[combinacion]
    indiceBit = 0
    for i in range(6):
        qr[8][i] = mascaraFormatop[indiceBit]
        indiceBit += 1
    qr[8][7] = mascaraFormatop[indiceBit]
    indiceBit += 1
    for i in range(8, -1, -1):
        if i != 6:
            qr[i][8] = mascaraFormatop[indiceBit]
            indiceBit += 1
    indiceBit = 0
    for i in range(1, 8):
        qr[len(qr)- i][8] = mascaraFormato[indiceBit]
        indiceBit += 1
    indiceBit = -1
    for i in range(1, 9):
        qr[8][len(qr) - i] = mascaraFormato[indiceBit]
        indiceBit -= 1

def generar_qr(qr: list[list], arrayBinario: list[str]):
    marcadores_posicion(qr)
    marcador_alineacion(qr)
    patrones_temporizacion(qr)
    qr[len(qr) - 8][8] = "1"
    formato = "0100"
    esquina_formato(qr, formato)
    longitudFormateada = format(len(arrayBinario),"08b")
    tam_mensaje(qr, longitudFormateada)
    arrayBinario = list(map(lambda x: format(x, "08b"), arrayBinario))
    newBin = arrayBinario.copy()
    newBin.insert(0, longitudFormateada)
    newBin.insert(0, formato)
    newBin.append("0000")
    stringQR = ''.join(newBin)
    newBin = [stringQR[i : i + 8] for i in range(0, len(stringQR), 8)]
    newInt = [int(i, 2) for i in newBin]
    encoded = reed_solomon_encode(newInt, 16, exp_table, log_table)
    final = [encoded[i] for i in range(len(newInt), len(encoded))]
    arrayBinario.append("0000")
    arrayBinario += list(map(lambda x: format(x, "08b"), final))
    mensaje(qr, arrayBinario, "011")
    lineas_formato(qr, "00011")

cadena = "www.youtube.com/veritasium"
cadena = "quantumnodelink.store/nose"
arrayBinario = [ord(i) for i in cadena]
codigoqr = [["0" for _ in range(25)] for _ in range(25)]
generar_qr(codigoqr, arrayBinario)
root = tkinter.Tk()
root.geometry("450x450")
root.configure(bg="white")
frame_con_margen = tkinter.Frame(root, width=400, height=400, bg="white")
frame_con_margen.place(relx=0.5, rely=0.5, anchor="center", width=400, height=400)
root.resizable(False, False)
mostrar_qr(frame_con_margen, codigoqr)
root.mainloop()