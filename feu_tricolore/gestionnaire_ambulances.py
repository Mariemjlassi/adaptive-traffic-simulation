from feu_tricolore.voiture import Voiture
from feu_tricolore.constants import (
    BLANC,
    DISTANCE_DETECTION_AMBULANCE,
    SPAWN_NORD_X, SPAWN_NORD_Y,
    SPAWN_SUD_X, SPAWN_SUD_Y,
    SPAWN_EST_X, SPAWN_EST_Y,
    SPAWN_OUEST_X, SPAWN_OUEST_Y
)

class GestionnaireAmbulances:
    def __init__(self, centre_x, centre_y, largeur, hauteur):
        self.centre_x = centre_x
        self.centre_y = centre_y
        self.largeur = largeur
        self.hauteur = hauteur

        # Système d'ambulances
        self.compteur_ambulances = 0
        self.ambulance_active = None
        self.phase_avant_ambulance = None

    def detecter_ambulance_approchant(self, voitures_nord, voitures_sud, voitures_est, voitures_ouest, mode_urgence):
        """Détecte si une ambulance approche de l'intersection et active la priorité"""
        if mode_urgence:
            return None

        # Distance de détection (300 pixels avant l'intersection)
        distance_detection = DISTANCE_DETECTION_AMBULANCE

        # Vérifier chaque direction - DÉTECTION ÉTENDUE jusqu'à l'entrée de l'intersection
        for voiture in voitures_nord:
            # Détecter de 300px avant jusqu'à l'ENTRÉE de l'intersection (y = centre_y - 140)
            if voiture.est_ambulance and voiture.y < self.centre_y - 140 and voiture.y > self.centre_y - distance_detection:
                return "N"

        for voiture in voitures_sud:
            # Détecter de 300px avant jusqu'à l'ENTRÉE de l'intersection (y = centre_y + 140)
            if voiture.est_ambulance and voiture.y > self.centre_y + 140 and voiture.y < self.centre_y + distance_detection:
                return "S"

        for voiture in voitures_est:
            # Détecter de 300px avant jusqu'à l'ENTRÉE de l'intersection (x = centre_x + 140)
            if voiture.est_ambulance and voiture.x > self.centre_x + 140 and voiture.x < self.centre_x + distance_detection:
                return "E"

        for voiture in voitures_ouest:
            # Détecter de 300px avant jusqu'à l'ENTRÉE de l'intersection (x = centre_x - 140)
            if voiture.est_ambulance and voiture.x < self.centre_x - 140 and voiture.x > self.centre_x - distance_detection:
                return "O"

        return None

    def activer_priorite_ambulance(self, direction, phase_actuelle):
        """Active le feu vert IMMÉDIATEMENT pour la direction de l'ambulance"""
        if self.ambulance_active == direction:
            return None

        # Sauvegarder la phase actuelle
        if self.ambulance_active is None:
            self.phase_avant_ambulance = phase_actuelle

        self.ambulance_active = direction
        return direction

    def verifier_ambulance_passee(self, voitures_nord, voitures_sud, voitures_est, voitures_ouest):
        """Vérifie si l'ambulance est passée pour restaurer le mode normal"""
        if self.ambulance_active is None:
            return False

        ambulance_passee = True

        # Vérifier si l'ambulance est encore dans la zone
        if self.ambulance_active == "N":
            for voiture in voitures_nord:
                if voiture.est_ambulance and voiture.y < self.centre_y + 200:
                    ambulance_passee = False
                    break
        elif self.ambulance_active == "S":
            for voiture in voitures_sud:
                if voiture.est_ambulance and voiture.y > self.centre_y - 200:
                    ambulance_passee = False
                    break
        elif self.ambulance_active == "E":
            for voiture in voitures_est:
                if voiture.est_ambulance and voiture.x > self.centre_x - 200:
                    ambulance_passee = False
                    break
        elif self.ambulance_active == "O":
            for voiture in voitures_ouest:
                if voiture.est_ambulance and voiture.x < self.centre_x + 200:
                    ambulance_passee = False
                    break

        if ambulance_passee:
            self.ambulance_active = None
            self.phase_avant_ambulance = None
            return True

        return False

    def spawner_ambulance(self, direction, voitures_nord, voitures_sud, voitures_est, voitures_ouest):
        """Spawne une ambulance dans une direction donnée"""
        couleur_ambulance = BLANC

        if direction == "N":
            ambulance = Voiture(SPAWN_NORD_X, SPAWN_NORD_Y, "N", couleur_ambulance, est_ambulance=True)
            voitures_nord.append(ambulance)
        elif direction == "S":
            ambulance = Voiture(SPAWN_SUD_X, SPAWN_SUD_Y, "S", couleur_ambulance, est_ambulance=True)
            voitures_sud.append(ambulance)
        elif direction == "E":
            ambulance = Voiture(SPAWN_EST_X, SPAWN_EST_Y, "E", couleur_ambulance, est_ambulance=True)
            voitures_est.append(ambulance)
        else:  # "O"
            ambulance = Voiture(SPAWN_OUEST_X, SPAWN_OUEST_Y, "O", couleur_ambulance, est_ambulance=True)
            voitures_ouest.append(ambulance)

        self.compteur_ambulances += 1
        return True