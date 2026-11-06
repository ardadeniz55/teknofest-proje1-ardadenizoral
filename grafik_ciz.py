import csv
import matplotlib.pyplot as plt

zaman = []
enlem = []
boylam = []
irtifa = []

with open("ucus_kaydi.csv", "r") as f:
    okuyucu = csv.DictReader(f)
    for satir in okuyucu:
        zaman.append(float(satir["zaman_s"]))
        enlem.append(float(satir["enlem"]))
        boylam.append(float(satir["boylam"]))
        irtifa.append(float(satir["irtifa_m"]))

# Grafikleri çizdirme
plt.figure(figsize=(10, 5))

# 1. Grafik: Yatay Rota (Enlem - Boylam)
plt.subplot(1, 2, 1)
plt.plot(boylam, enlem, label="İHA Rotası", color="blue")
plt.title("Uçuş Rotası (Enlem/Boylam)")
plt.xlabel("Boylam")
plt.ylabel("Enlem")
plt.grid(True)

# 2. Grafik: Zaman - İrtifa Grafiği
plt.subplot(1, 2, 2)
plt.plot(zaman, irtifa, label="İrtifa (m)", color="orange")
plt.title("Zamana Göre İrtifa Değişimi")
plt.xlabel("Zaman (s)")
plt.ylabel("İrtifa (m)")
plt.grid(True)

plt.tight_layout()

# Pencere açmak yerine resim olarak kaydediyoruz!
plt.savefig("ucus_grafigi.png", dpi=300)
print("Grafik başarıyla 'ucus_grafigi.png' olarak kaydedildi!")