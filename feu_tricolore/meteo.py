
"""

    meteo.toggle()  # Bascule normal <-> pluie
    meteo.set_pluie()
    meteo.set_normal()
"""


class Meteo:

    # États possibles
    NORMAL = "normal"
    PLUIE = "rain"

    def __init__(self):
        self._etat = self.NORMAL

    @property
    def etat(self):
        """Retourne l'état météo actuel."""
        return self._etat

    def set_pluie(self):
        """Active le mode pluie."""
        self._etat = self.PLUIE

    def set_normal(self):
        """Retourne au mode normal."""
        self._etat = self.NORMAL

    def toggle(self):
        """Bascule entre normal et pluie."""
        if self._etat == self.NORMAL:
            self._etat = self.PLUIE
        else:
            self._etat = self.NORMAL
        return self._etat

    @property
    def facteur_vitesse(self):
        """
        Facteur de réduction de vitesse.
        - Normal: 1.0 (100% vitesse)
        - Pluie: 0.7 (-30% vitesse)
        """
        if self._etat == self.PLUIE:
            return 0.7
        return 1.0

    @property
    def facteur_distance_securite(self):
        """
        Facteur d'augmentation de la distance de sécurité.
        - Normal: 1.0 (distance standard)
        - Pluie: 1.2 (+20% distance de freinage)
        """
        if self._etat == self.PLUIE:
            return 1.2
        return 1.0

    @property
    def est_pluie(self):
        """Retourne True si météo = pluie."""
        return self._etat == self.PLUIE

    @property
    def est_normal(self):
        """Retourne True si météo = normal."""
        return self._etat == self.NORMAL
    

    


# Instance globale unique (singleton)
meteo = Meteo()
