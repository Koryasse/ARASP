#!/usr/bin/env python3
"""Fait avancer le SunFounder PiCar jusqu'à Ctrl+C."""
import time

import picar
from picar import back_wheels

VITESSE = 40

picar.setup()
bw = back_wheels.Back_Wheels()
bw.ready()

try:
    bw.left_wheel.speed = VITESSE
    bw.right_wheel.speed = VITESSE
    bw.left_wheel.forward()
    bw.right_wheel.forward()
    print("La voiture avance. Appuyez sur Ctrl+C pour l'arrêter.")
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\nArrêt demandé.")
finally:
    bw.stop()
