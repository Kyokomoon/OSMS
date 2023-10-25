import math
import matplotlib.pyplot as plt

# Входные данные
P_Tx_BS_dBm = 46  # Мощность передатчика BS в dBm
num_sectors = 3  # Число секторов на одной BS
P_Tx_UE_dBm = 24  # Мощность передатчика пользовательского терминала UE в dBm
AntGain_BS_dBi = 21  # Коэффициент усиления антенны BS в дБи
reserve_on_penetrationLoss = 15  # Запас мощности сигнала на проникновения сквозь стены (dB)
reserve_on_interferenceLoss = 1  # Запас мощности сигнала на интерференцию (dB)
F_range = 1.8  # Диапазон частот (Гигагерцы)
UL_bandwidth = 10 * (10**6)  # Полоса частот в uplink (Мегагерцы)
DL_bandwidth = 20 * (10**6) # Полоса частот в downlink (Мегагерцы)
Coefficient_Rx_noise_BS = 2.4  # Коэффициент шума приемника BS (dB)
Coefficient_Rx_noise_UE = 6  # Коэффициент шума приемника пользователя (dB)
SINR_for_DL = 2  # Требуемое отношение SINR для DL (dB)
SINR_for_UL = 4  # Требуемое отношение SINR для UL (dB)
anten_count_BS = 2  # Число приемо-передающих антенн на BS (MIMO)
area_of_coverage_sqkm = 100  # Площадь территории, на которой требуется спроектировать сеть (квадратные километры)
area_of_shopping_centers_sqm = 4  # Площадь торговых и бизнес центров, где требуется спроектировать сеть на базе микро- и фемтосот (квадратные метры)
FeederLoss = 2
MIMOGain = 3
Termal_Noise_UL = -174 + 10* math.log10(UL_bandwidth)
Termal_Noise_DL = -174 + 10* math.log10(DL_bandwidth)
# Расчет бюджета восходящего канала
Rx_Sense_BS = Coefficient_Rx_noise_BS + SINR_for_DL + Termal_Noise_DL
Rx_Sense_AT = Coefficient_Rx_noise_UE + SINR_for_UL + Termal_Noise_UL
MAPL_UL = P_Tx_UE_dBm - FeederLoss + AntGain_BS_dBi + MIMOGain - reserve_on_interferenceLoss - reserve_on_penetrationLoss - Rx_Sense_BS
# Расчет бюджета нисходящего канала
MAPL_DL = P_Tx_BS_dBm - FeederLoss + AntGain_BS_dBi + MIMOGain - reserve_on_interferenceLoss - reserve_on_penetrationLoss - Rx_Sense_AT

# Расстояния между приемником и передатчиком (от 1 до 1000 метров)
distances_m = list(range(1, 6001))

#Модель UMiNLOS
PL_UMiNLOS = []

def S(d, hBS,f):
    if d < 1:
        s = (47.88 + 13.9 * math.log10(f) - 13.9 * math.log10(hBS)) * (1/math.log10(50))
    else:
        s = 44.9-6.55 * math.log10(f)
    return s
#Модель COST231
for i in range(len(distances_m)):
    PL_UMiNLOS.append( 26 * math.log10(F_range) + 22.7 + 36.7 * math.log10(distances_m[i]))
#Выбор местности 
#CLATTER = 'DU'  #плотная городская застройка
CLATTER = 'U'   #город
#CLATTER = 'SU'   #пригород
#CLATTER = 'RURAL'   #сельская местность
#CLATTER = 'ROAD'    #трасса
PL_COST231 = []
A = 46.3
B = 33.9
hBS = 50 #m
hms = 1 #m
f = F_range * 1000 
if CLATTER == 'DU':
    Lclutter = 3
    a = 3.2 * ((math.log10(11.75*hms))**2) - 4.97
elif CLATTER == 'U':
    Lclutter = 0
    a = 3.2 * ((math.log10(11.75*hms))**2) - 4.97
elif CLATTER == 'SU':
    Lclutter = -(2 * ((math.log10(f/28))**2) + 5.4)
    a = (1.1 * math.log10(f)) * hms - (1.56*math.log10(f)-0.8)
elif CLATTER == 'RURAL':
    Lclutter = -(4.78 * ((math.log10(f))**2) - 18.33 * math.log10(f) + 40.94)
    a = (1.1 * math.log10(f)) * hms - (1.56*math.log10(f)-0.8)
elif CLATTER == 'ROAD':
    Lclutter = -(4.78 * ((math.log10(f))**2) - 18.33 * math.log10(f) + 35.94)
    a = (1.1 * math.log10(f)) * hms - (1.56*math.log10(f)-0.8)
else:
    Lclutter = 0
    a = 3.2 * ((math.log10(11.75*hms))**2) - 4.97

for i in range(len(distances_m)):
    PL_COST231.append(A + B * math.log10(f) - 13.82 * math.log10(hBS) - a + S((distances_m[i]/1000),hBS,f) *math.log10(distances_m[i]/1000) + Lclutter)

#Walfish
PL_Walfish = []
for i in range(len(distances_m)):
    PL_Walfish.append(42.6 + 20* math.log10(f) + 26 * math.log10(distances_m[i]/1000))
MAPL_DL_G = [MAPL_DL] * len(distances_m)
MAPL_UL_G = [MAPL_UL] * len(distances_m)


UM_Cross_in_UL = 0
COST_Cross_in_UL = 0
Wall_Cross_in_UL = 0
for i in range(1,len(PL_UMiNLOS)-1):
    if PL_UMiNLOS[i-1] < MAPL_UL and PL_UMiNLOS[i+1] > MAPL_UL:
        UM_Cross_in_UL = i
        
    if PL_COST231[i-1] < MAPL_UL and PL_COST231[i+1] > MAPL_UL:
        COST_Cross_in_UL = i
        
    if PL_Walfish[i-1] < MAPL_UL and PL_Walfish[i+1] > MAPL_UL:
       Wall_Cross_in_UL = i
        
UM_Cross_in_DL = 0
COST_Cross_in_DL = 0
Wall_Cross_in_DL = 0
for i in range(1,len(PL_UMiNLOS)-1):
    if PL_UMiNLOS[i-1] < MAPL_DL and PL_UMiNLOS[i+1] > MAPL_DL:
        UM_Cross_in_DL = i
        
    if PL_COST231[i-1] < MAPL_DL and PL_COST231[i+1] > MAPL_DL:
        COST_Cross_in_DL = i
        
    if PL_Walfish[i-1] < MAPL_DL and PL_Walfish[i+1] > MAPL_DL:
       Wall_Cross_in_DL = i



UM_Cross = [0]*len(distances_m)
if UM_Cross_in_UL > 0:
    UM_Cross[UM_Cross_in_UL] = PL_UMiNLOS[UM_Cross_in_UL]
COST_Cross = [0]*len(distances_m)
if COST_Cross_in_UL > 0:
    COST_Cross[COST_Cross_in_UL] = PL_COST231[COST_Cross_in_UL]

Wall_Cross = [0]*len(distances_m)
if Wall_Cross_in_UL > 0:
    Wall_Cross[Wall_Cross_in_UL] = PL_Walfish[Wall_Cross_in_UL]


if num_sectors == 3:
    S_sot_UM = 1.95 * ((UM_Cross_in_UL/1000)**2)
    S_sot_COST = 1.95 * ((COST_Cross_in_UL/1000)**2)
elif num_sectors == 2:
    S_sot_UM = 1.73 * ((UM_Cross_in_UL/1000)**2)
    S_sot_COST = 1.73 * ((COST_Cross_in_UL/1000)**2)
else:
    S_sot_UM = 2.6 * ((UM_Cross_in_UL/1000)**2)
    S_sot_COST = 2.6 * ((COST_Cross_in_UL/1000)**2)




Count_sot_UM = math.ceil((area_of_shopping_centers_sqm) / S_sot_UM)
Count_sot_COST = math.ceil((area_of_coverage_sqkm) / S_sot_COST)
# Построение графиков
plt.figure(figsize=(10, 6))
plt.plot(distances_m, PL_UMiNLOS, label='UMiNLOS', linestyle='-',color = 'g')
plt.plot(distances_m, PL_COST231, label='COST231: ' + CLATTER, linestyle='-', color = 'r')
plt.plot(distances_m, PL_Walfish, label='Walfish', linestyle='-',color = 'y')
plt.plot(distances_m, MAPL_DL_G, label='MAPL_DL',linestyle='dashed', color='b')
plt.plot(distances_m, MAPL_UL_G, label='MAPL_UL',linestyle='dashed', color='black')
plt.stem(distances_m, UM_Cross)
plt.stem(distances_m, COST_Cross)
plt.stem(distances_m, Wall_Cross)
plt.xlabel('Расстояние между приемником и передатчиком (метры)')
plt.ylabel('Входные потери радиосигнала (дБ)')
plt.title('Зависимость входных потерь радиосигнала от расстояния')
plt.legend()
plt.grid(True)

plt.show()

print("выбрана следующая местность: ", CLATTER)
print("радиус базовой станции для модели UMiNLOS" , UM_Cross_in_UL, 'm')
print("радиус базовой станции для модели COST231", COST_Cross_in_UL,'m')
print("радиус базовой станции для модели Wallfish", Wall_Cross_in_UL, 'm')
print("Площадь базовой станции UMiNLOS", S_sot_UM, 'km2')
print("Площадь базовой станции COST231", S_sot_COST, 'km2')
print("Количество базовых станций для  UMiNLOS: ",Count_sot_UM)
print("Количество базовых станций для COST231: ",Count_sot_COST)


