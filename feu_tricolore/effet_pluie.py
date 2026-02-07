import pygame
import random
import numpy as np

class EffetPluie:
    """Gère l'effet visuel de pluie à l'écran avec son"""
    
    # Variables de classe pour le son (partagées entre toutes les instances)
    son_pluie = None
    son_initialise = False
    
    @classmethod
    def initialiser_son_pluie(cls):
        """Initialise le son de pluie une seule fois pour toutes les instances"""
        if not cls.son_initialise:
            try:
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
                cls.son_pluie = cls._generer_son_pluie()
                cls.son_initialise = True
            except Exception as e:
                print(f"Impossible d'initialiser le son de pluie: {e}")
                cls.son_pluie = None
                cls.son_initialise = True
    
    @classmethod
    def _generer_son_pluie(cls):
        """
        Génère un son de pluie synthétique réaliste CONTINU
        Combine du bruit blanc filtré pour créer un effet de pluie constant
        """
        try:
            # Paramètres du son - DURÉE LONGUE pour continuité
            sample_rate = 22050
            duration = 8.0  # 8 secondes (boucle plus longue = plus fluide)
            
            # Générer du bruit blanc (base du son de pluie)
            t = np.linspace(0, duration, int(sample_rate * duration))
            
            # BRUIT BLANC CONTINU - Base constante
            noise = np.random.normal(0, 0.2, len(t))  # Amplitude augmentée pour volume
            
            # Ajouter des "gouttes" aléatoires TOUT AU LONG (pas de silence)
            num_drops = int(duration * 150)  # Plus de gouttes = son plus dense
            for _ in range(num_drops):
                drop_time = random.random() * duration
                drop_idx = int(drop_time * sample_rate)
                if drop_idx < len(noise) - 100:
                    # Créer une enveloppe pour la goutte
                    drop_length = random.randint(20, 60)
                    drop_envelope = np.exp(-np.linspace(0, 4, drop_length))
                    drop_sound = np.sin(2 * np.pi * random.randint(1800, 4500) * np.linspace(0, drop_length/sample_rate, drop_length))
                    drop_sound = drop_sound * drop_envelope * random.uniform(0.08, 0.25)
                    noise[drop_idx:drop_idx+drop_length] += drop_sound[:min(drop_length, len(noise)-drop_idx)]
            
            # Filtre passe-bas pour rendre le son plus doux (bruit constant)
            filtered = np.convolve(noise, np.ones(8)/8, mode='same')
            
            # Normaliser SANS réduire trop le volume (pour continuité perceptible)
            max_val = np.max(np.abs(filtered))
            if max_val > 0:
                filtered = filtered / max_val * 0.35  # Volume plus élevé
            
            # FADE ULTRA-COURT juste pour éviter clic lors boucle
            # (quasi imperceptible = continuité totale)
            fade_samples = int(sample_rate * 0.02)  # 0.02s seulement (20ms)
            filtered[:fade_samples] *= np.linspace(0.8, 1.0, fade_samples)  # Fade in doux
            filtered[-fade_samples:] *= np.linspace(1.0, 0.8, fade_samples)  # Fade out doux
            
            # Convertir en format pygame
            signal = np.int16(filtered * 32767)
            
            # Créer un tableau stéréo
            stereo_signal = np.column_stack((signal, signal))
            
            # Créer un objet Sound à partir du tableau numpy
            sound = pygame.sndarray.make_sound(stereo_signal)
            return sound
            
        except Exception as e:
            print(f"Impossible de générer le son de pluie: {e}")
            return None
    
    def __init__(self, largeur, hauteur):
        self.largeur = largeur
        self.hauteur = hauteur
        self.gouttes = []
        self.nombre_gouttes = 300  # Nombre de gouttes simultanées
        self.son_actif = False  # Pour savoir si le son joue actuellement
        
        # Initialiser le son si pas encore fait
        if not EffetPluie.son_initialise:
            EffetPluie.initialiser_son_pluie()
        
        # Créer les gouttes initiales
        self._creer_gouttes_initiales()
    
    def demarrer_son(self):
        """Démarre le son de pluie en boucle"""
        if EffetPluie.son_pluie and not self.son_actif:
            try:
                EffetPluie.son_pluie.play(loops=-1)  # -1 = boucle infinie
                self.son_actif = True
            except Exception as e:
                print(f"Erreur lors de la lecture du son de pluie: {e}")
    
    def arreter_son(self):
        """Arrête le son de pluie"""
        if EffetPluie.son_pluie and self.son_actif:
            try:
                EffetPluie.son_pluie.stop()
                self.son_actif = False
            except Exception:
                pass
    
    def _creer_gouttes_initiales(self):
        """Crée toutes les gouttes initiales réparties sur l'écran"""
        for _ in range(self.nombre_gouttes):
            self.gouttes.append(self._creer_nouvelle_goutte(position_aleatoire=True))
    
    def _creer_nouvelle_goutte(self, position_aleatoire=False):
        """
        Crée une nouvelle goutte de pluie
        
        Args:
            position_aleatoire: Si True, place la goutte aléatoirement sur tout l'écran
                              Si False, place la goutte en haut de l'écran
        """
        if position_aleatoire:
            # Position aléatoire sur tout l'écran (pour initialisation)
            x = random.randint(0, self.largeur)
            y = random.randint(0, self.hauteur)
        else:
            # Position en haut de l'écran (pour gouttes qui tombent)
            x = random.randint(0, self.largeur)
            y = random.randint(-50, -10)
        
        return {
            'x': x,
            'y': y,
            'vitesse': random.randint(8, 15),  # Vitesse de chute
            'longueur': random.randint(12, 25),  # Longueur de la goutte
            'opacite': random.randint(100, 180), # Transparence
            'vent': random.uniform(-0.5, 0.5)
        }
    
    def update(self):
        """Met à jour la position de toutes les gouttes"""
        for goutte in self.gouttes:
            # Faire tomber la goutte
            goutte['y'] += goutte['vitesse']
            goutte['x'] += goutte['vent'] 
            
            # Si la goutte sort de l'écran, la recréer en haut
            if goutte['y'] > self.hauteur:
                nouvelle = self._creer_nouvelle_goutte(position_aleatoire=False)
                goutte.update(nouvelle)
    
    def dessiner(self, surface):
        """
        Dessine toutes les gouttes de pluie + effet d'assombrissement
        
        Args:
            surface: Surface pygame sur laquelle dessiner
        """
        # 1. EFFET D'ASSOMBRISSEMENT (ciel gris)
        # Créer un voile semi-transparent gris sur tout l'écran
        voile_gris = pygame.Surface((self.largeur, self.hauteur), pygame.SRCALPHA)
        
        # Gris sombre avec 50 de transparence (0=invisible, 255=opaque)
        # Plus le chiffre est élevé, plus c'est sombre
        voile_gris.fill((45, 55, 75, 100))  # RGB gris + alpha (transparence)
        surface.blit(voile_gris, (0, 0))
        
        # 2. GOUTTES DE PLUIE
        for goutte in self.gouttes:
            # Couleur bleu-gris clair avec transparence
            couleur = (200, 210, 230, goutte['opacite'])
            
            # Créer une surface temporaire pour la transparence
            goutte_surface = pygame.Surface((3, goutte['longueur']), pygame.SRCALPHA)
            pygame.draw.line(
                goutte_surface,
                couleur,
                (1, 0),
                (1, goutte['longueur']),
                2
            )
            
            # Blitter la goutte sur la surface principale
            surface.blit(goutte_surface, (goutte['x'], goutte['y']))
    
    def __del__(self):
        """Destructeur - arrête le son quand l'effet est détruit"""
        self.arreter_son()