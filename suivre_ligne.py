#!/usr/bin/env python3
"""
Suiveur de ligne noire - SunFounder PiCar-X
Usage :
    python3 suiveur_ligne.py          -> suivi de ligne
    python3 suiveur_ligne.py --calib  -> affiche les valeurs brutes des capteurs
"""
import sys
import time
from picarx import Picarx

# ---------------- Réglages (à ajuster) ----------------
BLANC = [1500, 1500, 1500]  # valeurs capteurs [gauche, milieu, droite] sur fond clair
NOIR = [300, 300, 300]      # valeurs capteurs sur la ligne noire

VITESSE_MAX = 30     # vitesse en ligne droite (0-100)
VITESSE_MIN = 15     # vitesse dans les virages serrés
ANGLE_MAX = 30       # braquage max du servo (degrés)
KP = 1.0             # gain de correction (augmenter si la voiture tourne trop peu)
SEUIL_PERDU = 0.3    # en dessous : la ligne n'est plus détectée
TIMEOUT_PERDU = 2.0  # secondes de recherche avant arrêt
PERIODE = 0.01       # pause de la boucle (s)
# ------------------------------------------------------

px = Picarx()


def noirceur(valeurs):
    """Convertit les valeurs brutes en 0.0 (blanc) -> 1.0 (noir) pour chaque capteur."""
    resultat = []
    for v, b, n in zip(valeurs, BLANC, NOIR):
        x = (b - v) / (b - n) if b != n else 0.0
        resultat.append(min(max(x, 0.0), 1.0))
    return resultat


def calibration():
    print("Place chaque capteur sur le blanc puis sur la ligne noire.")
    print("Note les valeurs et reporte-les dans BLANC / NOIR. Ctrl+C pour quitter.")
    while True:
        print(px.get_grayscale_data())
        time.sleep(0.2)


def suivre_ligne():
    derniere_pos = 0.0
    perdu_depuis = None

    while True:
        g, m, d = noirceur(px.get_grayscale_data())
        total = g + m + d

        if total >= SEUIL_PERDU:
            # Ligne visible : position de -1 (ligne à gauche) à +1 (ligne à droite)
            perdu_depuis = None
            pos = (d - g) / total
            derniere_pos = pos

            angle = max(-ANGLE_MAX, min(ANGLE_MAX, KP * pos * ANGLE_MAX))
            vitesse = VITESSE_MAX - (VITESSE_MAX - VITESSE_MIN) * abs(pos)

            px.set_dir_servo_angle(angle)
            px.forward(int(vitesse))
        else:
            # Ligne perdue : on braque du côté où on l'a vue en dernier
            if perdu_depuis is None:
                perdu_depuis = time.time()
            if time.time() - perdu_depuis > TIMEOUT_PERDU:
                px.stop()
                print("Ligne perdue, arrêt.")
                return
            px.set_dir_servo_angle(ANGLE_MAX if derniere_pos > 0 else -ANGLE_MAX)
            px.forward(VITESSE_MIN)

        time.sleep(PERIODE)


if __name__ == "__main__":
    try:
        if "--calib" in sys.argv:
            calibration()
        else:
            suivre_ligne()
    except KeyboardInterrupt:
        print("\nArrêt demandé.")
    finally:
        px.set_dir_servo_angle(0)
        px.stop()