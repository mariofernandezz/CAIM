import enchant
import csv
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# FUncion de ZIPF
def zipf(rango, a, b, c):
    return c/((rango+b)**a)


# Dicionario ingles
di = enchant.Dict("en_GB")
# Guardar frecuencias
freq = []


with open('outNo.csv', 'r', newline='') as input_csv, open('archivo_filtrado.csv', 'w', newline='') as output_csv:
    reader = csv.reader(input_csv)
    writer = csv.writer(output_csv)

    for row in reader:
        if len(row) >= 2:
            cantidad, palabra = row[0], row[1].strip()

            # Verificar si la palabra es válida en inglés
            if di.check(palabra):
                freq.append(int(row[0]))
                writer.writerow([cantidad, palabra])
        
    writer.writerow([len(freq), "words"])

# Rangos de las palabras
freq.sort(reverse=True)
freq = freq[: 750]
rang = [i+1 for i in range(len(freq))]

popt, pcov = curve_fit(zipf, rang, freq, bounds=([0.5, -749.0, 0.0],[1.5, 750.0, 1000000.0]))

plt.xscale('log')     # linear   
plt.yscale('log')     # linear

plt.plot(rang, freq, "r", label = "data")
plt.plot(rang, zipf(rang, *popt),"b--", label = "ideal")

plt.xlabel("RANGO")
plt.ylabel("FRECUENCIA")

print(popt)

plt.title("PALABRAS-FRECUENCIA")
plt.legend()
plt.show()