# feu_tricolore/voiture.py
import pygame
from feu_tricolore.meteo import meteo

class Voiture:
    """
    Représente une voiture animée dans la simulation.
    Modèle (Model) dans l'architecture MVC.
    """

    # Constantes de couleurs (pour les phares)
    JAUNE = (255, 255, 0)
    NOIR = (0, 0, 0)
    BLANC = (255, 255, 255)
    ROUGE = (255, 0, 0)
    BLEU = (0, 0, 255)

    # Son d'ambulance (variable de classe partagée)
    son_ambulance = None
    son_initialise = False

    @classmethod
    def initialiser_son_ambulance(cls):
        """Initialise le son d'ambulance une seule fois pour toutes les instances"""
        if not cls.son_initialise:
            try:
                # Créer un son de sirène synthétique avec Pygame
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
                cls.son_ambulance = cls._generer_son_sirene("europeenne")
                cls.son_initialise = True
            except Exception as e:
                print(f"Impossible d'initialiser le son d'ambulance: {e}")
                cls.son_ambulance = None
                cls.son_initialise = True

    @classmethod
    def _generer_son_sirene(cls, type_sirene="europeenne"):
        """
        Génère un son de sirène synthétique
        Types disponibles:
        - "europeenne" : Hi-Lo classique (660/960 Hz)
        - "americaine" : Wail montant/descendant
        - "yelp" : Rapide et urgent
        - "simple" : Bip-bip basique
        """
        try:
            import numpy as np

            # Paramètres du son
            sample_rate = 22050
            duration = 1.5  # 1.5 secondes
            t = np.linspace(0, duration, int(sample_rate * duration))

            if type_sirene == "europeenne":
                # Sirène européenne Hi-Lo (660/960 Hz)
                freq1 = 660
                freq2 = 960
                signal = np.zeros_like(t)
                for i, time in enumerate(t):
                    if (time % 0.5) < 0.25:
                        signal[i] = np.sin(2 * np.pi * freq1 * time)
                    else:
                        signal[i] = np.sin(2 * np.pi * freq2 * time)

            elif type_sirene == "americaine":
                # Sirène américaine "Wail" - fréquence qui monte et descend
                freq_min = 500
                freq_max = 1200
                # Modulation sinusoïdale de la fréquence
                freq = freq_min + (freq_max - freq_min) * (0.5 + 0.5 * np.sin(2 * np.pi * 1.5 * t))
                # Créer le signal avec fréquence variable
                phase = np.cumsum(2 * np.pi * freq / sample_rate)
                signal = np.sin(phase)

            elif type_sirene == "yelp":
                # Sirène "Yelp" - rapide et urgente
                freq_min = 600
                freq_max = 1400
                # Modulation rapide (4 cycles par seconde)
                freq = freq_min + (freq_max - freq_min) * (0.5 + 0.5 * np.sin(2 * np.pi * 4 * t))
                phase = np.cumsum(2 * np.pi * freq / sample_rate)
                signal = np.sin(phase)

            elif type_sirene == "simple":
                # Simple bip-bip (pour tests ou préférence minimaliste)
                freq = 800
                signal = np.zeros_like(t)
                # Créer des bips courts
                for i, time in enumerate(t):
                    if (time % 0.4) < 0.15:  # Bip de 0.15s toutes les 0.4s
                        signal[i] = np.sin(2 * np.pi * freq * time)

            else:
                # Par défaut: européenne
                return cls._generer_son_sirene("europeenne")

            # Ajouter une enveloppe pour éviter les clics
            envelope = np.minimum(t * 10, 1.0) * np.minimum((duration - t) * 10, 1.0)
            signal = signal * envelope * 0.3  # Volume à 30%

            # Convertir en format pygame
            signal = np.int16(signal * 32767)

            # Créer un tableau stéréo
            stereo_signal = np.column_stack((signal, signal))

            # Créer un objet Sound à partir du tableau numpy
            sound = pygame.sndarray.make_sound(stereo_signal)
            return sound

        except Exception as e:
            print(f"Impossible de générer le son de sirène: {e}")
            return None

    def __init__(self, x, y, direction, couleur, est_ambulance=False):
        """
        Initialise une voiture.

        Args:
            x (int): Position x initiale
            y (int): Position y initiale
            direction (str): Direction de déplacement ("N", "S", "E", "O")
            couleur (tuple): Couleur RGB de la voiture
            est_ambulance (bool): True si c'est une ambulance (priorité absolue)
        """
        self.x = x
        self.y = y
        self.direction = direction  # "N", "S", "E", "O"
        self.couleur = couleur
        self.est_ambulance = est_ambulance
        self.largeur = 40
        self.hauteur = 25
        self.vitesse_base = 5 if est_ambulance else 3  # Ambulance plus rapide
        self.temps_gyrophare = 0  # Pour animation du gyrophare

        # Gestion du son pour les ambulances
        if self.est_ambulance:
            # Initialiser le son si pas encore fait
            if not Voiture.son_initialise:
                Voiture.initialiser_son_ambulance()

            # Démarrer le son de sirène en boucle
            if Voiture.son_ambulance:
                try:
                    Voiture.son_ambulance.play(loops=-1)  # -1 = boucle infinie
                except Exception as e:
                    print(f"Erreur lors de la lecture du son: {e}")

    @property
    def vitesse(self):
        """Vitesse effective tenant compte de la météo."""
        return self.vitesse_base * meteo.facteur_vitesse

    def __del__(self):
        """Destructeur - arrête le son quand l'ambulance est détruite"""
        if self.est_ambulance and Voiture.son_ambulance:
            try:
                Voiture.son_ambulance.stop()
            except Exception:
                pass

    def deplacer(self, peut_avancer):
        """
        Déplace la voiture si autorisé.

        Args:
            peut_avancer (bool): True si la voiture peut avancer (feu vert)
        """
        if peut_avancer:
            if self.direction == "N":  # Nord -> Sud (descend)
                self.y += self.vitesse
            elif self.direction == "S":  # Sud -> Nord (monte)
                self.y -= self.vitesse
            elif self.direction == "E":  # Est -> Ouest (va vers la gauche)
                self.x -= self.vitesse
            elif self.direction == "O":  # Ouest -> Est (va vers la droite)
                self.x += self.vitesse

    def dessiner(self, ecran):
        """
        Dessine la voiture sur l'écran Pygame.

        Args:
            ecran (pygame.Surface): Surface Pygame sur laquelle dessiner
        """
        # Adapter le rectangle selon l'orientation
        if self.direction in ["N", "S"]:
            rect = pygame.Rect(self.x - self.hauteur//2, self.y - self.largeur//2,
                             self.hauteur, self.largeur)
        else:
            rect = pygame.Rect(self.x - self.largeur//2, self.y - self.hauteur//2,
                             self.largeur, self.hauteur)

        # Dessiner le corps de la voiture
        pygame.draw.rect(ecran, self.couleur, rect, border_radius=5)
        pygame.draw.rect(ecran, self.NOIR, rect, 2, border_radius=5)

        if self.est_ambulance:
            # Ambulance : dessin spécial avec croix rouge et gyrophare
            self._dessiner_ambulance(ecran, rect)
        else:
            # Dessiner les phares selon la direction
            self._dessiner_phares(ecran)

    

    def _dessiner_ambulance(self, ecran, rect):
        """
        Dessine les éléments distinctifs d'une ambulance.

        Args:
            ecran (pygame.Surface): Surface Pygame sur laquelle dessiner
            rect (pygame.Rect): Rectangle de la voiture
        """
        # Croix rouge au centre
        taille_croix = 10
        epaisseur = 3

        # Barre horizontale de la croix
        pygame.draw.rect(ecran, self.ROUGE,
                        (self.x - taille_croix//2, self.y - epaisseur//2,
                        taille_croix, epaisseur))
        # Barre verticale de la croix
        pygame.draw.rect(ecran, self.ROUGE,
                        (self.x - epaisseur//2, self.y - taille_croix//2,
                        epaisseur, taille_croix))

        # ═════════════════════════════════════════════════════════════
        # GYROPHARE AMÉLIORÉ - Plus intense et visible
        # ═════════════════════════════════════════════════════════════
        self.temps_gyrophare += 1
        
        # Effet stroboscopique : 3 niveaux d'intensité
        phase = (self.temps_gyrophare // 6) % 3
        
        if phase == 0:
            # Flash BLEU intense
            couleur_gyro = (0, 100, 255)  # Bleu vif
            rayon_gyro = 7
            rayon_halo = 12
        elif phase == 1:
            # Flash ROUGE intense
            couleur_gyro = (255, 50, 50)  # Rouge vif
            rayon_gyro = 7
            rayon_halo = 12
        else:
            # Éteint / Faible
            couleur_gyro = (50, 50, 100)  # Bleu très sombre
            rayon_gyro = 4
            rayon_halo = 0

        # Position du gyrophare selon la direction
        if self.direction in ["N", "S"]:
            gyro_x = self.x
            gyro_y = self.y - 15 if self.direction == "N" else self.y + 15
        else:
            gyro_x = self.x - 15 if self.direction == "E" else self.x + 15
            gyro_y = self.y

        # HALO LUMINEUX (effet de diffusion) - visible seulement pendant flash
        if rayon_halo > 0:
            # Cercle extérieur semi-transparent (effet glow)
            s = pygame.Surface((rayon_halo * 2 + 4, rayon_halo * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(s, (*couleur_gyro, 80), (rayon_halo + 2, rayon_halo + 2), rayon_halo)
            ecran.blit(s, (int(gyro_x) - rayon_halo - 2, int(gyro_y) - rayon_halo - 2))

        # Dessiner le gyrophare principal (plus gros)
        pygame.draw.circle(ecran, couleur_gyro, (int(gyro_x), int(gyro_y)), rayon_gyro)
        
        # Contour blanc pour visibilité
        pygame.draw.circle(ecran, self.BLANC, (int(gyro_x), int(gyro_y)), rayon_gyro, 2)
        
        # Reflet blanc (effet LED réaliste) - visible seulement pendant flash
        if rayon_gyro >= 6:
            pygame.draw.circle(ecran, self.BLANC, (int(gyro_x - 2), int(gyro_y - 2)), 2)

    def est_hors_zone(self, largeur_ecran, hauteur_ecran, marge=50):
        """
        Vérifie si la voiture est sortie de la zone visible.

        Args:
            largeur_ecran (int): Largeur de l'écran
            hauteur_ecran (int): Hauteur de l'écran
            marge (int): Marge de sécurité pour la suppression

        Returns:
            bool: True si la voiture est hors zone
        """
        return (self.x < -marge or self.x > largeur_ecran + marge or
                self.y < -marge or self.y > hauteur_ecran + marge)
    


    def _dessiner_phares(self, ecran):
        """
        Dessine les phares de la voiture selon sa direction.
        En mode pluie, ajoute un effet de faisceau lumineux.

        Args:
            ecran (pygame.Surface): Surface Pygame sur laquelle dessiner
        """
        # En mode pluie, dessiner d'abord les faisceaux lumineux
        if meteo.est_pluie:
            self._dessiner_faisceaux_lumineux(ecran)
        
        # Dessiner les phares (points jaunes)
        if self.direction == "N":
            pygame.draw.circle(ecran, self.JAUNE, (int(self.x - 6), int(self.y + 8)), 3)
            pygame.draw.circle(ecran, self.JAUNE, (int(self.x + 6), int(self.y + 8)), 3)
        elif self.direction == "S":
            pygame.draw.circle(ecran, self.JAUNE, (int(self.x - 6), int(self.y - 8)), 3)
            pygame.draw.circle(ecran, self.JAUNE, (int(self.x + 6), int(self.y - 8)), 3)
        elif self.direction == "E":  # Va vers l'Ouest (gauche) donc phares à gauche
            pygame.draw.circle(ecran, self.JAUNE, (int(self.x - 8), int(self.y - 6)), 3)
            pygame.draw.circle(ecran, self.JAUNE, (int(self.x - 8), int(self.y + 6)), 3)
        else:  # "O" - Va vers l'Est (droite) donc phares à droite
            pygame.draw.circle(ecran, self.JAUNE, (int(self.x + 8), int(self.y - 6)), 3)
            pygame.draw.circle(ecran, self.JAUNE, (int(self.x + 8), int(self.y + 6)), 3)
    
    def _dessiner_faisceaux_lumineux(self, ecran):
        """
        Dessine les faisceaux lumineux des phares en mode pluie.
        Crée un effet de cône de lumière devant la voiture.
        
        Args:
            ecran (pygame.Surface): Surface Pygame sur laquelle dessiner
        """
        # Longueur et largeur du faisceau
        longueur_faisceau = 30
        largeur_base = 12
        largeur_fin = 35
        
        # Créer une surface avec transparence pour le faisceau
        faisceau_surface = pygame.Surface((200, 200), pygame.SRCALPHA)
        
        # Couleur jaune semi-transparente (R, G, B, Alpha)
        # Couleurs plus claires et plus transparentes
        couleur_faisceau = (255, 255, 220, 60)  # jaune très clair, alpha plus bas
        couleur_centre = (255, 255, 240, 90)    # centre presque blanc, alpha plus bas


        
        if self.direction == "N":  # Descend - faisceau vers le bas
            # Points du trapèze (faisceau qui s'élargit)
            points = [
                (int(self.x - largeur_base/2), int(self.y + 8)),  # Haut gauche
                (int(self.x + largeur_base/2), int(self.y + 8)),  # Haut droit
                (int(self.x + largeur_fin/2), int(self.y + 8 + longueur_faisceau)),  # Bas droit
                (int(self.x - largeur_fin/2), int(self.y + 8 + longueur_faisceau))   # Bas gauche
            ]
            # Ligne centrale plus lumineuse
            pygame.draw.line(ecran, couleur_centre, 
                           (int(self.x), int(self.y + 8)),
                           (int(self.x), int(self.y + 8 + longueur_faisceau)), 2)
            
        elif self.direction == "S":  # Monte - faisceau vers le haut
            points = [
                (int(self.x - largeur_base/2), int(self.y - 8)),
                (int(self.x + largeur_base/2), int(self.y - 8)),
                (int(self.x + largeur_fin/2), int(self.y - 8 - longueur_faisceau)),
                (int(self.x - largeur_fin/2), int(self.y - 8 - longueur_faisceau))
            ]
            pygame.draw.line(ecran, couleur_centre,
                           (int(self.x), int(self.y - 8)),
                           (int(self.x), int(self.y - 8 - longueur_faisceau)), 2)
            
        elif self.direction == "E":  # Va vers l'Ouest (gauche)
            points = [
                (int(self.x - 8), int(self.y - largeur_base/2)),
                (int(self.x - 8), int(self.y + largeur_base/2)),
                (int(self.x - 8 - longueur_faisceau), int(self.y + largeur_fin/2)),
                (int(self.x - 8 - longueur_faisceau), int(self.y - largeur_fin/2))
            ]
            pygame.draw.line(ecran, couleur_centre,
                           (int(self.x - 8), int(self.y)),
                           (int(self.x - 8 - longueur_faisceau), int(self.y)), 2)
            
        else:  # "O" - Va vers l'Est (droite)
            points = [
                (int(self.x + 8), int(self.y - largeur_base/2)),
                (int(self.x + 8), int(self.y + largeur_base/2)),
                (int(self.x + 8 + longueur_faisceau), int(self.y + largeur_fin/2)),
                (int(self.x + 8 + longueur_faisceau), int(self.y - largeur_fin/2))
            ]
            pygame.draw.line(ecran, couleur_centre,
                           (int(self.x + 8), int(self.y)),
                           (int(self.x + 8 + longueur_faisceau), int(self.y)), 2)
        
        # Dessiner le trapèze du faisceau avec transparence
        pygame.draw.polygon(ecran, couleur_faisceau, points)
        
        # Ajouter un contour subtil pour plus de réalisme
        pygame.draw.polygon(ecran, (255, 255, 180, 40), points, 1)