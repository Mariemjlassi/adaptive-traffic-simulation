# feu_tricolore/trafic.py
import random

class Trafic:
    """
    Simule le niveau de trafic pour une voie donnée, les piétons et les urgences.
    """
    def __init__(self, sens):
        self.sens = sens
        self.niveau = 0
        self.demande_pieton = False
        self.urgence = False
        self.compteur_vehicules = 0

    def simuler_trafic(self):
        """
        Génère un niveau de trafic aléatoire entre 1 et 10.
        """
        self.niveau = random.randint(1, 10)
        # Simulation réaliste du passage des véhicules
        if random.random() < 0.3:  # 30% de chance d'avoir un véhicule
            self.compteur_vehicules += random.randint(1, 3)

    def simuler_pieton(self, probabilite=0.1):
        """
        Simule une demande de passage piéton avec une faible probabilité.
        """
        if random.random() < probabilite:
            self.demande_pieton = True
            return f"🚶‍♂️ Demande piéton simulée sur {self.sens}"
        return None
    
    def simuler_urgence(self, probabilite=0.05):
        """
        Simule l'arrivée d'un véhicule d'urgence.
        """
        self.urgence = random.random() < probabilite
