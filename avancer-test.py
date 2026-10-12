import time
import picar
from picar import back_wheels
from SunFounder_Line_Follower import Line_Follower

picar.setup()

# ---------- Initialisation ----------
lf = Line_Follower.Line_Follower()
bw = back_wheels.Back_Wheels()
bw.ready()

# ---------- Réglages ----------
VITESSE_BASE = 40          # vitesse quand la ligne est centrée
GAIN = 25                  # force de la correction (plus grand = tourne plus fort)
VITESSE_MAX = 80           # limite de vitesse d'une roue
TEMPS_PERDU_MAX = 2.0      # secondes sans voir la ligne avant arrêt
VITESSE_RECHERCHE = 40     # vitesse du pivot quand la ligne est perdue
INVERSER_DIRECTION = True  # mettre False si le robot tourne du mauvais côté

# Poids de chaque capteur : plus il est loin du centre, plus on tourne fort
# [extrême gauche, gauche, centre, droite, extrême droite]
POIDS = [-2, -1, 0, 1, 2]

# ---------- Moteurs ----------
def regler_roue(roue, v):
    """v > 0 : avance, v < 0 : recule."""
    v = max(-VITESSE_MAX, min(VITESSE_MAX, int(v)))
    roue.speed = abs(v)
    if v >= 0:
        roue.forward()
    else:
        roue.backward()
    return v

def moteurs(vg, vd):
    vg = regler_roue(bw.left_wheel, vg)
    vd = regler_roue(bw.right_wheel, vd)
    return vg, vd

def stopper():
    bw.stop()

# ---------- Calibration ----------
def calibrer():
    input("Placez les capteurs sur une surface CLAIRE, puis Entrée...")
    clair = lf.read_analog()
    input("Placez les capteurs sur la LIGNE NOIRE, puis Entrée...")
    sombre = lf.read_analog()

    lf.references = [(c + s) // 2 for c, s in zip(clair, sombre)]
    print("Clair :", clair)
    print("Sombre:", sombre)
    print("Seuils:", lf.references)

    etat = lf.read_digital()
    niveau_ligne = 1 if sum(etat) >= 3 else 0
    print("Sur la ligne, read_digital() donne :", etat, "-> ligne =", niveau_ligne)
    return niveau_ligne

# ---------- Suivi de ligne proportionnel ----------
def suivre_ligne(niveau_ligne):
    derniere_erreur = 0.0
    dernier_vu = time.time()
    debut = time.time()
    dernier_affiche = None

    while True:
        brut = lf.read_digital()
        s = [1 if x == niveau_ligne else 0 for x in brut]
        if INVERSER_DIRECTION:
            s = s[::-1]

        if sum(s) == 0:
            # Ligne perdue : on pivote du côté où elle a disparu
            if time.time() - dernier_vu > TEMPS_PERDU_MAX:
                stopper()
                print("Ligne perdue, arrêt.")
                return
            if derniere_erreur < 0:
                vg, vd = moteurs(-VITESSE_RECHERCHE, VITESSE_RECHERCHE)
            elif derniere_erreur > 0:
                vg, vd = moteurs(VITESSE_RECHERCHE, -VITESSE_RECHERCHE)
            else:
                stopper(); vg, vd = 0, 0
            erreur = derniere_erreur
        else:
            dernier_vu = time.time()
            # Position moyenne de la ligne : de -2 (très à gauche) à +2 (très à droite)
            erreur = sum(p * x for p, x in zip(POIDS, s)) / sum(s)
            derniere_erreur = erreur
            # Plus l'erreur est grande, plus la différence entre les roues augmente
            vg, vd = moteurs(VITESSE_BASE + GAIN * erreur,
                             VITESSE_BASE - GAIN * erreur)

        if brut != dernier_affiche:
            print(f"{time.time() - debut:7.2f}s  {brut}  erreur={erreur:+.2f}  G={vg:+d} D={vd:+d}")
            dernier_affiche = brut

        time.sleep(0.02)

# ---------- Programme principal ----------
if __name__ == "__main__":
    try:
        niveau = calibrer()
        input("Posez le robot sur la ligne, puis Entrée pour démarrer (Ctrl+C pour stopper)...")
        suivre_ligne(niveau)
    except KeyboardInterrupt:
        print("Arrêt demandé.")
    finally:
        stopper()
        print("Moteurs arrêtés.")
