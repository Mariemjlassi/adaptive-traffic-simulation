# feu_tricolore/feu.py
import time
from datetime import datetime
try:
    import winsound
except Exception:
    winsound = None

class Feu:
    """
    Représente un feu (voiture) et son feu piéton associé.
    Logique piéton :
      - demande_pieton : True si quelqu'un a demandé (mémoire)
      - pieton_vert : True si la phase piéton est active
      - temps_pieton_restant : temps restant pour piétons
    """
    def __init__(self, sens, couleur_initiale="Rouge", duree_verte=30, duree_pieton_min=7):
        self.sens = sens
        self.couleur = couleur_initiale  # "Rouge", "Orange", "Vert"
        self.duree_verte_base = duree_verte
        self.duree_verte_actuelle = duree_verte
        self.duree_orange = 3
        self.temps_restant = 0

        # Statistiques
        self.compteur_cycles = 0
        self.historique_temps_vert = []

        # Urgence / piéton
        self.en_urgence = False

        # PIETON: flags & timing
        self.demande_pieton = False        # mémoire d'une demande appuyée
        self.pieton_vert = False          # vrai si le feu piéton est vert maintenant
        self.temps_pieton_restant = 0
        self.duree_pieton_min = duree_pieton_min

    @property
    def duree_rouge(self):
        # Durée rouge = durée verte opposée + orange (approximation)
        return self.duree_verte_actuelle + self.duree_orange

    def set_couleur(self, nouvelle_couleur):
        """Met à jour la couleur et initialise temps_restant pour la phase."""
        self.couleur = nouvelle_couleur
        if nouvelle_couleur == "Vert":
            self.temps_restant = self.duree_verte_actuelle
        elif nouvelle_couleur == "Orange":
            self.temps_restant = self.duree_orange
        elif nouvelle_couleur == "Rouge":
            # Lorsqu'on met au rouge, on fixe un temps par défaut. 
            # Il pourra être prolongé si on doit servir un piéton.
            self.temps_restant = self.duree_rouge

    def reduire_temps(self):
        """Appeler chaque seconde pour diminuer les timers."""
        if self.temps_restant > 0:
            self.temps_restant -= 1
        if self.temps_pieton_restant > 0:
            self.temps_pieton_restant -= 1
            if self.temps_pieton_restant == 0:
                # Fin de la phase piéton
                self.end_pieton_phase()

    def ajuster_duree_verte(self, niveau_trafic):
        """Ajuste légèrement la durée verte selon le trafic."""
        if niveau_trafic > 7:
            self.duree_verte_actuelle = self.duree_verte_base + 2
        else:
            self.duree_verte_actuelle = self.duree_verte_base

    def enregistrer_temps_vert(self):
        self.historique_temps_vert.append(self.duree_verte_actuelle)

    def calculer_stats(self):
        if self.historique_temps_vert:
            return sum(self.historique_temps_vert) / len(self.historique_temps_vert)
        return 0

    def mode_urgence(self, en_cours=True):
        """Active le mode urgence (force rouge)."""
        self.en_urgence = en_cours
        if en_cours:
            self.set_couleur("Rouge")
            self.temps_restant = 10
            return f" URGENCE activée sur {self.sens}"
        else:
            # Fin d'urgence : on laisse le feu au rouge bref moment
            self.set_couleur("Rouge")
            self.temps_restant = 1
            self.en_urgence = False
            return f" URGENCE terminée sur {self.sens}"

    # -----------------------------
    # Gestion piéton (logique réelle)
    # -----------------------------
    def request_pieton(self):
        """
        Appelé quand quelqu'un appuie sur le bouton piéton.
        Comportement :
          - si feu voiture == Rouge --> démarrer phase piéton immédiatement
          - sinon (Vert ou Orange) --> mémoriser la demande (demande_pieton=True)
        """
        if self.couleur == "Rouge":
            # Si déjà en rouge et pas déjà en phase piéton, démarrer tout de suite
            if not self.pieton_vert:
                self.start_pieton_phase()
            else:
                # Si piéton déjà vert, on ne fait rien (déjà servi)
                pass
        else:
            # Vert ou Orange -> mémoriser la demande et attendre le prochain Rouge
            self.demande_pieton = True
        return True

    def start_pieton_phase(self):
        """
        Lance la phase piéton : bloque la circulation (feu voiture reste Rouge),
        met pieton_vert True et initialise temps_pieton_restant.
        """
        # Définir drapeau piéton actif
        self.pieton_vert = True
        self.demande_pieton = False
        # Garantir au minimum la durée piéton
        self.temps_pieton_restant = max(self.duree_pieton_min, 0)
        # Si le temps rouge restant est trop court pour la traversée,
        # on prolonge le rouge pour sécuriser la traversée.
        if self.temps_restant < self.temps_pieton_restant:
            self.temps_restant = self.temps_pieton_restant
        # Optionnel : bip sonore Windows
        if winsound:
            try:
                winsound.Beep(1000, 200)
            except Exception:
                pass
        return f" Passage piéton démarré sur {self.sens} ({self.temps_pieton_restant}s)"

    def end_pieton_phase(self):
        """Termine la phase piéton."""
        self.pieton_vert = False
        self.temps_pieton_restant = 0
        return f" Passage piéton terminé sur {self.sens}"
