#!/usr/bin/env python3
"""Fait avancer le SunFounder PiCar-X en ligne droite jusqu'à Ctrl+C."""
import time

from importlib import import_module

# picarx is provided by the PiCar-X environment, not by the standard Python install.
Picarx = import_module("picarx").Picarx

VITESSE = 50  # vitesse moteur (0-100)

px = Picarx()

try:
    px.set_dir_servo_angle(0)
    print("La voiture avance. Appuyez sur Ctrl+C pour l'arrêter.")
    while True:
        px.forward(VITESSE)
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\nArrêt demandé.")
finally:
    px.set_dir_servo_angle(0)
    px.stop()
