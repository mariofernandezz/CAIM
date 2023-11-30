import enchant
import csv
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit


# Funcion de HEAPS
def heaps(i, k, b):
    return k*(i**b)

# Dicionario ingles
di = enchant.Dict("en_GB")

# Guardar frecuencias
freq = []
numTotal = []
numDiff = []

for i in range(1, 7):
    nom = "out" + str(i) + ".csv"
    with open(nom, 'r', newline='') as input_csv, open('archivo_filtrado.csv', 'w', newline='') as output_csv:
        reader = csv.reader(input_csv)
        writer = csv.writer(output_csv)
        count = 0

        for row in reader:
            
            if len(row) == 2:
                cantidad, palabra = row[0], row[1].strip()

                # Verificar si la palabra es válida en inglés
                if di.check(palabra):
                    freq.append(int(row[0]))
                    writer.writerow([cantidad, palabra])
                    count = count + int(cantidad)
            elif (row[0] == "--------------------"): 
                numTotal.append(count)
                numDiff.append(len(freq))   
            
        writer.writerow([len(freq), "words"])


popt, pcov = curve_fit(heaps, numDiff, numTotal)

plt.xscale('linear')     # linear   
plt.yscale('linear')     # linear

plt.plot(numDiff, numTotal, "r", label = "data")
plt.plot(numDiff, heaps(numDiff, *popt),"b--", label = "ideal")

plt.xlabel("PALABRAS")
plt.ylabel("PALABRAS DISTINTAS")

print(popt)

plt.title("LEY DE HEAPS")
plt.legend()
plt.show()