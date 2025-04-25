#!/usr/bin/env python3
import serial
import time
import numpy as np

# Verfügbare Frequenzen zur Messung
#FREQUENCIES_TO_MEASURE = [8000, 9000, 10000, 72000, 80000, 90000, 100000, 120000, 150000, 180000, 200000]
FREQUENCIES_TO_MEASURE = [  1000, 2000, 3000, 4000,5000, 6000, 8000, 9000, 10000, 20000, 30000, 40000, 50000, 60000, 80000, 90000, 100000, 120000, 150000, 180000, 200000]
 
#FREQUENCIES_TO_MEASURE = [ 300, 360, 400, 450, 500, 600, 720, 800, 900, 1000, 1200, 1500, 1800, 2000, 2500, 3000, 3600, 4000, 4500, 5000, 6000, 7500, 8000, 9000, 10000, 12000, 15000, 18000, 20000, 25000, 30000, 36000, 40000, 45000, 50000, 60000, 72000, 80000, 90000, 100000, 120000, 150000, 180000, 200000]
  # Beispielhafte Auswahl

def set_keithley_voltage(keithley, voltage):
    """ Setzt die Spannung am Keithley """
    try:
        keithley.write(f"SOUR:VOLT {voltage}\n".encode())
        time.sleep(3)  # Warte auf Stabilisierung
    except Exception as e:
        print(f"Fehler beim Setzen der Spannung: {e}")

def read_impedance(ser, freq):
    """ Setzt die Frequenz und misst die Impedanz und Phase """
    try:
        ser.write(f"FREQ {freq}\r\n".encode())
        time.sleep(2)  # Kurze Wartezeit
        ser.write("XALL?\r\n".encode())  # Befehl zum Auslesen von Impedanz und Phase
        response = ser.readline().decode().strip()

        if not response:
            print(f" Warnung: Keine Antwort vom Hameg bei {freq} Hz")
            return None

        values = response.split(",")

        if len(values) < 3:
            print(f" Fehlerhafte Antwort vom Hameg: '{response}'")
            return None  # Antwort ist unvollständig

        # Umwandlung in Float mit Fehlerbehandlung
        try:
            impedance = float(values[0]) / 1000  # Umwandlung in kOhm
            phase = float(values[1])
        except ValueError:
            print(f" Fehler beim Umwandeln der Werte: {values}")
            return None

        return impedance, phase  

    except serial.SerialException as e:
        print(f" Serielle Kommunikationsfehler: {e}")
        return None

def main():
    port_keithley = "/dev/ttyUSB1"
    port_hameg = "/dev/ttyUSB0"  # Anpassung ggf. nötig

    try:
        keithley = serial.Serial(port_keithley, 9600, timeout=1)
        hameg = serial.Serial(port_hameg, 9600, timeout=1)
        print(f"Verbunden mit Keithley ({port_keithley}) und Hameg ({port_hameg})")
        keithley.write(f"SOUR:VOLT:ILIM {25e-4}\n".encode())
        # **Eingabe der Spannungsrange**
        voltage_start = float(input("Startspannung (V): "))
        voltage_end = float(input("Endspannung (V): "))
        voltage_step = float(input("Schrittweite (V): "))
        filename = input("Filename: ")
        # Erzeuge eine Liste von Spannungen
        voltages = np.arange(voltage_start, voltage_end + voltage_step, voltage_step)

        for voltage in voltages:
            # **Spannung setzen**
            set_keithley_voltage(keithley, voltage)
            print(f"\n Spannung gesetzt auf {voltage} V\n")

            # **Dateiname für diese Spannung erstellen**
            data_file = f"{filename}_{voltage:.2f}V.txt".replace(",", ".")  # Ersetzt Komma durch Punkt für Dateinamen

            # **Messung starten und Daten speichern**
            with open(data_file, "w") as file:
                
                file.write("Frequenz (Hz) | Impedanz (kOhm) | Phase (°)\n")
                file.write(f"Spannung: {voltage} V\n")
                

                for freq in FREQUENCIES_TO_MEASURE:
                    result = read_impedance(hameg, freq)
                    if result:
                        impedance, phase = result
                        print(f"Frequenz {freq} Hz: Impedanz = {impedance} kOhm, Phase = {phase}°")
                        file.write(f"{freq:<12} , {impedance:<16} , {phase:<10}\n")
                    else:
                        print(f"Fehler bei Frequenz {freq}, speichere 'Fehler'")
                        #file.write(f"{freq:<12} , Fehler           , Fehler   \n")

            print(f" Messdaten gespeichert in {data_file}")

    except Exception as e:
        print(f"Fehler: {e}")

    finally:
        shutdown_voltages = np.arange(voltage_end,-2,10)
        for v in shutdown_voltages:
            set_keithley_voltage(keithley, v)

        keithley.close()
        hameg.close()
        print("\n Verbindungen geschlossen.")

if __name__ == "__main__":
    main()
