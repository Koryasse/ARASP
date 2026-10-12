#!/usr/bin/env python3
"""Fait avancer le SunFounder PiCar-X en ligne droite jusqu'à Ctrl+C."""
import time

from picarx import Picarx

VITESSE = 30  # vitesse moteur (0-100)

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
