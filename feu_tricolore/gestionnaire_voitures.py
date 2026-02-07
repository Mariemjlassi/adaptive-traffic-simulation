import random
from feu_tricolore.voiture import Voiture
from feu_tricolore.meteo import meteo
from feu_tricolore.constants import (
    COULEURS_VOITURES,
    INTERVALLE_SPAWN_VOITURES,
    PROBABILITE_SPAWN,
    VOITURES_INITIALES_MIN,
    VOITURES_INITIALES_MAX,
    DISTANCE_SECURITE_VOITURE,
    SEUIL_COLLISION_X,
    SEUIL_COLLISION_Y,
    ZONE_INTERSECTION_DEMI_LARGEUR,
    ZONE_INTERSECTION_DEMI_HAUTEUR,
    DUREE_INTERVENTION_ACCIDENT,
    SPAWN_NORD_X, SPAWN_NORD_Y,
    SPAWN_SUD_X, SPAWN_SUD_Y,
    SPAWN_EST_X, SPAWN_EST_Y,
    SPAWN_OUEST_X, SPAWN_OUEST_Y,
    LIMITE_SORTIE_NORD,
    LIMITE_SORTIE_SUD,
    LIMITE_SORTIE_EST,
    LIMITE_SORTIE_OUEST,
    ZONE_ARRET_NORD_MIN, ZONE_ARRET_NORD_MAX,
    ZONE_ARRET_SUD_MIN, ZONE_ARRET_SUD_MAX,
    ZONE_ARRET_EST_MIN, ZONE_ARRET_EST_MAX,
    ZONE_ARRET_OUEST_MIN, ZONE_ARRET_OUEST_MAX,
    ZONE_ATTENTE_NS_MIN, ZONE_ATTENTE_NS_MAX,
    ZONE_ATTENTE_EO_MIN, ZONE_ATTENTE_EO_MAX,
    ZONE_APPROCHE_DISTANCE,
    ROUGE, BLEU
)

class GestionnaireVoitures:
    def __init__(self, centre_x, centre_y, largeur, hauteur):
        self.centre_x = centre_x
        self.centre_y = centre_y
        self.largeur = largeur
        self.hauteur = hauteur

        # Voitures animées par direction
        self.voitures_nord = []
        self.voitures_sud = []
        self.voitures_est = []
        self.voitures_ouest = []
        self.temps_spawn_voiture = 0

        # Système d'accidents
        self.mode_urgence = False
        self.accident_actif = None
        self.temps_clignotement = 0
        self.compteur_accidents = 0
        self.duree_intervention = DUREE_INTERVENTION_ACCIDENT

        # Système de priorité ambulance
        self.ambulance_direction_active = None

    def spawn_voitures(self, trafic_nord, trafic_sud, trafic_est, trafic_ouest):
        """Génère des voitures selon le niveau de trafic"""
        self.temps_spawn_voiture += 1

        if self.temps_spawn_voiture > INTERVALLE_SPAWN_VOITURES:
            self.temps_spawn_voiture = 0

            # Nord (venant du haut, allant vers le bas)
            if len(self.voitures_nord) < trafic_nord.niveau and random.random() > PROBABILITE_SPAWN:
                couleur = random.choice(COULEURS_VOITURES)
                self.voitures_nord.append(Voiture(SPAWN_NORD_X, SPAWN_NORD_Y, "N", couleur))

            # Sud (venant du bas, allant vers le haut)
            if len(self.voitures_sud) < trafic_sud.niveau and random.random() > PROBABILITE_SPAWN:
                couleur = random.choice(COULEURS_VOITURES)
                self.voitures_sud.append(Voiture(SPAWN_SUD_X, SPAWN_SUD_Y, "S", couleur))

            # Est (venant de la droite, allant vers la gauche)
            if len(self.voitures_est) < trafic_est.niveau and random.random() > PROBABILITE_SPAWN:
                couleur = random.choice(COULEURS_VOITURES)
                self.voitures_est.append(Voiture(SPAWN_EST_X, SPAWN_EST_Y, "E", couleur))

            # Ouest (venant de la gauche, allant vers la droite)
            if len(self.voitures_ouest) < trafic_ouest.niveau and random.random() > PROBABILITE_SPAWN:
                couleur = random.choice(COULEURS_VOITURES)
                self.voitures_ouest.append(Voiture(SPAWN_OUEST_X, SPAWN_OUEST_Y, "O", couleur))

    def detecter_ambulance_active(self):
        """Détecte s'il y a une ambulance active et dans quelle direction"""
        for voiture in self.voitures_nord:
            if voiture.est_ambulance:
                return "N"
        for voiture in self.voitures_sud:
            if voiture.est_ambulance:
                return "S"
        for voiture in self.voitures_est:
            if voiture.est_ambulance:
                return "E"
        for voiture in self.voitures_ouest:
            if voiture.est_ambulance:
                return "O"
        return None

    def intersection_est_securisee_pour_ambulance(self, direction_ambulance):
        """
        Vérifie si l'intersection est sécurisée pour le passage de l'ambulance.
        Retourne True si aucun véhicule n'est dans l'intersection.

        Args:
            direction_ambulance: Direction de l'ambulance ("N", "S", "E", "O")

        Returns:
            bool: True si l'intersection est sécurisée
        """
        # Zone d'intersection
        zone_x_min = self.centre_x - ZONE_INTERSECTION_DEMI_LARGEUR
        zone_x_max = self.centre_x + ZONE_INTERSECTION_DEMI_LARGEUR
        zone_y_min = self.centre_y - ZONE_INTERSECTION_DEMI_HAUTEUR
        zone_y_max = self.centre_y + ZONE_INTERSECTION_DEMI_HAUTEUR

        # Vérifier les voitures dans l'intersection (sauf l'ambulance elle-même)
        for voiture in self.voitures_nord:
            if not voiture.est_ambulance and zone_y_min <= voiture.y <= zone_y_max:
                return False

        for voiture in self.voitures_sud:
            if not voiture.est_ambulance and zone_y_min <= voiture.y <= zone_y_max:
                return False

        for voiture in self.voitures_est:
            if not voiture.est_ambulance and zone_x_min <= voiture.x <= zone_x_max:
                return False

        for voiture in self.voitures_ouest:
            if not voiture.est_ambulance and zone_x_min <= voiture.x <= zone_x_max:
                return False

        return True

    def peut_ambulance_avancer(self, ambulance, direction, feux_pietons):
        """
        Détermine si l'ambulance peut avancer en sécurité.
        
        1. Si loin de l'intersection → avance librement (ignore piétons)
        2. Si proche de l'intersection:
        - Si piétons traversent → s'arrête AVANT la zone piétons
        - Si pas de piétons → vérifie que l'intersection est vide
        
        """
        # Distance de sécurité avant l'intersection
        zone_proche = 170
        
        #  VÉRIFIER SI AMBULANCE EST LOIN DE L'INTERSECTION
        if direction == "N":
            if ambulance.y < self.centre_y - zone_proche:
                return True  # Loin → avance librement (ignore piétons)
            
            # PROCHE DE L'INTERSECTION : Vérifier piétons
            if feux_pietons['nord'].pieton_vert or feux_pietons['sud'].pieton_vert:
                # Piétons traversent → S'arrêter AVANT la zone piétons (zone_proche)
                # Permettre d'avancer jusqu'à zone_proche + 20px de marge
                if ambulance.y < self.centre_y - zone_proche - 20:
                    return True  # Peut encore avancer vers la zone d'arrêt
                else:
                    return False  # STOP : trop proche des piétons
            
            # Pas de piétons → Vérifier que l'intersection est vide
            return self.intersection_est_securisee_pour_ambulance(direction)
        
        elif direction == "S":
            if ambulance.y > self.centre_y + zone_proche:
                return True  # Loin → avance librement
            
            # Proche : vérifier piétons
            if feux_pietons['nord'].pieton_vert or feux_pietons['sud'].pieton_vert:
                if ambulance.y > self.centre_y + zone_proche + 20:
                    return True  # Peut encore avancer
                else:
                    return False  # STOP : proche des piétons
            
            return self.intersection_est_securisee_pour_ambulance(direction)
        
        elif direction == "E":
            if ambulance.x > self.centre_x + zone_proche:
                return True  # Loin → avance librement
            
            # Proche : vérifier piétons
            if feux_pietons['est'].pieton_vert or feux_pietons['ouest'].pieton_vert:
                if ambulance.x > self.centre_x + zone_proche + 20:
                    return True  # Peut encore avancer
                else:
                    return False  # STOP : proche des piétons
            
            return self.intersection_est_securisee_pour_ambulance(direction)
        
        else:  # "O"
            if ambulance.x < self.centre_x - zone_proche:
                return True  # Loin → avance librement
            
            # Proche : vérifier piétons
            if feux_pietons['est'].pieton_vert or feux_pietons['ouest'].pieton_vert:
                if ambulance.x < self.centre_x - zone_proche - 20:
                    return True  # Peut encore avancer
                else:
                    return False  # STOP : proche des piétons
            
            return self.intersection_est_securisee_pour_ambulance(direction)

    def spawn_voitures_initial(self):
        """Crée quelques voitures au démarrage pour avoir du trafic immédiatement"""
        # Créer 2-3 voitures par direction au démarrage
        for _ in range(random.randint(VOITURES_INITIALES_MIN, VOITURES_INITIALES_MAX)):
            # Nord
            couleur = random.choice(COULEURS_VOITURES)
            y_pos = random.randint(50, 200)
            self.voitures_nord.append(Voiture(SPAWN_NORD_X, y_pos, "N", couleur))

            # Sud
            couleur = random.choice(COULEURS_VOITURES)
            y_pos = random.randint(self.hauteur - 200, self.hauteur - 50)
            self.voitures_sud.append(Voiture(SPAWN_SUD_X, y_pos, "S", couleur))

            # Est
            couleur = random.choice(COULEURS_VOITURES)
            x_pos = random.randint(self.largeur - 800, self.largeur - 650)
            self.voitures_est.append(Voiture(x_pos, SPAWN_EST_Y, "E", couleur))

            # Ouest
            couleur = random.choice(COULEURS_VOITURES)
            x_pos = random.randint(50, 200)
            self.voitures_ouest.append(Voiture(x_pos, SPAWN_OUEST_Y, "O", couleur))

    def update_voitures(self, feu_nord, feu_sud, feu_est, feu_ouest):
        """Met à jour les positions des voitures"""

        # BLOQUER mouvement si mode urgence (accident)
        if self.mode_urgence:
            return

        # Détecter ambulance active
        self.ambulance_direction_active = self.detecter_ambulance_active()

        # Créer dict des feux pour vérification piétons
        feux_pietons = {
            'nord': feu_nord,
            'sud': feu_sud,
            'est': feu_est,
            'ouest': feu_ouest
        }

        # Nord (venant du haut, descendant vers le sud)
        # Voie à gauche de la route verticale (x = centre_x - 60)
        for i, voiture in enumerate(self.voitures_nord):
            peut_avancer = True

            # AMBULANCES : Priorité conditionnelle - vérifie sécurité avant d'avancer
            if voiture.est_ambulance:
                peut_avancer = self.peut_ambulance_avancer(voiture, "N", feux_pietons)
                voiture.deplacer(peut_avancer)
                continue

            # VOITURES NORMALES : S'arrêtent si ambulance active sur leur axe
            if self.ambulance_direction_active in ["N", "S"]:
                # Ambulance N-S active : arrêt obligatoire AVANT l'intersection
                if ZONE_ARRET_NORD_MIN <= voiture.y < ZONE_ARRET_NORD_MAX:
                    peut_avancer = False
                    voiture.deplacer(peut_avancer)
                    continue

            # SÉCURITÉ PIÉTONS : Bloquer si piétons traversent cette voie
            # Voiture NORD (x=-60, voie gauche) croise passages horizontaux Nord/Sud
            # Passage Nord/Sud = piétons traversant la route E-O (horizontale)
            if feux_pietons['nord'].pieton_vert or feux_pietons['sud'].pieton_vert:
                if ZONE_ARRET_NORD_MIN <= voiture.y < ZONE_ARRET_NORD_MAX:
                    peut_avancer = False
                    voiture.deplacer(peut_avancer)
                    continue

            # Vérifier collision avec la voiture devant
            if i > 0:
                voiture_devant = self.voitures_nord[i - 1]
                distance = voiture_devant.y - voiture.y
                if distance < DISTANCE_SECURITE_VOITURE:
                    peut_avancer = False

            # Zone d'arrêt au feu AVANT l'intersection - s'arrête seulement si PAS ENCORE dans l'intersection
            if feu_nord.couleur != "Vert":
                if ZONE_ARRET_NORD_MIN <= voiture.y < ZONE_ARRET_NORD_MAX:
                    peut_avancer = False

            voiture.deplacer(peut_avancer)

        # Supprimer les voitures qui sortent
        self.voitures_nord = [v for v in self.voitures_nord if v.y <= LIMITE_SORTIE_NORD]

        # Sud (venant du bas, montant vers le nord)
        # Voie à droite de la route verticale (x = centre_x + 60)
        for i, voiture in enumerate(self.voitures_sud):
            peut_avancer = True

            # AMBULANCES : Priorité conditionnelle - vérifie sécurité avant d'avancer
            if voiture.est_ambulance:
                peut_avancer = self.peut_ambulance_avancer(voiture, "S", feux_pietons)
                voiture.deplacer(peut_avancer)
                continue

            # VOITURES NORMALES : S'arrêtent si ambulance active sur leur axe
            if self.ambulance_direction_active in ["N", "S"]:
                # Ambulance N-S active : arrêt obligatoire AVANT l'intersection
                if ZONE_ARRET_SUD_MIN < voiture.y <= ZONE_ARRET_SUD_MAX:
                    peut_avancer = False
                    voiture.deplacer(peut_avancer)
                    continue

            # SÉCURITÉ PIÉTONS : Bloquer si piétons traversent cette voie
            # Voiture SUD (x=+60, voie droite) croise passages horizontaux Nord/Sud
            # Passage Nord/Sud = piétons traversant la route E-O (horizontale)
            if feux_pietons['nord'].pieton_vert or feux_pietons['sud'].pieton_vert:
                if ZONE_ARRET_SUD_MIN < voiture.y <= ZONE_ARRET_SUD_MAX:
                    peut_avancer = False
                    voiture.deplacer(peut_avancer)
                    continue

            # Vérifier collision avec la voiture devant
            if i > 0:
                voiture_devant = self.voitures_sud[i - 1]
                distance = voiture.y - voiture_devant.y
                if distance < DISTANCE_SECURITE_VOITURE:
                    peut_avancer = False

            # Zone d'arrêt au feu AVANT l'intersection - s'arrête seulement si PAS ENCORE dans l'intersection
            if feu_sud.couleur != "Vert":
                if ZONE_ARRET_SUD_MIN < voiture.y <= ZONE_ARRET_SUD_MAX:
                    peut_avancer = False

            voiture.deplacer(peut_avancer)

        # Supprimer les voitures qui sortent
        self.voitures_sud = [v for v in self.voitures_sud if v.y >= LIMITE_SORTIE_SUD]

        # Est (venant de la droite, allant vers la gauche/ouest)
        # Voie en haut de la route horizontale (y = centre_y - 60)
        for i, voiture in enumerate(self.voitures_est):
            peut_avancer = True

            # AMBULANCES : Priorité conditionnelle - vérifie sécurité avant d'avancer
            if voiture.est_ambulance:
                peut_avancer = self.peut_ambulance_avancer(voiture, "E", feux_pietons)
                voiture.deplacer(peut_avancer)
                continue

            # VOITURES NORMALES : S'arrêtent si ambulance active sur leur axe
            if self.ambulance_direction_active in ["E", "O"]:
                # Ambulance E-O active : arrêt obligatoire AVANT l'intersection
                if ZONE_ARRET_EST_MIN < voiture.x <= ZONE_ARRET_EST_MAX:
                    peut_avancer = False
                    voiture.deplacer(peut_avancer)
                    continue

            # SÉCURITÉ PIÉTONS : Bloquer si piétons traversent cette voie
            # Voiture EST (y=-60, voie haut) croise passages verticaux Est/Ouest
            # Passage Est/Ouest = piétons traversant la route N-S (verticale)
            if feux_pietons['est'].pieton_vert or feux_pietons['ouest'].pieton_vert:
                if ZONE_ARRET_EST_MIN < voiture.x <= ZONE_ARRET_EST_MAX:
                    peut_avancer = False
                    voiture.deplacer(peut_avancer)
                    continue

            # Vérifier collision avec la voiture devant
            if i > 0:
                voiture_devant = self.voitures_est[i - 1]
                distance = voiture.x - voiture_devant.x
                if distance < DISTANCE_SECURITE_VOITURE:
                    peut_avancer = False

            # Zone d'arrêt au feu AVANT l'intersection - s'arrête seulement si PAS ENCORE dans l'intersection
            if feu_est.couleur != "Vert":
                if ZONE_ARRET_EST_MIN < voiture.x <= ZONE_ARRET_EST_MAX:
                    peut_avancer = False

            voiture.deplacer(peut_avancer)

        # Supprimer les voitures qui sortent
        self.voitures_est = [v for v in self.voitures_est if v.x >= LIMITE_SORTIE_EST]

        # Ouest (venant de la gauche, allant vers la droite/est)
        # Voie en bas de la route horizontale (y = centre_y + 60)
        for i, voiture in enumerate(self.voitures_ouest):
            peut_avancer = True

            # AMBULANCES : Priorité conditionnelle - vérifie sécurité avant d'avancer
            if voiture.est_ambulance:
                peut_avancer = self.peut_ambulance_avancer(voiture, "O", feux_pietons)
                voiture.deplacer(peut_avancer)
                continue

            # VOITURES NORMALES : S'arrêtent si ambulance active sur leur axe
            if self.ambulance_direction_active in ["E", "O"]:
                # Ambulance E-O active : arrêt obligatoire AVANT l'intersection
                if ZONE_ARRET_OUEST_MIN <= voiture.x < ZONE_ARRET_OUEST_MAX:
                    peut_avancer = False
                    voiture.deplacer(peut_avancer)
                    continue

            # SÉCURITÉ PIÉTONS : Bloquer si piétons traversent cette voie
            # Voiture OUEST (y=+60, voie bas) croise passages verticaux Est/Ouest
            # Passage Est/Ouest = piétons traversant la route N-S (verticale)
            if feux_pietons['est'].pieton_vert or feux_pietons['ouest'].pieton_vert:
                if ZONE_ARRET_OUEST_MIN <= voiture.x < ZONE_ARRET_OUEST_MAX:
                    peut_avancer = False
                    voiture.deplacer(peut_avancer)
                    continue

            # Vérifier collision avec la voiture devant
            if i > 0:
                voiture_devant = self.voitures_ouest[i - 1]
                distance = voiture_devant.x - voiture.x
                if distance < DISTANCE_SECURITE_VOITURE:
                    peut_avancer = False

            # Zone d'arrêt au feu AVANT l'intersection - s'arrête seulement si PAS ENCORE dans l'intersection
            if feu_ouest.couleur != "Vert":
                if ZONE_ARRET_OUEST_MIN <= voiture.x < ZONE_ARRET_OUEST_MAX:
                    peut_avancer = False

            voiture.deplacer(peut_avancer)

        # Supprimer les voitures qui sortent
        self.voitures_ouest = [v for v in self.voitures_ouest if v.x <= LIMITE_SORTIE_OUEST]

    def detecter_collisions(self):
        """Détecte les collisions entre voitures dans l'intersection"""
        if self.accident_actif:
            return  # Un accident est déjà en cours

        # Zone d'intersection pour détection
        zone_x_min = self.centre_x - ZONE_INTERSECTION_DEMI_LARGEUR
        zone_x_max = self.centre_x + ZONE_INTERSECTION_DEMI_LARGEUR
        zone_y_min = self.centre_y - ZONE_INTERSECTION_DEMI_HAUTEUR
        zone_y_max = self.centre_y + ZONE_INTERSECTION_DEMI_HAUTEUR

        # Collecter toutes les voitures dans l'intersection
        # NOTE: Les ambulances sont incluses mais la logique les empêche d'entrer si dangereux
        voitures_intersection = []

        for voiture in self.voitures_nord:
            if zone_y_min <= voiture.y <= zone_y_max:
                voitures_intersection.append(("N", voiture))

        for voiture in self.voitures_sud:
            if zone_y_min <= voiture.y <= zone_y_max:
                voitures_intersection.append(("S", voiture))

        for voiture in self.voitures_est:
            if zone_x_min <= voiture.x <= zone_x_max:
                voitures_intersection.append(("E", voiture))

        for voiture in self.voitures_ouest:
            if zone_x_min <= voiture.x <= zone_x_max:
                voitures_intersection.append(("O", voiture))

        # Vérifier les collisions entre voitures de directions différentes
        for i, (dir1, v1) in enumerate(voitures_intersection):
            for dir2, v2 in voitures_intersection[i+1:]:
                # Collision si les rectangles se chevauchent
                if (abs(v1.x - v2.x) < SEUIL_COLLISION_X and abs(v1.y - v2.y) < SEUIL_COLLISION_Y):
                    # ACCIDENT DÉTECTÉ !
                    return (v1, v2, dir1, dir2)
        return None

    def declencher_accident(self, voiture1, voiture2, dir1, dir2):
        """Déclenche un accident et active le mode urgence"""
        # Position de l'accident (milieu entre les 2 voitures)
        pos_x = (voiture1.x + voiture2.x) // 2
        pos_y = (voiture1.y + voiture2.y) // 2

        self.accident_actif = {
            "position": (pos_x, pos_y),
            "directions": [dir1, dir2],
            "duree": self.duree_intervention,
            "voitures": [voiture1, voiture2]
        }

        self.mode_urgence = True
        self.compteur_accidents += 1

    def gerer_accident(self):
        """Gère l'évolution de l'accident et le retour à la normale"""
        if not self.accident_actif:
            return False

        self.accident_actif["duree"] -= 1

        if self.accident_actif["duree"] <= 0:
            # Retirer les voitures accidentées
            for voiture in self.accident_actif["voitures"]:
                for liste in [self.voitures_nord, self.voitures_sud, self.voitures_est, self.voitures_ouest]:
                    if voiture in liste:
                        liste.remove(voiture)

            self.accident_actif = None
            self.mode_urgence = False
            return True
        return False

    def simuler_accident(self):
        """Simule un accident au centre de l'intersection"""
        if self.mode_urgence:
            return False

        # Créer un accident simulé au centre de l'intersection
        # Trouver deux voitures dans l'intersection ou créer des voitures fictives
        voitures_fictives = []

        # Voiture fictive 1 (de la direction Nord)
        v1 = Voiture(self.centre_x - 60, self.centre_y, "N", ROUGE)
        voitures_fictives.append(v1)

        # Voiture fictive 2 (de la direction Est)
        v2 = Voiture(self.centre_x, self.centre_y - 60, "E", BLEU)
        voitures_fictives.append(v2)

        # Déclencher l'accident
        self.declencher_accident(v1, v2, "N", "E")
        return True

    def compter_voitures_en_attente_ns(self):
        """Compte les voitures en attente dans la zone d'arrêt Nord-Sud"""
        count = 0
        # Voitures Nord en attente (zone d'arrêt)
        for voiture in self.voitures_nord:
            if self.centre_y - ZONE_ATTENTE_NS_MAX <= voiture.y < self.centre_y - ZONE_ATTENTE_NS_MIN:
                count += 1
        # Voitures Sud en attente (zone d'arrêt)
        for voiture in self.voitures_sud:
            if self.centre_y + ZONE_ATTENTE_NS_MIN < voiture.y <= self.centre_y + ZONE_ATTENTE_NS_MAX:
                count += 1
        return count

    def compter_voitures_en_attente_eo(self):
        """Compte les voitures en attente dans la zone d'arrêt Est-Ouest"""
        count = 0
        # Voitures Est en attente (zone d'arrêt)
        for voiture in self.voitures_est:
            if self.centre_x + ZONE_ATTENTE_EO_MIN < voiture.x <= self.centre_x + ZONE_ATTENTE_EO_MAX:
                count += 1
        # Voitures Ouest en attente (zone d'arrêt)
        for voiture in self.voitures_ouest:
            if self.centre_x - ZONE_ATTENTE_EO_MAX <= voiture.x < self.centre_x - ZONE_ATTENTE_EO_MIN:
                count += 1
        return count

    def compter_voitures_approchant_ns(self):
        """Compte les voitures qui approchent de l'intersection Nord-Sud"""
        count = 0
        # Voitures Nord approchant (dans les 200 pixels avant l'intersection)
        for voiture in self.voitures_nord:
            if voiture.y < self.centre_y - ZONE_ATTENTE_NS_MIN and voiture.y > self.centre_y - ZONE_APPROCHE_DISTANCE:
                count += 1
        # Voitures Sud approchant
        for voiture in self.voitures_sud:
            if voiture.y > self.centre_y + ZONE_ATTENTE_NS_MIN and voiture.y < self.centre_y + ZONE_APPROCHE_DISTANCE:
                count += 1
        return count

    def compter_voitures_approchant_eo(self):
        """Compte les voitures qui approchent de l'intersection Est-Ouest"""
        count = 0
        # Voitures Est approchant
        for voiture in self.voitures_est:
            if voiture.x > self.centre_x + ZONE_ATTENTE_EO_MIN and voiture.x < self.centre_x + ZONE_APPROCHE_DISTANCE:
                count += 1
        # Voitures Ouest approchant
        for voiture in self.voitures_ouest:
            if voiture.x < self.centre_x - ZONE_ATTENTE_EO_MIN and voiture.x > self.centre_x - ZONE_APPROCHE_DISTANCE:
                count += 1
        return count
