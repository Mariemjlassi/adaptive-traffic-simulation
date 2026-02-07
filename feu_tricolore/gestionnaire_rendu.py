import pygame
import math
import random
from feu_tricolore.meteo import meteo
from feu_tricolore.constants import (
    BLANC, NOIR, GRIS, GRIS_CLAIR, GRIS_FONCE,
    VERT, ROUGE, ORANGE, BLEU, BLEU_FONCE, JAUNE,
    VERT_FONCE, VERT_GAZON,
    TAILLE_POLICE_TITRE, TAILLE_POLICE_NORMALE, TAILLE_POLICE_PETITE,
    DUREE_MESSAGE,
    PIETON_TETE_RAYON, PIETON_CORPS_LARGEUR, PIETON_CORPS_HAUTEUR,
    PIETON_JAMBE_LONGUEUR, PIETON_COULEUR_TETE, PIETON_COULEUR_CORPS,
    PIETON_COULEUR_CONTOUR, NOMBRE_PIETONS_SIMULTANES, DUREE_TRAVERSEE_PIETON
)

class GestionnaireRendu:
    def __init__(self, ecran, centre_x, centre_y, largeur, hauteur):
        self.ecran = ecran
        self.centre_x = centre_x
        self.centre_y = centre_y
        self.largeur = largeur
        self.hauteur = hauteur

        self.police_titre = pygame.font.Font(None, TAILLE_POLICE_TITRE)
        self.police_normale = pygame.font.Font(None, TAILLE_POLICE_NORMALE)
        self.police_petite = pygame.font.Font(None, TAILLE_POLICE_PETITE)

        # Message
        self.message = "Prêt à démarrer la simulation"
        self.message_couleur = BLEU
        self.message_temps = 0

        # Scroll du panneau de droite
        self.scroll_offset = 0
        self.scroll_max = 0
        self.header_height = 140  # Hauteur du header fixe

        # Animation piétons
        self.frame_count = 0  # Compteur de frames pour animation jambes

        # Texture d'herbe (générée une seule fois)
        self.texture_herbe = self._generer_texture_herbe()

        # Boutons
        self.btn_start = None
        self.btn_stop = None
        self.btn_pieton_nord = None
        self.btn_pieton_sud = None
        self.btn_pieton_est = None
        self.btn_pieton_ouest = None
        self.btn_urgence = None
        self.btn_ambulance_nord = None
        self.btn_ambulance_sud = None
        self.btn_ambulance_est = None
        self.btn_ambulance_ouest = None
        self.btn_meteo = None
        # NOUVEAU: Effet de pluie
        from feu_tricolore.effet_pluie import EffetPluie
        self.effet_pluie = EffetPluie(largeur, hauteur)

        

    def afficher_message(self, texte, couleur=BLEU):
        """Affiche un message temporaire"""
        self.message = texte
        self.message_couleur = couleur
        self.message_temps = DUREE_MESSAGE

    def gerer_scroll(self, direction):
        """Gère le défilement du panneau de droite"""
        scroll_speed = 30
        if direction == "up":
            self.scroll_offset = max(0, self.scroll_offset - scroll_speed)
        elif direction == "down":
            self.scroll_offset = min(self.scroll_max, self.scroll_offset + scroll_speed)

    def _generer_texture_herbe(self):
        """
        Génère une texture d'herbe réaliste avec variations de couleur.
        Version optimisée pour un chargement rapide.
        """
        texture = pygame.Surface((self.largeur, self.hauteur))
        base_r, base_g, base_b = VERT_GAZON
        texture.fill(VERT_GAZON)

        # Méthode rapide : créer une petite tuile et la répéter
        tuile_size = 64
        tuile = pygame.Surface((tuile_size, tuile_size))
        tuile.fill(VERT_GAZON)

        # Ajouter des variations sur la petite tuile seulement
        for _ in range(200):
            x = random.randint(0, tuile_size - 1)
            y = random.randint(0, tuile_size - 1)
            variation = random.randint(-20, 20)
            r = max(0, min(255, base_r + variation))
            g = max(0, min(255, base_g + variation + random.randint(-5, 10)))
            b = max(0, min(255, base_b + variation))
            pygame.draw.circle(tuile, (r, g, b), (x, y), random.randint(1, 2))

        # Ajouter quelques brins sur la tuile
        for _ in range(80):
            x = random.randint(0, tuile_size - 1)
            y = random.randint(2, tuile_size - 1)
            if random.random() > 0.5:
                couleur = (base_r - 25, base_g - 15, base_b - 25)
            else:
                couleur = (base_r + 15, base_g + 25, base_b + 8)
            couleur = tuple(max(0, min(255, c)) for c in couleur)
            pygame.draw.line(tuile, couleur, (x, y), (x, y - random.randint(2, 4)), 1)

        # Répéter la tuile sur toute la surface
        for tx in range(0, self.largeur, tuile_size):
            for ty in range(0, self.hauteur, tuile_size):
                texture.blit(tuile, (tx, ty))

        return texture

    def dessiner_route(self):
        """Dessine les routes et l'intersection"""
        # Fond gazon avec texture réaliste
        self.ecran.blit(self.texture_herbe, (0, 0))

        # Routes horizontales (Est-Ouest)
        pygame.draw.rect(self.ecran, GRIS_FONCE,
                        (0, self.centre_y - 120, self.largeur - 600, 240))

        # Routes verticales (Nord-Sud)
        pygame.draw.rect(self.ecran, GRIS_FONCE,
                        (self.centre_x - 120, 0, 240, self.hauteur))

        # Zone d'intersection centrale
        pygame.draw.rect(self.ecran, GRIS_FONCE,
                        (self.centre_x - 120, self.centre_y - 120, 240, 240))

        # Lignes de STOP (épaisses et rouges) avant chaque feu
        # Nord - ligne horizontale
        pygame.draw.rect(self.ecran, BLANC,
                        (self.centre_x - 90, self.centre_y - 140, 60, 8))

        # Sud - ligne horizontale
        pygame.draw.rect(self.ecran, BLANC,
                        (self.centre_x + 30, self.centre_y + 132, 60, 8))

        # Est - ligne verticale
        pygame.draw.rect(self.ecran, BLANC,
                        (self.centre_x + 132, self.centre_y - 90, 8, 60))

        # Ouest - ligne verticale
        pygame.draw.rect(self.ecran, BLANC,
                        (self.centre_x - 140, self.centre_y + 30, 8, 60))

        # Lignes blanches horizontales (en pointillés)
        for x in range(0, self.largeur - 600, 50):
            if x < self.centre_x - 130 or x > self.centre_x + 130:
                # Ligne centrale voie Nord (y = centre_y - 60)
                if self.centre_y - 70 > 120:
                    pygame.draw.rect(self.ecran, BLANC, (x, self.centre_y - 65, 30, 10))
                # Ligne centrale voie Sud (y = centre_y + 60)
                if self.centre_y + 70 < self.hauteur - 120:
                    pygame.draw.rect(self.ecran, BLANC, (x, self.centre_y + 55, 30, 10))

        # Lignes blanches verticales (en pointillés)
        for y in range(0, self.hauteur, 50):
            if y < self.centre_y - 130 or y > self.centre_y + 130:
                # Ligne centrale voie Ouest (x = centre_x - 60)
                pygame.draw.rect(self.ecran, BLANC, (self.centre_x - 65, y, 10, 30))
                # Ligne centrale voie Est (x = centre_x + 60)
                pygame.draw.rect(self.ecran, BLANC, (self.centre_x + 55, y, 10, 30))

        # Passages piétons (4 côtés)
        self.dessiner_passages_pietons()

    def dessiner_passages_pietons(self):
        """Dessine les 4 passages piétons"""
        largeur_bande = 20
        espacement = 25

        # Nord
        for i in range(9):
            pygame.draw.rect(self.ecran, BLANC,
                           (self.centre_x - 110 + i * espacement, self.centre_y - 135,
                            largeur_bande, 12))

        # Sud
        for i in range(9):
            pygame.draw.rect(self.ecran, BLANC,
                           (self.centre_x - 110 + i * espacement, self.centre_y + 123,
                            largeur_bande, 12))

        # Ouest
        for i in range(9):
            pygame.draw.rect(self.ecran, BLANC,
                           (self.centre_x - 135, self.centre_y - 110 + i * espacement,
                            12, largeur_bande))

        # Est
        for i in range(9):
            pygame.draw.rect(self.ecran, BLANC,
                           (self.centre_x + 123, self.centre_y - 110 + i * espacement,
                            12, largeur_bande))

    def dessiner_feu(self, x, y, feu, orientation="vertical", direction="E"):
        """Dessine un feu tricolore avec orientation et direction
        direction: 'E' pour Est (poteau à droite), 'O' pour Ouest (poteau à gauche)"""
        if orientation == "vertical":
            # Poteau
            pygame.draw.rect(self.ecran, GRIS_FONCE, (x - 8, y, 16, 100))

            # Boîtier
            pygame.draw.rect(self.ecran, NOIR, (x - 28, y - 8, 56, 90), border_radius=8)

            # Lumières
            rouge = ROUGE if feu.couleur == "Rouge" else GRIS
            orange = ORANGE if feu.couleur == "Orange" else GRIS
            vert = VERT if feu.couleur == "Vert" else GRIS

            pygame.draw.circle(self.ecran, rouge, (x, y + 12), 16)
            pygame.draw.circle(self.ecran, NOIR, (x, y + 12), 16, 2)

            pygame.draw.circle(self.ecran, orange, (x, y + 40), 16)
            pygame.draw.circle(self.ecran, NOIR, (x, y + 40), 16, 2)

            pygame.draw.circle(self.ecran, vert, (x, y + 68), 16)
            pygame.draw.circle(self.ecran, NOIR, (x, y + 68), 16, 2)

            # Timer
            texte = self.police_petite.render(f"{feu.temps_restant}s", True, BLANC)
            self.ecran.blit(texte, (x - 12, y + 85))

        else:  # horizontal
            if direction == "O":  # Ouest - poteau à gauche
                # Poteau à GAUCHE (court comme les autres)
                pygame.draw.rect(self.ecran, GRIS_FONCE, (x - 50, y - 8, 50, 16))

                # Boîtier
                pygame.draw.rect(self.ecran, NOIR, (x - 8, y - 28, 90, 56), border_radius=8)

                # Lumières (inversées pour Ouest)
                rouge = ROUGE if feu.couleur == "Rouge" else GRIS
                orange = ORANGE if feu.couleur == "Orange" else GRIS
                vert = VERT if feu.couleur == "Vert" else GRIS

                pygame.draw.circle(self.ecran, vert, (x + 12, y), 16)
                pygame.draw.circle(self.ecran, NOIR, (x + 12, y), 16, 2)

                pygame.draw.circle(self.ecran, orange, (x + 40, y), 16)
                pygame.draw.circle(self.ecran, NOIR, (x + 40, y), 16, 2)

                pygame.draw.circle(self.ecran, rouge, (x + 68, y), 16)
                pygame.draw.circle(self.ecran, NOIR, (x + 68, y), 16, 2)

                # Timer
                texte = self.police_petite.render(f"{feu.temps_restant}s", True, BLANC)
                self.ecran.blit(texte, (x + 30, y + 25))
            else:  # Est - poteau à droite (original)
                # Poteau à DROITE (court comme les autres)
                pygame.draw.rect(self.ecran, GRIS_FONCE, (x, y - 8, 100, 16))

                # Boîtier
                pygame.draw.rect(self.ecran, NOIR, (x - 8, y - 28, 90, 56), border_radius=8)

                # Lumières
                rouge = ROUGE if feu.couleur == "Rouge" else GRIS
                orange = ORANGE if feu.couleur == "Orange" else GRIS
                vert = VERT if feu.couleur == "Vert" else GRIS

                pygame.draw.circle(self.ecran, rouge, (x + 12, y), 16)
                pygame.draw.circle(self.ecran, NOIR, (x + 12, y), 16, 2)

                pygame.draw.circle(self.ecran, orange, (x + 40, y), 16)
                pygame.draw.circle(self.ecran, NOIR, (x + 40, y), 16, 2)

                pygame.draw.circle(self.ecran, vert, (x + 68, y), 16)
                pygame.draw.circle(self.ecran, NOIR, (x + 68, y), 16, 2)

                # Timer
                texte = self.police_petite.render(f"{feu.temps_restant}s", True, BLANC)
                self.ecran.blit(texte, (x + 30, y + 25))

    def dessiner_feu_pieton(self, x, y, feu):
        """Dessine un feu piéton"""
        couleur = VERT if feu.pieton_vert else ROUGE
        pygame.draw.rect(self.ecran, NOIR, (x - 15, y - 18, 30, 45), border_radius=5)
        pygame.draw.circle(self.ecran, couleur, (x, y), 12)
        pygame.draw.circle(self.ecran, NOIR, (x, y), 12, 2)

        if feu.pieton_vert:
            # Bonhomme qui marche (vert)
            pygame.draw.circle(self.ecran, NOIR, (x, y - 5), 3)
            pygame.draw.line(self.ecran, NOIR, (x, y - 2), (x, y + 5), 2)
            pygame.draw.line(self.ecran, NOIR, (x, y), (x - 3, y + 3), 2)
            pygame.draw.line(self.ecran, NOIR, (x, y), (x + 3, y + 3), 2)
            pygame.draw.line(self.ecran, NOIR, (x, y + 5), (x - 3, y + 10), 2)
            pygame.draw.line(self.ecran, NOIR, (x, y + 5), (x + 3, y + 10), 2)
        else:
            # Main levée (rouge)
            pygame.draw.circle(self.ecran, BLANC, (x, y - 4), 2)
            pygame.draw.line(self.ecran, BLANC, (x, y - 2), (x, y + 4), 2)
            pygame.draw.line(self.ecran, BLANC, (x - 2, y - 2), (x + 2, y - 2), 2)

    def dessiner_accident(self, accident_actif, temps_clignotement):
        """Dessine la visualisation de l'accident avec effets"""
        if not accident_actif:
            return

        pos_x, pos_y = accident_actif["position"]

        # Effet de clignotement
        if temps_clignotement % 20 < 10:
            # Cercle d'alerte rouge clignotant
            pygame.draw.circle(self.ecran, ROUGE, (pos_x, pos_y), 50, 5)
            pygame.draw.circle(self.ecran, ORANGE, (pos_x, pos_y), 35, 3)

        # Symbole d'accident (X rouge)
        taille = 40
        pygame.draw.line(self.ecran, ROUGE,
                        (pos_x - taille, pos_y - taille),
                        (pos_x + taille, pos_y + taille), 8)
        pygame.draw.line(self.ecran, ROUGE,
                        (pos_x + taille, pos_y - taille),
                        (pos_x - taille, pos_y + taille), 8)

        # Triangle d'avertissement
        if temps_clignotement % 30 < 15:
            points_triangle = [
                (pos_x, pos_y - 60),
                (pos_x - 50, pos_y + 40),
                (pos_x + 50, pos_y + 40)
            ]
            pygame.draw.polygon(self.ecran, ORANGE, points_triangle, 4)

            # Point d'exclamation dans le triangle
            pygame.draw.line(self.ecran, ROUGE, (pos_x, pos_y - 30), (pos_x, pos_y + 10), 3)
            pygame.draw.circle(self.ecran, ROUGE, (pos_x, pos_y + 20), 4)

        # Texte "ACCIDENT"
        texte_accident = self.police_normale.render("ACCIDENT", True, BLANC)
        rect_fond = pygame.Rect(pos_x - 60, pos_y - 90, 120, 35)
        pygame.draw.rect(self.ecran, ROUGE, rect_fond)
        pygame.draw.rect(self.ecran, BLANC, rect_fond, 2)
        self.ecran.blit(texte_accident, (pos_x - 55, pos_y - 85))

        # Compteur d'intervention
        temps_restant = accident_actif["duree"] // 60
        texte_temps = self.police_petite.render(f"Intervention: {temps_restant}s", True, BLANC)
        rect_temps = pygame.Rect(pos_x - 70, pos_y + 60, 140, 25)
        pygame.draw.rect(self.ecran, GRIS_FONCE, rect_temps)
        pygame.draw.rect(self.ecran, ORANGE, rect_temps, 2)
        self.ecran.blit(texte_temps, (pos_x - 65, pos_y + 63))

    def dessiner_card_shadow(self, surface, rect):
        """Dessine une ombre subtile pour les cards"""
        shadow_color = (0, 0, 0, 15)
        shadow_surf = pygame.Surface((rect.width + 4, rect.height + 4), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, shadow_color, (2, 2, rect.width, rect.height), border_radius=12)
        surface.blit(shadow_surf, (rect.x - 2, rect.y - 2))

    def dessiner_pieton(self, x, y, taille=1.0, type_pieton="adulte", progression=0.0):
        """Dessine un piéton avec animation et variation

        Args:
            x, y: Position du piéton (centre de la tête)
            taille: Facteur d'échelle (0.7=enfant, 1.0=adulte, 0.9=senior)
            type_pieton: "enfant", "adulte", ou "senior"
            progression: Position dans la marche (0.0 à 1.0) pour animation jambes
        """
        # Couleurs selon le type
        couleurs = {
            "enfant": ((40, 40, 40), (120, 120, 120)),      # Tête/Corps gris
            "adulte": ((50, 50, 50), (100, 100, 100)),      # Tête/Corps gris foncé
            "senior": ((60, 60, 60), (90, 90, 90))          # Tête/Corps gris moyen
        }
        couleur_tete, couleur_corps = couleurs.get(type_pieton, couleurs["adulte"])

        # Dimensions ajustées selon la taille
        tete_rayon = int(PIETON_TETE_RAYON * taille)
        corps_largeur = int(PIETON_CORPS_LARGEUR * taille)
        corps_hauteur = int(PIETON_CORPS_HAUTEUR * taille)
        jambe_longueur = int(PIETON_JAMBE_LONGUEUR * taille)

        # Tête (cercle)
        pygame.draw.circle(self.ecran, couleur_tete,
                          (int(x), int(y)), tete_rayon)
        pygame.draw.circle(self.ecran, PIETON_COULEUR_CONTOUR,
                          (int(x), int(y)), tete_rayon, 2)

        # Corps (rectangle)
        corps_y = y + tete_rayon
        corps_rect = pygame.Rect(
            int(x - corps_largeur // 2),
            int(corps_y),
            corps_largeur,
            corps_hauteur
        )
        pygame.draw.rect(self.ecran, couleur_corps, corps_rect, border_radius=3)
        pygame.draw.rect(self.ecran, PIETON_COULEUR_CONTOUR, corps_rect, 2, border_radius=3)

        # Jambes animées (marche réaliste - une avant, une arrière)
        jambe_y_start = corps_y + corps_hauteur

        # Animation de marche : oscillation continue
        # Chaque piéton a un décalage basé sur sa position
        phase_marche = (self.frame_count + (progression * 100)) * 0.15

        # Calcul du mouvement avant/arrière pour chaque jambe
        # sin() varie de -1 à +1, parfait pour avant/arrière
        mouvement_gauche = math.sin(phase_marche) * 8  # Amplitude de 8 pixels
        mouvement_droite = math.sin(phase_marche + math.pi) * 8  # Opposé (décalage de π)

        # Jambe GAUCHE (avance et recule)
        # Quand mouvement > 0 : jambe vers l'avant (direction de marche)
        # Quand mouvement < 0 : jambe vers l'arrière
        jambe_gauche_x = x - 3 + int(mouvement_gauche)
        jambe_gauche_y = jambe_y_start + jambe_longueur

        # Épaisseur variable : jambe devant = plus épaisse
        epaisseur_gauche = 4 if mouvement_gauche > 0 else 3
        pygame.draw.line(self.ecran, couleur_corps,
                        (int(x), int(jambe_y_start)),
                        (int(jambe_gauche_x), int(jambe_gauche_y)), epaisseur_gauche)

        # Jambe DROITE (opposée à la gauche)
        jambe_droite_x = x + 3 + int(mouvement_droite)
        jambe_droite_y = jambe_y_start + jambe_longueur

        # Épaisseur variable : jambe devant = plus épaisse
        epaisseur_droite = 4 if mouvement_droite > 0 else 3
        pygame.draw.line(self.ecran, couleur_corps,
                        (int(x), int(jambe_y_start)),
                        (int(jambe_droite_x), int(jambe_droite_y)), epaisseur_droite)

    def dessiner_pietons_traversant(self, feu_nord, feu_sud, feu_est, feu_ouest):
        """Affiche les piétons en train de traverser selon l'état des feux

        Args:
            feu_nord, feu_sud, feu_est, feu_ouest: Objets Feu

        Logique:
            - Passages Nord/Sud (verticaux) traversent la route E-O → contrôlés par feux EST/OUEST
            - Passages Est/Ouest (horizontaux) traversent la route N-S → contrôlés par feux NORD/SUD
        """
        # Configuration passages piétons
        # Chaque passage est contrôlé par SON feu spécifique
        # Passage Nord (haut, horizontal) → bouton Nord → feu Nord
        # Passage Sud (bas, horizontal) → bouton Sud → feu Sud
        # Passage Est (droite, vertical) → bouton Est → feu Est
        # Passage Ouest (gauche, vertical) → bouton Ouest → feu Ouest
        passages = {
            'Nord': {
                'actif': feu_nord.pieton_vert,
                'temps': feu_nord.temps_pieton_restant,
                'x_debut': self.centre_x + 120,
                'x_fin': self.centre_x - 120,
                'y_base': self.centre_y - 120,
                'direction': 'horizontal'
            },
            'Sud': {
                'actif': feu_sud.pieton_vert,
                'temps': feu_sud.temps_pieton_restant,
                'x_debut': self.centre_x - 120,
                'x_fin': self.centre_x + 120,
                'y_base': self.centre_y + 120,
                'direction': 'horizontal'
            },
            'Est': {
                'actif': feu_est.pieton_vert,
                'temps': feu_est.temps_pieton_restant,
                'x_base': self.centre_x + 120,
                'y_debut': self.centre_y + 120,
                'y_fin': self.centre_y - 120,
                'direction': 'vertical'
            },
            'Ouest': {
                'actif': feu_ouest.pieton_vert,
                'temps': feu_ouest.temps_pieton_restant,
                'x_base': self.centre_x - 120,
                'y_debut': self.centre_y - 120,
                'y_fin': self.centre_y + 120,
                'direction': 'vertical'
            }
        }

        # Dessiner piétons pour chaque passage actif
        for sens, passage in passages.items():
            if not passage['actif']:
                continue

            # Calculer progression (0.0 à 1.0)
            temps_restant = max(0, passage['temps'])
            progression_globale = 1 - (temps_restant / DUREE_TRAVERSEE_PIETON)

            # Compteur de piétons visibles
            pietons_count = 0

            # Générer piétons avec types aléatoires (seed basée sur le sens pour cohérence)
            random.seed(hash(sens))
            types_pietons = []
            for i in range(NOMBRE_PIETONS_SIMULTANES):
                type_choix = random.choice(["enfant", "adulte", "adulte", "senior"])  # Plus d'adultes
                taille_map = {"enfant": 0.7, "adulte": 1.0, "senior": 0.9}
                types_pietons.append((type_choix, taille_map[type_choix]))
            random.seed()  # Reset seed

            # Dessiner plusieurs piétons espacés le long de TOUTE la traversée
            for i in range(NOMBRE_PIETONS_SIMULTANES):
                # Chaque piéton démarre à un moment différent de la traversée
                # Étalement sur 1.5x la durée pour éviter regroupement
                offset = i / (NOMBRE_PIETONS_SIMULTANES * 1.5)
                progression = progression_globale - offset

                # Ne dessiner que si le piéton est dans la zone de traversée (0.0 à 1.0)
                if progression < 0 or progression > 1.0:
                    continue  # Piéton pas encore parti ou déjà arrivé

                # Récupérer type et taille de ce piéton
                type_pieton, taille = types_pietons[i]

                # Calculer position selon direction
                if passage['direction'] == 'vertical':
                    x = passage['x_base']
                    y_total = passage['y_fin'] - passage['y_debut']
                    y = passage['y_debut'] + y_total * progression

                    # Dessiner le piéton (déjà dans la zone 0-1)
                    self.dessiner_pieton(x, y, taille, type_pieton, progression)
                    pietons_count += 1

                else:  # horizontal
                    x_total = passage['x_fin'] - passage['x_debut']
                    x = passage['x_debut'] + x_total * progression
                    y = passage['y_base']

                    # Dessiner le piéton (déjà dans la zone 0-1)
                    self.dessiner_pieton(x, y, taille, type_pieton, progression)
                    pietons_count += 1

            # Afficher compteur visuel au-dessus du passage
            if pietons_count > 0:
                # Position du compteur
                if passage['direction'] == 'vertical':
                    compteur_x = passage['x_base']
                    compteur_y = self.centre_y - 150
                else:  # horizontal
                    compteur_x = self.centre_x
                    compteur_y = passage['y_base'] - 30

                # Fond du compteur
                texte_compteur = f"{pietons_count} piéton{'s' if pietons_count > 1 else ''}"
                texte_surf = self.police_petite.render(texte_compteur, True, BLANC)
                texte_rect = texte_surf.get_rect(center=(compteur_x, compteur_y))

                # Fond semi-transparent
                bg_rect = texte_rect.inflate(12, 8)
                bg_surf = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
                pygame.draw.rect(bg_surf, (0, 150, 0, 180), bg_surf.get_rect(), border_radius=8)
                self.ecran.blit(bg_surf, bg_rect.topleft)

                # Texte
                self.ecran.blit(texte_surf, texte_rect)

    def dessiner_stats_rapides(self, x, y, cycle_count, temps_total_simulation, simulation_active, feu_nord, feu_sud):
        """Dessine les 3 stats rapides dans le header (Cycle, Phase, Temps)"""
        card_width = 150  # Réduit de 170 à 150
        card_height = 36
        gap = 15
        start_x = x + 30

        # Phase actuelle - basée sur la couleur réelle des feux
        if simulation_active:
            # Vérifier quelle direction a le feu vert
            if feu_nord.couleur == "Vert" or feu_sud.couleur == "Vert":
                phase_text = "N-S"
            else:
                phase_text = "E-O"
        else:
            phase_text = "--"

        stats = [
            {"label": "Cycle", "value": f"#{cycle_count}", "bg": (239, 246, 255), "border": (191, 219, 254), "text": (29, 78, 216)},
            {"label": "Phase", "value": phase_text, "bg": (240, 253, 244), "border": (187, 247, 208), "text": (22, 163, 74)},
            {"label": "Temps", "value": f"{temps_total_simulation // 60}:{(temps_total_simulation % 60):02d}", "bg": (250, 245, 255), "border": (233, 213, 255), "text": (126, 34, 206)}
        ]

        for i, stat in enumerate(stats):
            sx = start_x + i * (card_width + gap)
            # Fond
            pygame.draw.rect(self.ecran, stat["bg"], (sx, y, card_width, card_height), border_radius=8)
            pygame.draw.rect(self.ecran, stat["border"], (sx, y, card_width, card_height), 1, border_radius=8)

            # Label
            label_surf = self.police_petite.render(stat["label"], True, stat["text"])
            self.ecran.blit(label_surf, (sx + 8, y + 5))

            # Valeur
            value_surf = self.police_normale.render(stat["value"], True, stat["text"])
            self.ecran.blit(value_surf, (sx + 8, y + 17))

    def dessiner_bouton_principal(self, x, y, simulation_active):
        """Dessine le bouton Démarrer/Arrêter dans le header"""
        btn_width = 470
        btn_height = 38
        btn_x = x + 60

        if not simulation_active:
            couleur_bg = (34, 197, 94)  # Vert vif
            texte_bouton = "> Démarrer"
        else:
            couleur_bg = (239, 68, 68)  # Rouge vif
            texte_bouton = "|| Arrêter"

        # Ombre subtile
        shadow_surf = pygame.Surface((btn_width + 4, btn_height + 4), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 30), (0, 0, btn_width + 4, btn_height + 4), border_radius=10)
        self.ecran.blit(shadow_surf, (btn_x - 2, y - 2))

        # Bouton
        pygame.draw.rect(self.ecran, couleur_bg, (btn_x, y, btn_width, btn_height), border_radius=10)

        # Texte centré
        texte = self.police_normale.render(texte_bouton, True, BLANC)
        texte_rect = texte.get_rect(center=(btn_x + btn_width // 2, y + btn_height // 2))
        self.ecran.blit(texte, texte_rect)

        # Sauvegarder le rectangle pour les clics
        self.btn_start = pygame.Rect(btn_x, y, btn_width, btn_height)
        self.btn_stop = pygame.Rect(btn_x, y, btn_width, btn_height)

    def dessiner_section_feux(self, surface, x, y, feu_nord, feu_sud, feu_est, feu_ouest):
        """Dessine la section État des Feux comme une card"""
        card_x = x + 30
        card_width = 530
        card_height = 230

        # Ombre de la card
        shadow_surf = pygame.Surface((card_width + 4, card_height + 4), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 20), (0, 0, card_width + 4, card_height + 4), border_radius=12)
        surface.blit(shadow_surf, (card_x - 2, y - 2))

        # Fond de la card
        pygame.draw.rect(surface, BLANC, (card_x, y, card_width, card_height), border_radius=12)
        pygame.draw.rect(surface, (229, 231, 235), (card_x, y, card_width, card_height), 1, border_radius=12)

        # Titre de la section avec point lumineux animé
        titre_y = y + 16
        pygame.draw.circle(surface, (34, 197, 94), (card_x + 16, titre_y + 6), 4)  # Point vert
        titre = self.police_petite.render("ÉTAT DES FEUX", True, (30, 41, 59))
        surface.blit(titre, (card_x + 28, titre_y))

        # Grille 2x2 des feux
        feux_data = [
            ("NORD", feu_nord, card_x + 16, y + 50),
            ("SUD", feu_sud, card_x + 280, y + 50),
            ("EST", feu_est, card_x + 16, y + 140),
            ("OUEST", feu_ouest, card_x + 280, y + 140)
        ]

        for direction, feu, fx, fy in feux_data:
            self.dessiner_feu_card(surface, fx, fy, direction, feu)

        return y + card_height

    def dessiner_feu_card(self, surface, x, y, direction, feu):
        """Dessine une mini-card pour un feu"""
        width = 240
        height = 75

        # Couleurs selon l'état
        if feu.couleur == "Vert":
            bg = (236, 253, 245)
            border = (167, 243, 208)
            text_color = (4, 120, 87)
            light_color = (34, 197, 94)
        elif feu.couleur == "Orange":
            bg = (255, 251, 235)
            border = (253, 224, 71)
            text_color = (161, 98, 7)
            light_color = (251, 191, 36)
        else:  # Rouge
            bg = (254, 242, 242)
            border = (252, 165, 165)
            text_color = (153, 27, 27)
            light_color = (239, 68, 68)

        # Fond
        pygame.draw.rect(surface, bg, (x, y, width, height), border_radius=10)
        pygame.draw.rect(surface, border, (x, y, width, height), 2, border_radius=10)

        # Direction et point lumineux
        pygame.draw.circle(surface, light_color, (x + 12, y + 18), 5)
        dir_text = self.police_petite.render(direction, True, text_color)
        surface.blit(dir_text, (x + 24, y + 12))

        # Timer
        timer_text = self.police_titre.render(f"{feu.temps_restant}s", True, text_color)
        surface.blit(timer_text, (x + width - 60, y + 8))

        # État textuel
        etat_text = self.police_petite.render(
            "Passage autorisé" if feu.couleur == "Vert" else "Arrêt obligatoire" if feu.couleur == "Rouge" else "Attention",
            True, text_color
        )
        etat_text.set_alpha(180)
        surface.blit(etat_text, (x + 12, y + 50))

        return y + height

    def dessiner_section_stats(self, surface, x, y, voitures_nord, voitures_sud, voitures_est, voitures_ouest, pietons_ns, pietons_eo):
        """Dessine la section Statistiques Temps Réel"""
        card_x = x + 30
        card_width = 530
        card_height = 185  # Optimisé

        # Ombre et fond
        shadow_surf = pygame.Surface((card_width + 4, card_height + 4), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 20), (0, 0, card_width + 4, card_height + 4), border_radius=12)
        surface.blit(shadow_surf, (card_x - 2, y - 2))

        pygame.draw.rect(surface, BLANC, (card_x, y, card_width, card_height), border_radius=12)
        pygame.draw.rect(surface, (229, 231, 235), (card_x, y, card_width, card_height), 1, border_radius=12)

        # Titre
        titre = self.police_petite.render("TRAFIC EN TEMPS RÉEL", True, (30, 41, 59))
        surface.blit(titre, (card_x + 16, y + 16))

        # Grille 2x2 des stats - Dimensions optimisées
        stats = [
            {"icon": "V", "label": "Véhicules N-S", "value": len(voitures_nord) + len(voitures_sud), "bg": (239, 246, 255), "border": (191, 219, 254), "text": (29, 78, 216)},
            {"icon": "V", "label": "Véhicules E-O", "value": len(voitures_est) + len(voitures_ouest), "bg": (239, 246, 255), "border": (191, 219, 254), "text": (29, 78, 216)},
            {"icon": "P", "label": "Piétons N-S", "value": pietons_ns, "bg": (240, 253, 244), "border": (187, 247, 208), "text": (22, 163, 74)},
            {"icon": "P", "label": "Piétons E-O", "value": pietons_eo, "bg": (240, 253, 244), "border": (187, 247, 208), "text": (22, 163, 74)}
        ]

        # Espacement optimisé: 2 cards de 235px + gap de 20px = 490px
        for i, stat in enumerate(stats):
            sx = card_x + 16 + (i % 2) * 245  # 235 + 20 = 255
            sy = y + 45 + (i // 2) * 75  # Hauteur card (65) + gap (10)
            self.dessiner_stat_card(surface, sx, sy, stat)

        return y + card_height

    def dessiner_stat_card(self, surface, x, y, stat):
        """Dessine une mini stat card"""
        width = 225  # Réduit pour bien rentrer dans le conteneur
        height = 60  # Réduit

        pygame.draw.rect(surface, stat["bg"], (x, y, width, height), border_radius=10)
        pygame.draw.rect(surface, stat["border"], (x, y, width, height), 2, border_radius=10)

        # Icône
        icon_text = self.police_normale.render(stat["icon"], True, stat["text"])
        surface.blit(icon_text, (x + 12, y + 10))

        # Label
        label_text = self.police_petite.render(stat["label"], True, stat["text"])
        label_text.set_alpha(180)
        surface.blit(label_text, (x + 40, y + 10))

        # Valeur
        value_text = self.police_titre.render(str(stat["value"]), True, stat["text"])
        surface.blit(value_text, (x + 40, y + 30))

    def dessiner_section_pietons(self, surface, x, y):
        """Dessine la section Contrôle Piétons"""
        card_x = x + 30
        card_width = 530
        card_height = 140  # Réduit pour bien contenir les boutons

        # Ombre et fond
        shadow_surf = pygame.Surface((card_width + 4, card_height + 4), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 20), (0, 0, card_width + 4, card_height + 4), border_radius=12)
        surface.blit(shadow_surf, (card_x - 2, y - 2))

        pygame.draw.rect(surface, BLANC, (card_x, y, card_width, card_height), border_radius=12)
        pygame.draw.rect(surface, (229, 231, 235), (card_x, y, card_width, card_height), 1, border_radius=12)

        # Titre
        titre = self.police_petite.render("CONTRÔLE PIÉTONS", True, (30, 41, 59))
        surface.blit(titre, (card_x + 16, y + 16))

        # Boutons 2x2 - Dimensions optimisées pour rentrer dans le conteneur
        # Largeur disponible: 530 - 32 (marges) = 498px
        # 2 boutons + 1 gap: (498 - gap) / 2 = btn_width
        btn_width = 241  # (498 - 16) / 2
        btn_height = 38
        gap = 16
        margin_top = 45
        boutons = [
            ("Nord", card_x + 16, y + margin_top),
            ("Sud", card_x + 16 + btn_width + gap, y + margin_top),
            ("Est", card_x + 16, y + margin_top + btn_height + 10),
            ("Ouest", card_x + 16 + btn_width + gap, y + margin_top + btn_height + 10)
        ]

        for i, (label, bx, by) in enumerate(boutons):
            pygame.draw.rect(surface, (239, 246, 255), (bx, by, btn_width, btn_height), border_radius=10)
            pygame.draw.rect(surface, (147, 197, 253), (bx, by, btn_width, btn_height), 2, border_radius=10)
            btn_text = self.police_normale.render(label, True, (29, 78, 216))
            btn_rect = btn_text.get_rect(center=(bx + btn_width // 2, by + btn_height // 2))
            surface.blit(btn_text, btn_rect)

            # Sauvegarder les rectangles de clic (position absolue à l'écran)
            # panel_x = largeur - 590, position absolue = panel_x + bx
            # position y à l'écran = header_height + (by - scroll_offset)
            panel_x = self.largeur - 590
            screen_x = panel_x + bx
            screen_y = self.header_height + by - self.scroll_offset

            if i == 0:
                self.btn_pieton_nord = pygame.Rect(screen_x, screen_y, btn_width, btn_height)
            elif i == 1:
                self.btn_pieton_sud = pygame.Rect(screen_x, screen_y, btn_width, btn_height)
            elif i == 2:
                self.btn_pieton_est = pygame.Rect(screen_x, screen_y, btn_width, btn_height)
            elif i == 3:
                self.btn_pieton_ouest = pygame.Rect(screen_x, screen_y, btn_width, btn_height)

        return y + card_height

    def dessiner_section_urgences(self, surface, x, y, mode_urgence):
        """Dessine la section Gestion Urgences"""
        card_x = x + 30
        card_width = 530
        card_height = 210  # Réduit pour bien contenir les boutons

        # Ombre et fond
        shadow_surf = pygame.Surface((card_width + 4, card_height + 4), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 20), (0, 0, card_width + 4, card_height + 4), border_radius=12)
        surface.blit(shadow_surf, (card_x - 2, y - 2))

        pygame.draw.rect(surface, BLANC, (card_x, y, card_width, card_height), border_radius=12)
        pygame.draw.rect(surface, (229, 231, 235), (card_x, y, card_width, card_height), 1, border_radius=12)

        # Titre
        titre = self.police_petite.render("GESTION URGENCES", True, (30, 41, 59))
        surface.blit(titre, (card_x + 16, y + 16))

        # Bouton Accident - Optimisé
        acc_y = y + 45
        acc_color = (239, 68, 68) if not mode_urgence else (185, 28, 28)
        pygame.draw.rect(surface, acc_color, (card_x + 16, acc_y, card_width - 32, 48), border_radius=10)
        acc_text = self.police_normale.render("! Simuler Accident", True, BLANC)
        acc_rect = acc_text.get_rect(center=(card_x + card_width // 2, acc_y + 24))
        surface.blit(acc_text, acc_rect)

        # Sauvegarder rectangle de clic (position absolue à l'écran)
        panel_x = self.largeur - 590
        screen_acc_x = panel_x + card_x + 16
        screen_acc_y = self.header_height + acc_y - self.scroll_offset
        self.btn_urgence = pygame.Rect(screen_acc_x, screen_acc_y, card_width - 32, 48)

        # Sous-titre Ambulances
        amb_title = self.police_petite.render("AMBULANCES", True, (100, 107, 115))
        surface.blit(amb_title, (card_x + 16, y + 108))

        # Boutons Ambulances 2x2 - Dimensions réduites
        btn_width = 230  # Réduit pour bien rentrer
        btn_height = 32
        gap = 20
        amb_y_start = y + 130
        boutons_amb = [
            ("Amb. N", card_x + 16, amb_y_start),
            ("Amb. S", card_x + 16 + btn_width + gap, amb_y_start),
            ("Amb. E", card_x + 16, amb_y_start + btn_height + 10),
            ("Amb. O", card_x + 16 + btn_width + gap, amb_y_start + btn_height + 10)
        ]

        for i, (label, bx, by) in enumerate(boutons_amb):
            pygame.draw.rect(surface, (255, 247, 237), (bx, by, btn_width, btn_height), border_radius=10)
            pygame.draw.rect(surface, (251, 146, 60), (bx, by, btn_width, btn_height), 1, border_radius=10)
            btn_text = self.police_normale.render(label, True, (234, 88, 12))
            btn_rect = btn_text.get_rect(center=(bx + btn_width // 2, by + btn_height // 2))
            surface.blit(btn_text, btn_rect)

            # Sauvegarder les rectangles de clic (position absolue à l'écran)
            screen_x = panel_x + bx
            screen_y = self.header_height + by - self.scroll_offset

            if i == 0:
                self.btn_ambulance_nord = pygame.Rect(screen_x, screen_y, btn_width, btn_height)
            elif i == 1:
                self.btn_ambulance_sud = pygame.Rect(screen_x, screen_y, btn_width, btn_height)
            elif i == 2:
                self.btn_ambulance_est = pygame.Rect(screen_x, screen_y, btn_width, btn_height)
            elif i == 3:
                self.btn_ambulance_ouest = pygame.Rect(screen_x, screen_y, btn_width, btn_height)

        return y + card_height

    def dessiner_section_meteo(self, surface, x, y):
        """Dessine la section Météo avec un bouton pour basculer normal/pluie"""
        card_x = x + 30
        card_width = 530
        card_height = 80

        # Ombre et fond
        shadow_surf = pygame.Surface((card_width + 4, card_height + 4), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 20), (0, 0, card_width + 4, card_height + 4), border_radius=12)
        surface.blit(shadow_surf, (card_x - 2, y - 2))

        pygame.draw.rect(surface, BLANC, (card_x, y, card_width, card_height), border_radius=12)
        pygame.draw.rect(surface, (229, 231, 235), (card_x, y, card_width, card_height), 1, border_radius=12)

        # Bouton Météo
        btn_y = y + 16
        btn_height = 48

        if meteo.est_pluie:
            btn_color = (59, 130, 246)  # Bleu vif (pluie)
            btn_text_str = "Meteo: PLUIE (cliquer pour soleil)"
        else:
            btn_color = (34, 197, 94)  # Vert (normal/soleil)
            btn_text_str = "Meteo: NORMAL (cliquer pour pluie)"

        pygame.draw.rect(surface, btn_color, (card_x + 16, btn_y, card_width - 32, btn_height), border_radius=10)
        btn_text = self.police_normale.render(btn_text_str, True, BLANC)
        btn_rect = btn_text.get_rect(center=(card_x + card_width // 2, btn_y + btn_height // 2))
        surface.blit(btn_text, btn_rect)

        # Sauvegarder rectangle de clic (position absolue à l'écran)
        panel_x = self.largeur - 590
        screen_x = panel_x + card_x + 16
        screen_y = self.header_height + btn_y - self.scroll_offset
        self.btn_meteo = pygame.Rect(screen_x, screen_y, card_width - 32, btn_height)

        return y + card_height

    def dessiner_section_evenements(self, surface, x, y, compteur_accidents, compteur_ambulances, mode_urgence):
        """Dessine la section Événements Récents"""
        card_x = x + 30
        card_width = 530
        # Hauteur optimisée selon le mode
        card_height = 168 if not mode_urgence else 223

        # Ombre et fond
        shadow_surf = pygame.Surface((card_width + 4, card_height + 4), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 20), (0, 0, card_width + 4, card_height + 4), border_radius=12)
        surface.blit(shadow_surf, (card_x - 2, y - 2))

        pygame.draw.rect(surface, BLANC, (card_x, y, card_width, card_height), border_radius=12)
        pygame.draw.rect(surface, (229, 231, 235), (card_x, y, card_width, card_height), 1, border_radius=12)

        # Titre
        titre = self.police_petite.render("ÉVÉNEMENTS RÉCENTS", True, (30, 41, 59))
        surface.blit(titre, (card_x + 16, y + 16))

        event_y = y + 45  # Réduit de 50 à 45
        event_height = 50  # Hauteur des cartes d'événements

        # Carte Accidents
        pygame.draw.rect(surface, (254, 242, 242), (card_x + 16, event_y, card_width - 32, event_height), border_radius=10)
        pygame.draw.rect(surface, (252, 165, 165), (card_x + 16, event_y, card_width - 32, event_height), 1, border_radius=10)
        icon_text = self.police_normale.render("!", True, (220, 38, 38))
        surface.blit(icon_text, (card_x + 28, event_y + 10))
        event_title = self.police_normale.render(f"{compteur_accidents} Accidents", True, (153, 27, 27))
        surface.blit(event_title, (card_x + 50, event_y + 10))
        event_sub = self.police_petite.render("Actifs dans la zone", True, (153, 27, 27))
        event_sub.set_alpha(180)
        surface.blit(event_sub, (card_x + 55, event_y + 28))

        event_y += 60  # event_height (50) + gap (10)

        # Carte Ambulances
        pygame.draw.rect(surface, (255, 247, 237), (card_x + 16, event_y, card_width - 32, event_height), border_radius=10)
        pygame.draw.rect(surface, (251, 191, 36), (card_x + 16, event_y, card_width - 32, event_height), 1, border_radius=10)
        icon_text = self.police_normale.render("+", True, (234, 88, 12))
        surface.blit(icon_text, (card_x + 28, event_y + 10))
        event_title = self.police_normale.render(f"{compteur_ambulances} Ambulances", True, (194, 65, 12))
        surface.blit(event_title, (card_x + 50, event_y + 10))
        event_sub = self.police_petite.render("En circulation", True, (194, 65, 12))
        event_sub.set_alpha(180)
        surface.blit(event_sub, (card_x + 55, event_y + 28))

        # Mode Urgence actif (si applicable)
        if mode_urgence:
            event_y += 60
            pygame.draw.rect(surface, (250, 245, 255), (card_x + 16, event_y, card_width - 32, event_height), border_radius=10)
            pygame.draw.rect(surface, (192, 132, 252), (card_x + 16, event_y, card_width - 32, event_height), 1, border_radius=10)
            icon_text = self.police_normale.render("*", True, (126, 34, 206))
            surface.blit(icon_text, (card_x + 28, event_y + 10))
            event_title = self.police_normale.render("Mode Urgence Actif", True, (107, 33, 168))
            surface.blit(event_title, (card_x + 50, event_y + 10))
            event_sub = self.police_petite.render("Priorité maximale", True, (107, 33, 168))
            event_sub.set_alpha(180)
            surface.blit(event_sub, (card_x + 55, event_y + 28))

        return y + card_height

    def dessiner_section_graphique(self, surface, x, y, historique_ns, historique_eo):
        """Dessine la section Graphique de trafic avec axes et labels clairs"""
        card_x = x + 30
        card_width = 530
        card_height = 220  # Augmenté pour faire de la place aux labels

        # Ombre et fond
        shadow_surf = pygame.Surface((card_width + 4, card_height + 4), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 20), (0, 0, card_width + 4, card_height + 4), border_radius=12)
        surface.blit(shadow_surf, (card_x - 2, y - 2))

        pygame.draw.rect(surface, BLANC, (card_x, y, card_width, card_height), border_radius=12)
        pygame.draw.rect(surface, (229, 231, 235), (card_x, y, card_width, card_height), 1, border_radius=12)

        # Titre
        titre = self.police_petite.render("TRAFIC (12 DERNIÈRES PHASES)", True, (30, 41, 59))
        surface.blit(titre, (card_x + 16, y + 16))

        # === ZONE GRAPHIQUE ===
        graph_x = card_x + 50      # Décalage pour laisser place à l'axe Y
        graph_y = y + 50
        graph_height = 100
        graph_width = card_width - 80  # Moins large pour les marges
        bar_count = 12

        # Combiner les données (N-S + E-O)
        combined_data = []
        for i in range(min(bar_count, len(historique_ns), len(historique_eo))):
            combined_data.append(historique_ns[i] + historique_eo[i])

        # Remplir avec des zéros si nécessaire
        while len(combined_data) < bar_count:
            combined_data.append(0)

        # Prendre les 12 derniers cycles
        data_to_display = combined_data[-bar_count:]
        max_value = max(data_to_display) if data_to_display and max(data_to_display) > 0 else 1

        # === DESSINER LES AXES ===
        # Axe Y (vertical, à gauche)
        pygame.draw.line(surface, (100, 116, 139), 
                        (graph_x, graph_y), 
                        (graph_x, graph_y + graph_height + 5), 2)
        
        # Axe X (horizontal, en bas)
        pygame.draw.line(surface, (100, 116, 139), 
                        (graph_x, graph_y + graph_height), 
                        (graph_x + graph_width, graph_y + graph_height), 2)

        # === LABELS AXE Y (Nombre de véhicules) ===
        # Label principal de l'axe Y
        label_y = self.police_petite.render("Véhicules", True, (100, 116, 139))
        # Rotation du texte (vertical)
        label_y_rotated = pygame.transform.rotate(label_y, 90)
        surface.blit(label_y_rotated, (card_x + 10, graph_y + graph_height // 2 - 25))

        # Graduations de l'axe Y (0, max/2, max)
        graduations_y = [0, max_value // 2, max_value]
        for i, val in enumerate(graduations_y):
            py = graph_y + graph_height - (i * graph_height // 2)
            # Trait de graduation
            pygame.draw.line(surface, (100, 116, 139), 
                            (graph_x - 5, py), (graph_x, py), 1)
            # Valeur
            val_text = self.police_petite.render(str(val), True, (100, 116, 139))
            surface.blit(val_text, (graph_x - 30, py - 8))

        # === DESSINER LES BARRES ===
        bar_width = graph_width // bar_count - 4

        for i, value in enumerate(data_to_display):
            bar_height = int((value / max_value) * graph_height) if max_value > 0 else 0
            bar_x = graph_x + 5 + i * (bar_width + 4)
            bar_y = graph_y + graph_height - bar_height

            # Gradient bleu selon intensité
            if value > max_value * 0.7:
                couleur_barre = (220, 38, 38)  # Rouge (trafic élevé)
            elif value > max_value * 0.4:
                couleur_barre = (251, 191, 36)  # Orange (trafic moyen)
            else:
                couleur_barre = (34, 197, 94)   # Vert (trafic faible)

            pygame.draw.rect(surface, couleur_barre, 
                            (bar_x, bar_y, bar_width, bar_height), border_radius=3)
            
            # Contour
            pygame.draw.rect(surface, (100, 116, 139), 
                            (bar_x, bar_y, bar_width, bar_height), 1, border_radius=3)

            # Valeur au-dessus de la barre (si assez haute)
            if bar_height > 15:
                val_text = self.police_petite.render(str(value), True, BLANC)
                val_rect = val_text.get_rect(center=(bar_x + bar_width // 2, bar_y + 8))
                surface.blit(val_text, val_rect)

        # === LABELS AXE X (Numéros de cycles) ===
        label_x = self.police_petite.render("Phases (cycles)", True, (100, 116, 139))
        label_x_rect = label_x.get_rect(center=(graph_x + graph_width // 2, 
                                                graph_y + graph_height + 25))
        surface.blit(label_x, label_x_rect)

        # Graduations de l'axe X (tous les 3 cycles)
        cycle_total = len(combined_data)
        for i in range(0, bar_count, 3):
            px = graph_x + 5 + i * (bar_width + 4) + bar_width // 2
            py = graph_y + graph_height
            
            # Trait de graduation
            pygame.draw.line(surface, (100, 116, 139), 
                            (px, py), (px, py + 5), 1)
            
            # Numéro de cycle
            cycle_num = cycle_total - bar_count + i + 1
            if cycle_num > 0:
                cycle_text = self.police_petite.render(str(cycle_num), True, (100, 116, 139))
                cycle_rect = cycle_text.get_rect(center=(px, py + 15))
                surface.blit(cycle_text, cycle_rect)

        # === LÉGENDE (N-S + E-O) ===
        legende_y = graph_y + graph_height + 40
        
        # Carré N-S (bleu)
        pygame.draw.rect(surface, (59, 130, 246), 
                        (card_x + 150, legende_y, 12, 12), border_radius=2)
        legende_ns = self.police_petite.render("N-S", True, (100, 116, 139))
        surface.blit(legende_ns, (card_x + 168, legende_y))

        # Carré E-O (orange)
        pygame.draw.rect(surface, (251, 146, 60), 
                        (card_x + 220, legende_y, 12, 12), border_radius=2)
        legende_eo = self.police_petite.render("E-O", True, (100, 116, 139))
        surface.blit(legende_eo, (card_x + 238, legende_y))

        # Info : Total combiné
        info_text = self.police_petite.render("(Somme N-S + E-O)", True, (100, 116, 139))
        info_text.set_alpha(150)
        surface.blit(info_text, (card_x + 300, legende_y))

        return y + card_height

    def dessiner_panel_droit(self, simulation_active, mode_urgence, feu_nord, feu_sud, feu_est, feu_ouest,
                            cycle_count, temps_total_simulation, voitures_nord, voitures_sud, voitures_est, voitures_ouest,
                            compteur_pietons_ns, compteur_pietons_eo, compteur_accidents, compteur_ambulances,
                            ambulance_active, historique_trafic_ns, historique_trafic_eo):
        """Dessine le panneau de contrôle à droite avec header fixe et contenu scrollable"""
        panel_x = self.largeur - 590
        panel_width = 590

        # Fond du panneau avec gradient
        pygame.draw.rect(self.ecran, (248, 249, 250), (panel_x, 0, panel_width, self.hauteur))
        pygame.draw.line(self.ecran, (220, 220, 230), (panel_x, 0), (panel_x, self.hauteur), 2)

        # ═══════════════════════════════════════════════════════
        # HEADER FIXE (non-scrollable)
        # ═══════════════════════════════════════════════════════
        header_bg = pygame.Surface((panel_width, self.header_height))
        header_bg.fill((255, 255, 255))
        self.ecran.blit(header_bg, (panel_x, 0))

        # Bordure en bas du header
        pygame.draw.line(self.ecran, (220, 220, 230), (panel_x, self.header_height),
                        (panel_x + panel_width, self.header_height), 2)

        # Titre
        titre = self.police_titre.render("CONTRÔLE INTERSECTION", True, (30, 41, 59))
        self.ecran.blit(titre, (panel_x + 90, 15))

        # Stats rapides en ligne (Cycle, Phase, Temps)
        y_stats = 55
        self.dessiner_stats_rapides(panel_x, y_stats, cycle_count, temps_total_simulation, simulation_active, feu_nord, feu_sud)

        # Bouton Démarrer/Arrêter
        y_btn = 98
        self.dessiner_bouton_principal(panel_x, y_btn, simulation_active)

        # ═══════════════════════════════════════════════════════
        # CONTENU SCROLLABLE
        # ═══════════════════════════════════════════════════════
        # Créer une surface pour le contenu scrollable
        content_height = 2000  # Hauteur totale du contenu (suffisamment grande)
        scroll_surface = pygame.Surface((panel_width, content_height))
        scroll_surface.fill((248, 249, 250))

        # Dessiner toutes les sections sur la surface scrollable
        y = 20  # Marge du haut augmentée

        # Section 1: État des feux
        y = self.dessiner_section_feux(scroll_surface, 0, y, feu_nord, feu_sud, feu_est, feu_ouest)
        y += 20  # Espacement entre sections augmenté

        # Section 2: Statistiques temps réel
        y = self.dessiner_section_stats(scroll_surface, 0, y, voitures_nord, voitures_sud,
                                       voitures_est, voitures_ouest, compteur_pietons_ns, compteur_pietons_eo)
        y += 20

        # Section 3: Contrôle Piétons
        y = self.dessiner_section_pietons(scroll_surface, 0, y)
        y += 20

        # Section 4: Gestion Urgences
        y = self.dessiner_section_urgences(scroll_surface, 0, y, mode_urgence)
        y += 20

        # Section 5: Météo
        y = self.dessiner_section_meteo(scroll_surface, 0, y)
        y += 20

        # Section 6: Événements récents
        y = self.dessiner_section_evenements(scroll_surface, 0, y, compteur_accidents,
                                             compteur_ambulances, mode_urgence)
        y += 20

        # Section 7: Graphique
        y = self.dessiner_section_graphique(scroll_surface, 0, y, historique_trafic_ns, historique_trafic_eo)
        y += 20  # Marge en bas

        # Calculer scroll_max
        scrollable_area_height = self.hauteur - self.header_height
        self.scroll_max = max(0, y - scrollable_area_height + 20)

        # Blitter la partie visible de la surface scrollable
        visible_rect = pygame.Rect(0, self.scroll_offset, panel_width, scrollable_area_height)
        self.ecran.blit(scroll_surface, (panel_x, self.header_height), visible_rect)

    def dessiner_boutons(self, x, y, simulation_active, mode_urgence):
        """Dessine les boutons de contrôle avec design moderne inspiré de l'image"""
        y_start = y  # Sauvegarder position de départ pour calcul des Rects

        # Bouton Démarrer/Arrêter unique - Change selon l'état
        if not simulation_active:
            # État arrêté - bouton vert "Démarrer"
            couleur_bg = (76, 175, 80)  # Vert vif comme l'image
            couleur_texte = BLANC
            texte_bouton = "▶  Démarrer"
        else:
            # État actif - bouton rouge "Arrêter"
            couleur_bg = (234, 67, 53)  # Rouge vif
            couleur_texte = BLANC
            texte_bouton = "⏸  Arrêter"

        # Dessiner le bouton unique centré
        pygame.draw.rect(self.ecran, couleur_bg, (x + 40, y, 510, 50), border_radius=10)
        texte = self.police_normale.render(texte_bouton, True, couleur_texte)
        texte_rect = texte.get_rect(center=(x + 295, y + 25))
        self.ecran.blit(texte, texte_rect)

        # Section PIÉTONS avec titre bien espacé
        y += 58
        titre_pietons = self.police_petite.render("PIÉTONS", True, (100, 100, 120))
        self.ecran.blit(titre_pietons, (x + 260, y))

        y += 20
        # Conteneur blanc avec bordure fine grise
        pygame.draw.rect(self.ecran, BLANC, (x + 40, y, 510, 110), border_radius=10)
        pygame.draw.rect(self.ecran, (230, 230, 235), (x + 40, y, 510, 110), 1, border_radius=10)

        # Boutons piétons (2x2 grid) - Bleu clair exactement comme l'image
        largeur_btn = 180
        hauteur_btn = 40
        espacement_h = 15
        espacement_v = 10
        marge_gauche = 65
        marge_haut = 15

        boutons_pietons = [
            ("Nord", x + marge_gauche, y + marge_haut),
            ("Sud", x + marge_gauche + largeur_btn + espacement_h, y + marge_haut),
            ("Est", x + marge_gauche, y + marge_haut + hauteur_btn + espacement_v),
            ("Ouest", x + marge_gauche + largeur_btn + espacement_h, y + marge_haut + hauteur_btn + espacement_v)
        ]

        for label, bx, by in boutons_pietons:
            # Bleu clair comme dans l'image
            pygame.draw.rect(self.ecran, (210, 230, 255), (bx, by, largeur_btn, hauteur_btn), border_radius=8)
            texte = self.police_normale.render(label, True, (60, 120, 220))
            texte_rect = texte.get_rect(center=(bx + largeur_btn//2, by + hauteur_btn//2))
            self.ecran.blit(texte, texte_rect)

        # Bouton SIMULER ACCIDENT - Rouge vif comme dans l'image
        y += 125  # 110 (hauteur conteneur) + 15 (espacement)
        couleur_accident_bg = (234, 67, 53) if not mode_urgence else (200, 40, 40)  # Rouge vif
        texte_couleur_accident = BLANC

        pygame.draw.rect(self.ecran, couleur_accident_bg, (x + 40, y, 510, 55), border_radius=10)
        texte_urgence = self.police_normale.render("⚠  Simuler Accident" if not mode_urgence else "⚠  ACCIDENT EN COURS",
                                                   True, texte_couleur_accident)
        texte_rect = texte_urgence.get_rect(center=(x + 295, y + 27))
        self.ecran.blit(texte_urgence, texte_rect)

        # Section AMBULANCES - Orange/beige clair comme dans l'image
        y += 70  # 55 (hauteur accident) + 15 (espacement)

        # Conteneur blanc avec bordure fine grise
        pygame.draw.rect(self.ecran, BLANC, (x + 40, y, 510, 110), border_radius=10)
        pygame.draw.rect(self.ecran, (230, 230, 235), (x + 40, y, 510, 110), 1, border_radius=10)

        # Boutons ambulances (2x2 grid) - Orange/beige clair
        boutons_ambulances = [
            ("Amb. N", x + marge_gauche, y + marge_haut),
            ("Amb. S", x + marge_gauche + largeur_btn + espacement_h, y + marge_haut),
            ("Amb. E", x + marge_gauche, y + marge_haut + hauteur_btn + espacement_v),
            ("Amb. O", x + marge_gauche + largeur_btn + espacement_h, y + marge_haut + hauteur_btn + espacement_v)
        ]

        for label, bx, by in boutons_ambulances:
            # Beige/orange clair comme dans l'image
            pygame.draw.rect(self.ecran, (255, 237, 213), (bx, by, largeur_btn, hauteur_btn), border_radius=5)
            texte = self.police_normale.render(label, True, (220, 120, 50))
            texte_rect = texte.get_rect(center=(bx + largeur_btn//2, by + hauteur_btn//2))
            self.ecran.blit(texte, texte_rect)

        # Bouton MÉTÉO - Bleu ciel si normal, bleu foncé si pluie
        y += 125  # 110 (hauteur conteneur ambulances) + 15 (espacement)
        if meteo.est_pluie:
            couleur_meteo_bg = (70, 130, 180)  # Bleu acier (pluie)
            texte_meteo = "🌧  Météo: PLUIE (cliquer pour soleil)"
        else:
            couleur_meteo_bg = (135, 206, 250)  # Bleu ciel (normal)
            texte_meteo = "☀  Météo: NORMAL (cliquer pour pluie)"

        pygame.draw.rect(self.ecran, couleur_meteo_bg, (x + 40, y, 510, 50), border_radius=10)
        texte = self.police_normale.render(texte_meteo, True, BLANC)
        texte_rect = texte.get_rect(center=(x + 295, y + 25))
        self.ecran.blit(texte, texte_rect)

        # Sauvegarder rectangles pour clics - calculés à partir de y_start
        # Bouton unique Start/Stop (y_start + 0)
        self.btn_start = pygame.Rect(x + 40, y_start, 510, 50)
        self.btn_stop = pygame.Rect(x + 40, y_start, 510, 50)

        # Piétons (y_start + 58 + 20 = y_start + 78)
        y_pietons_container = y_start + 78
        self.btn_pieton_nord = pygame.Rect(x + marge_gauche, y_pietons_container + marge_haut, largeur_btn, hauteur_btn)
        self.btn_pieton_sud = pygame.Rect(x + marge_gauche + largeur_btn + espacement_h, y_pietons_container + marge_haut, largeur_btn, hauteur_btn)
        self.btn_pieton_est = pygame.Rect(x + marge_gauche, y_pietons_container + marge_haut + hauteur_btn + espacement_v, largeur_btn, hauteur_btn)
        self.btn_pieton_ouest = pygame.Rect(x + marge_gauche + largeur_btn + espacement_h, y_pietons_container + marge_haut + hauteur_btn + espacement_v, largeur_btn, hauteur_btn)

        # Accident (y_start + 78 + 125 = y_start + 203)
        y_accident_button = y_start + 203
        self.btn_urgence = pygame.Rect(x + 40, y_accident_button, 510, 55)

        # Ambulances (y_start + 203 + 70 = y_start + 273)
        y_ambulances_container = y_start + 273
        self.btn_ambulance_nord = pygame.Rect(x + marge_gauche, y_ambulances_container + marge_haut, largeur_btn, hauteur_btn)
        self.btn_ambulance_sud = pygame.Rect(x + marge_gauche + largeur_btn + espacement_h, y_ambulances_container + marge_haut, largeur_btn, hauteur_btn)
        self.btn_ambulance_est = pygame.Rect(x + marge_gauche, y_ambulances_container + marge_haut + hauteur_btn + espacement_v, largeur_btn, hauteur_btn)
        self.btn_ambulance_ouest = pygame.Rect(x + marge_gauche + largeur_btn + espacement_h, y_ambulances_container + marge_haut + hauteur_btn + espacement_v, largeur_btn, hauteur_btn)

        # Météo (y_start + 273 + 125 = y_start + 398)
        self.btn_meteo = pygame.Rect(x + 40, y_start + 398, 510, 50)

    def dessiner_etat_feux(self, x, y, feu_nord, feu_sud, feu_est, feu_ouest):
        """Affiche l'état actuel des 4 feux avec design moderne"""
        BORDURE_FINE = (220, 220, 230)  # Bordure gris clair pour cohérence

        # Conteneur blanc avec bordure fine gris clair (même style que les autres sections)
        pygame.draw.rect(self.ecran, BLANC, (x + 40, y, 510, 180), border_radius=10)
        pygame.draw.rect(self.ecran, BORDURE_FINE, (x + 40, y, 510, 180), 1, border_radius=10)

        titre = self.police_petite.render("ÉTAT DES FEUX", True, (100, 100, 120))
        self.ecran.blit(titre, (x + 225, y + 12))

        feux_info = [
            ("NORD", feu_nord, x + 60, y + 50),
            ("SUD", feu_sud, x + 310, y + 50),
            ("EST", feu_est, x + 60, y + 110),
            ("OUEST", feu_ouest, x + 310, y + 110)
        ]

        for label, feu, fx, fy in feux_info:
            # Couleurs pastel modernes avec bordures fines
            if feu.couleur == "Vert":
                couleur_bg = (232, 245, 233)  # Vert pastel
                couleur_bordure = (76, 175, 80)  # Vert
                couleur_texte = (27, 94, 32)  # Vert foncé
            elif feu.couleur == "Orange":
                couleur_bg = (255, 243, 224)  # Orange pastel
                couleur_bordure = (255, 152, 0)  # Orange
                couleur_texte = (230, 81, 0)  # Orange foncé
            else:
                couleur_bg = (255, 235, 238)  # Rouge pastel
                couleur_bordure = (244, 67, 54)  # Rouge
                couleur_texte = (183, 28, 28)  # Rouge foncé

            # Fond pastel avec bordure fine
            pygame.draw.rect(self.ecran, couleur_bg, (fx, fy, 200, 45), border_radius=8)
            pygame.draw.rect(self.ecran, couleur_bordure, (fx, fy, 200, 45), 1, border_radius=8)

            texte = self.police_petite.render(f"{label}: {feu.couleur}", True, couleur_texte)
            self.ecran.blit(texte, (fx + 10, fy + 7))

            texte_temps = self.police_petite.render(f"{feu.temps_restant}s", True, couleur_texte)
            self.ecran.blit(texte_temps, (fx + 140, fy + 22))

    def dessiner_kpi(self, x, y, cycle_count, temps_total_simulation, voitures_nord, voitures_sud,
                    voitures_est, voitures_ouest, compteur_pietons_ns, compteur_pietons_eo,
                    compteur_accidents, mode_urgence, compteur_ambulances, ambulance_active):
        """Dessine les KPI avec style moderne"""
        # Couleurs modernes inspirées de l'image
        BLEU_CLAIR_TRANSPARENT = (173, 216, 230, 128)  # Bleu clair pour véhicules
        ROUGE_CLAIR_TRANSPARENT = (255, 182, 193, 128)  # Rose clair pour accidents
        ORANGE_CLAIR_TRANSPARENT = (255, 218, 185, 128)  # Orange clair pour ambulances
        BORDURE_FINE = (220, 220, 230)  # Bordure gris très clair

        # Cartes de statistiques principales (2x2 grid)
        cards = [
            {
                "label": " Véhicules N-S",
                "valeur": str(len(voitures_nord) + len(voitures_sud)),
                "couleur_fond": BLEU_CLAIR_TRANSPARENT,
                "couleur_texte": (65, 105, 225),  # Bleu royal
                "position": (x + 40, y + 20)
            },
            {
                "label": " Véhicules E-O",
                "valeur": str(len(voitures_est) + len(voitures_ouest)),
                "couleur_fond": BLEU_CLAIR_TRANSPARENT,
                "couleur_texte": (65, 105, 225),
                "position": (x + 295, y + 20)
            },
            {
                "label": " Accidents",
                "valeur": str(compteur_accidents),
                "couleur_fond": ROUGE_CLAIR_TRANSPARENT,
                "couleur_texte": (220, 53, 69),  # Rouge
                "position": (x + 40, y + 110)
            },
            {
                "label": " Ambulances",
                "valeur": str(compteur_ambulances),
                "couleur_fond": ORANGE_CLAIR_TRANSPARENT,
                "couleur_texte": (255, 140, 0),  # Orange foncé
                "position": (x + 295, y + 110)
            }
        ]

        # Dessiner les cartes principales
        for card in cards:
            cx, cy = card["position"]
            # Fond blanc transparent
            s = pygame.Surface((230, 70), pygame.SRCALPHA)
            s.fill((255, 255, 255, 250))
            pygame.draw.rect(s, card["couleur_fond"], (0, 0, 230, 70), border_radius=12)
            self.ecran.blit(s, (cx, cy))

            # Bordure fine
            pygame.draw.rect(self.ecran, BORDURE_FINE, (cx, cy, 230, 70), 1, border_radius=12)

            # Label en haut
            texte_label = self.police_petite.render(card["label"], True, (100, 100, 120))
            self.ecran.blit(texte_label, (cx + 15, cy + 12))

            # Valeur grande au centre
            font_grande = pygame.font.Font(None, 42)
            texte_valeur = font_grande.render(card["valeur"], True, card["couleur_texte"])
            self.ecran.blit(texte_valeur, (cx + 15, cy + 32))

        # Section "Contrôles" (piétons et mode urgence)
        y_controles = y + 210

        # Titre section
        titre = self.police_normale.render("CONTRÔLES", True, (80, 80, 100))
        self.ecran.blit(titre, (x + 230, y_controles))

        # Cartes piétons (2x2)
        pietons_cards = [
            ("Piétons N+S", str(compteur_pietons_ns), x + 40, y_controles + 40),
            ("Piétons E+O", str(compteur_pietons_eo), x + 295, y_controles + 40),
            ("Mode Urgence", "OUI" if mode_urgence else "NON", x + 40, y_controles + 100),
            ("Priorité Amb", ambulance_active if ambulance_active else "NON", x + 295, y_controles + 100)
        ]

        for label, valeur, px, py in pietons_cards:
            # Fond blanc avec bordure fine
            pygame.draw.rect(self.ecran, BLANC, (px, py, 230, 45), border_radius=8)
            pygame.draw.rect(self.ecran, BORDURE_FINE, (px, py, 230, 45), 1, border_radius=8)

            # Texte
            texte_label = self.police_petite.render(label, True, (100, 100, 120))
            texte_valeur = self.police_petite.render(str(valeur), True, BLEU_FONCE)
            self.ecran.blit(texte_label, (px + 12, py + 8))
            self.ecran.blit(texte_valeur, (px + 150, py + 20))

    def dessiner_graphique(self, x, y, historique_trafic_ns, historique_trafic_eo):
        """Dessine un graphique du trafic"""
        pygame.draw.rect(self.ecran, BLANC, (x + 40, y, 510, 180), border_radius=10)
        pygame.draw.rect(self.ecran, BLEU_FONCE, (x + 40, y, 510, 180), 3, border_radius=10)

        titre = self.police_normale.render("Trafic Temps Reel", True, BLEU_FONCE)
        self.ecran.blit(titre, (x + 180, y + 10))

        if len(historique_trafic_ns) > 1:
            # Axes
            pygame.draw.line(self.ecran, GRIS_FONCE, (x + 60, y + 150), (x + 520, y + 150), 2)
            pygame.draw.line(self.ecran, GRIS_FONCE, (x + 60, y + 40), (x + 60, y + 150), 2)

            # Ligne N-S
            points_ns = []
            for i, val in enumerate(historique_trafic_ns):
                px = x + 60 + (i * 440 // len(historique_trafic_ns))
                py = y + 150 - (val * 10)
                points_ns.append((px, py))

            if len(points_ns) > 1:
                pygame.draw.lines(self.ecran, BLEU, False, points_ns, 3)

            # Ligne E-O
            points_eo = []
            for i, val in enumerate(historique_trafic_eo):
                px = x + 60 + (i * 440 // len(historique_trafic_eo))
                py = y + 150 - (val * 10)
                points_eo.append((px, py))

            if len(points_eo) > 1:
                pygame.draw.lines(self.ecran, ROUGE, False, points_eo, 3)

            # Légende
            pygame.draw.line(self.ecran, BLEU, (x + 80, y + 165), (x + 110, y + 165), 3)
            texte = self.police_petite.render("N-S", True, BLEU)
            self.ecran.blit(texte, (x + 115, y + 158))

            pygame.draw.line(self.ecran, ROUGE, (x + 180, y + 165), (x + 210, y + 165), 3)
            texte = self.police_petite.render("E-O", True, ROUGE)
            self.ecran.blit(texte, (x + 215, y + 158))

    def dessiner_message(self):
        """Affiche le message en bas"""
        if self.message_temps > 0:
            pygame.draw.rect(self.ecran, self.message_couleur, (50, self.hauteur - 60, 900, 45),
                           border_radius=10)
            pygame.draw.rect(self.ecran, NOIR, (50, self.hauteur - 60, 900, 45), 2, border_radius=10)
            texte = self.police_normale.render(self.message, True, BLANC)
            self.ecran.blit(texte, (70, self.hauteur - 48))
            self.message_temps -= 1

    def dessiner_interface(self, simulation_active, mode_urgence, feu_nord, feu_sud, feu_est, feu_ouest,
                          voitures_nord, voitures_sud, voitures_est, voitures_ouest,
                          accident_actif, temps_clignotement, cycle_count, temps_total_simulation,
                          compteur_pietons_ns, compteur_pietons_eo, compteur_accidents,
                          compteur_ambulances, ambulance_active, historique_trafic_ns, historique_trafic_eo):
        """Dessine toute l'interface"""
        # Incrémenter compteur pour animation piétons
        self.frame_count += 1

        self.dessiner_route()

        # Dessiner les 4 feux tricolores aux bons emplacements (dans les zones vertes)
        # Nord (en haut, dans la zone verte à gauche de la route)
        self.dessiner_feu(self.centre_x - 150, self.centre_y - 220, feu_nord, "vertical")

        # Sud (en bas, dans la zone verte à droite de la route)
        self.dessiner_feu(self.centre_x + 150, self.centre_y + 140, feu_sud, "vertical")

        # Est (à droite, à côté de la route - comme Nord/Sud)
        self.dessiner_feu(self.centre_x + 130, self.centre_y - 150, feu_est, "horizontal", "E")

        # Ouest (à gauche, à côté de la route - comme Nord/Sud)
        self.dessiner_feu(self.centre_x - 205, self.centre_y + 150, feu_ouest, "horizontal", "O")

        # Feux piétons aux 4 coins de l'intersection (dans les zones vertes, loin de la route)
        # Coin Nord-Ouest (haut-gauche)
        self.dessiner_feu_pieton(self.centre_x - 200, self.centre_y - 190, feu_nord)
        # Coin Sud-Est (bas-droite)
        self.dessiner_feu_pieton(self.centre_x + 200, self.centre_y + 200, feu_sud)
        # Coin Nord-Est (haut-droite)
        self.dessiner_feu_pieton(self.centre_x + 190, self.centre_y - 190, feu_est)
        # Coin Sud-Ouest (bas-gauche)
        self.dessiner_feu_pieton(self.centre_x - 190, self.centre_y + 190, feu_ouest)

        # Dessiner piétons en train de traverser
        self.dessiner_pietons_traversant(feu_nord, feu_sud, feu_est, feu_ouest)

        # Dessiner voitures avec ordre de profondeur correct
        # Les voitures plus éloignées du centre doivent être dessinées en premier
        # pour créer un effet de profondeur réaliste
        toutes_voitures = voitures_nord + voitures_sud + voitures_est + voitures_ouest
        # Message en bas
        self.dessiner_message()
        
        # NOUVEAU: Dessiner la pluie si météo = pluie
        

        # Tri par profondeur : calculer la distance au centre pour chaque voiture
        # Les voitures loin du centre sont dessinées d'abord (arrière-plan)
        def distance_au_centre(voiture):
            dx = voiture.x - self.centre_x
            dy = voiture.y - self.centre_y
            return -(dx*dx + dy*dy)  # Négatif pour trier du plus loin au plus proche

        voitures_triees = sorted(toutes_voitures, key=distance_au_centre)

        for voiture in voitures_triees:
            voiture.dessiner(self.ecran)

        from feu_tricolore.meteo import meteo
        if meteo.est_pluie:
            self.effet_pluie.update()
            self.effet_pluie.dessiner(self.ecran)


            # ÉTAPE 3: Re-dessiner les faisceaux lumineux et phares PAR-DESSUS la pluie
            # pour qu'ils restent bien visibles et jaunes vifs
            for voiture in voitures_triees:
                # Dessiner uniquement les faisceaux et phares
                if hasattr(voiture, '_dessiner_faisceaux_lumineux'):
                    voiture._dessiner_faisceaux_lumineux(self.ecran)
                if hasattr(voiture, '_dessiner_phares_seuls'):
                    voiture._dessiner_phares_seuls(self.ecran)

        # Dessiner accident si actif
        if accident_actif:
            self.dessiner_accident(accident_actif, temps_clignotement)

        # Panel droit
        self.dessiner_panel_droit(simulation_active, mode_urgence, feu_nord, feu_sud, feu_est, feu_ouest,
                                 cycle_count, temps_total_simulation, voitures_nord, voitures_sud,
                                 voitures_est, voitures_ouest, compteur_pietons_ns, compteur_pietons_eo,
                                 compteur_accidents, compteur_ambulances, ambulance_active,
                                 historique_trafic_ns, historique_trafic_eo)

        # Message en bas
        self.dessiner_message()
