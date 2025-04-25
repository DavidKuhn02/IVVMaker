import serial
import time
import numpy as np
import matplotlib.pyplot as plt
from scipy import constants
import matplotlib.lines as mlines
from matplotlib.animation import FuncAnimation

# Prefixes
centi = float(1e-2)
milli = float(1e-3)
mu = float(1e-6)
nano = float(1e-9)
pico = float(1e-12)
femto = float(1e-15)

# Units
mm2 = pow(milli, 2)  # mm²
ccm = pow(centi, 3)  # cm³

# Physics constants
epsilon_Si = float(11.7)  # permitivitty of Silicon

# Define measurement parameters
Frequency = [20, 25, 30, 36, 40, 45, 50, 60, 72, 80, 90, 100, 120, 150, 180, 200, 250, 300, 360, 400, 450, 500, 600, 720, 800, 900, 1000, 1200, 1500, 1800, 2000, 2500, 3000, 3600, 4000, 4500, 5000, 6000, 7500, 8000, 9000, 10000, 12000, 15000, 18000, 20000, 25000, 30000, 36000, 40000, 45000, 50000, 60000, 72000, 80000, 90000, 100000, 120000, 150000, 180000, 200000]
#Frequency = [200, 250, 300, 360, 400, 450, 500, 600, 720, 800, 900, 1000, 1200, 1500, 1800, 2000, 2500, 3000, 3600, 4000, 4500, 5000, 6000, 7500, 8000, 9000, 10000, 12000, 15000, 18000, 20000, 25000, 30000, 36000, 40000, 45000, 50000, 60000, 72000, 80000]
#Frequency = [20,100,500,1000,1500]
# Define plot
fig, ax1 = plt.subplots(figsize=(10, 10))
plt.xlim(10., 2.5e5)
plt.grid(True, which='both')
ax1.set_xlabel('f [kHz]')
ax1.set_ylabel('Z [kOhm]', color='r')
ax1.tick_params('y', labelcolor='r')
ax1.set_xscale('log')
ax1.set_yscale('log')
#plt.ylim(0, 100000)

axtwin1 = ax1.twinx()  # instantiate a second Axes that shares the same x-axis
axtwin1.set_ylabel('phi[°]', color='b')  # we already handled the x-label with ax1
axtwin1.tick_params(axis='y', labelcolor='b')
#plt.ylim(-180, 180)
plt.title('Bode diagram')
fig.tight_layout()  # otherwise the right y-label is slightly clipped

# File to save data
data_file = "S_MP_W07_05_CGR_-20_-60.00V.txt"
#data_file = "Cond_lila_C_R_3.txt"
#data_file = "Test2.txt"
with open(data_file, "w") as file:
    file.write("Frequency (Hz),Impedance (kOhm),Phase (°)\n")
    #file.write("Frequency (Hz), Capacity (F), Resistor (kOhm)\n")
    file.write(" 33 nF, 10kOhm,-10V, Board\n")
reward = 0

def save_to_file(F, Z, phi):
    with open(data_file, "a") as file:
        file.write(f"{F} , {Z} , {phi}\n")
        
def open_hm8118(port, command, baudrate=9600, timeout=1):
    try:
        ser = serial.Serial(port, baudrate, timeout=timeout)
        print(f"Verbunden mit {port} bei {baudrate} Baud.")
        ser.write(command.encode())
        time.sleep(0.5)  # Kurze Pause für Antwort
        response = ser.readline().decode().strip()
        return response
    except serial.SerialException as e:
        print(f"Fehler bei der seriellen Kommunikation: {e}")
        return None

def write_hm8118(port, command, baudrate=9600, timeout=1):
    try:
        ser.write(command.encode())
        return 0
    except serial.SerialException as e:
        print(f"Fehler bei der seriellen Kommunikation: {e}")
        return None

def read_hm8118(port, command, baudrate=9600, timeout=1):
    try:
        ser.write(command.encode())
        response = ser.readline().decode().strip()
        return response
    except serial.SerialException as e:
        print(f"Fehler bei der seriellen Kommunikation: {e}")
        return None

def readData_hm8118(port, command, baudrate=9600, timeout=1):
    result = [0., 0., 0]
    try:
        ser.write(command.encode())
        time.sleep(0.5)
        response = ser.readline().decode().strip()
        print(f"Raw response: '{response}'")
        if not response:
            print("Warning: Empty response from the device")
            return None
        string_values = response.split(',')
        result = (float(string_values[0]), float(string_values[1]), int(string_values[2]))
        return result
    except (serial.SerialException, ValueError, IndexError) as e:
        print(f"Fehler bei der seriellen Kommunikation oder Datenverarbeitung: {e}")
        return None

# Updates the data and graph
def update(freq):
    freq_string = "FREQ {0}\r\n".format(freq)
    data = write_hm8118(port, freq_string)
    data = read_hm8118(port, "FREQ?\r\n")
    if data is None:
        return  # Skip this frequency if there is an error
    try:
        freq_meas = float(data)
    except ValueError:
        print(f"Invalid frequency measurement: {data}")
        return  # Skip this frequency if there is an error

    if freq_meas != freq:
        print("ERROR WHEN SETTING FREQUENCY!!!")
        return  # Skip this frequency if there is an error

    data = write_hm8118(port, "STRT\r\n")
    data = write_hm8118(port, "*WAI\r\n")
    data = readData_hm8118(port, "XALL?\r\n")
    if data is None:
        return  # Skip this frequency if there is an error

    freq_array.append(freq_meas)
    Impedance.append(data[0] / 1000)  # -> Note: Impedance is now in kOhm
    Phase.append(data[1])
    print(freq_meas, data[0], data[1])
    save_to_file(freq_meas, data[0], data[1])
    ax1.plot(freq_array, Impedance, marker='o', markersize=10, linestyle='', color='r')
    axtwin1.plot(freq_array, Phase, marker='o', markersize=10, linestyle='', color='b')
    return 0

# Initialize, i.e. select measurement mode
def initialize():
    data = read_hm8118(port, "CIRC 0\r\n")  # select Parallel Mode
    data = read_hm8118(port, "CIRC?\r\n")
    print("Mode = ", data)
    return 0

# Main routine
if __name__ == "__main__":
    global freq_array, Impedance, Phase
    freq_array = []
    Impedance = []
    Phase = []

    # Open device
    port = "/dev/ttyUSB0"
    baudrate = 9600
    timeout = 1
    ser = serial.Serial(port, baudrate, timeout=timeout)
    print(f"Verbunden mit {port} bei {baudrate} Baud.")

    command = "*IDN?\r\n"
    ser.write(command.encode())
    time.sleep(0.5)  # Kurze Pause für Antwort
    response = ser.readline().decode().strip()
    print(response)

    # Do the things you want to do
    anim = FuncAnimation(fig, update, frames=Frequency, init_func=initialize, repeat=False)
    plt.show()

    # Close device
    data = read_hm8118(port, "LOCK 0\r\n")
    ser.close()