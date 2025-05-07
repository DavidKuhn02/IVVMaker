#!/usr/bin/env python3
import serial
import time
import numpy as np

# Verfügbare Frequenzen zur Messung
FREQUENCIES_TO_MEASURE = [100000,120000]
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
            impedance = float(values[0]) # Umwandlung in kOhm
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

        # **Eingabe der Spannungsrange**
        voltage_start = float(input("Startspannung (V): "))
        voltage_end = float(input("Endspannung (V): "))
        voltage_step = float(input("Schrittweite (V): "))
        voltages = np.arange(voltage_start, voltage_end + voltage_step, voltage_step)
        repetitions = 3  # Anzahl der Wiederholungen pro Frequenz
        filename = input("Filename: ")
        data_file = f"{filename}.txt".replace(",", ".")  # Ersetzt Komma durch Punkt für Dateinamen
        with open(data_file, "w") as file:
            
            file.write(" Frequency (Hz) | Impedance (kOhm) | Phase (°)\n")

            for voltage in voltages:
                set_keithley_voltage(keithley, voltage)
                print(f"\nSpannung gesetzt auf {voltage} V\n")

            # Wiederholungsmessungen
                for freq in FREQUENCIES_TO_MEASURE:
                    for rep in range(1, repetitions + 1):
                        result = read_impedance(hameg, freq)
                        if result:
                            impedance, phase = result
                            print(f"[{rep}] Frequenz {freq} Hz: Impedanz = {impedance} kOhm, Phase = {phase}°")
                            file.write(f" {freq:<15} , {impedance:<18} , {phase:<10}\n")
                        else:
                            print(f"[{rep}] Fehler bei Frequenz {freq}, speichere 'Fehler'")
                            file.write(f"{rep:<10} , {freq:<15} , Fehler              , Fehler\n")



    except Exception as e:
        print(f"Fehler: {e}")

    finally:
        print("\nFahre Spannung automatisch herunter...")
        shutdown_voltage = -5  # Zielspannung am Ende
        shutdown_step = -5    # Schrittgröße beim Herunterfahren

        current_voltage = voltage_end
        while current_voltage - shutdown_step < shutdown_voltage:
            current_voltage -= shutdown_step  # Schrittweise nach unten
            set_keithley_voltage(keithley, current_voltage)
            print(f"Spannung heruntergeregelt auf {current_voltage} V")
            

        # Sicherstellen, dass die Zielspannung auch wirklich gesetzt wird
        set_keithley_voltage(keithley, shutdown_voltage)
        print(f"Endspannung erreicht: {shutdown_voltage} V")

        keithley.close()
        hameg.close()
        print("\nVerbindungen geschlossen.")


if __name__ == "__main__":
	main()
  
