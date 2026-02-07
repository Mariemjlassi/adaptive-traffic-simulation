import pygame
import sys
from collections import deque
from feu_tricolore.feu import Feu
from feu_tricolore.trafic import Trafic
from feu_tricolore.database import Database
from feu_tricolore.gestionnaire_voitures import GestionnaireVoitures
from feu_tricolore.gestionnaire_ambulances import GestionnaireAmbulances
from feu_tricolore.gestionnaire_rendu import GestionnaireRendu
from feu_tricolore.meteo import meteo
from feu_tricolore.constants import (
    LARGEUR, HAUTEUR, FPS,
    BLEU, VERT, ROUGE, ORANGE
)

# Initialisation Pygame
pygame.init()

class SimulationPygame:
    def __init__(self):
        self.ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
        pygame.display.set_caption("Simulation Intersection 4 Feux Intelligents")
        self.horloge = pygame.time.Clock()

        # État simulation
        self.db = Database()
        self.running = True
        self.simulation_active = False
        self.cycle_count = 0
        self.phase_actuelle = "NS_VERT"
        self.temps_depuis_dernier_tick = 0

        # 4 Feux (un pour chaque direction)
        self.feu_nord = Feu("Nord", couleur_initiale="Vert")
        self.feu_sud = Feu("Sud", couleur_initiale="Vert")
        self.feu_est = Feu("Est", couleur_initiale="Rouge")
        self.feu_ouest = Feu("Ouest", couleur_initiale="Rouge")

        # 4 Trafics
        self.trafic_nord = Trafic("Nord")
        self.trafic_sud = Trafic("Sud")
        self.trafic_est = Trafic("Est")
        self.trafic_ouest = Trafic("Ouest")

        # Statistiques
        from feu_tricolore.constants import TAILLE_HISTORIQUE_TRAFIC, CENTRE_X, CENTRE_Y
        self.historique_trafic_ns = deque(maxlen=TAILLE_HISTORIQUE_TRAFIC)
        self.historique_trafic_eo = deque(maxlen=TAILLE_HISTORIQUE_TRAFIC)
        self.compteur_pietons_ns = 0
        self.compteur_pietons_eo = 0
        self.temps_total_simulation = 0

        # Centre intersection (zone de simulation)
        self.centre_x = CENTRE_X
        self.centre_y = CENTRE_Y

        # Gestionnaires
        self.gestionnaire_voitures = GestionnaireVoitures(self.centre_x, self.centre_y, LARGEUR, HAUTEUR)
        self.gestionnaire_ambulances = GestionnaireAmbulances(self.centre_x, self.centre_y, LARGEUR, HAUTEUR)
        self.gestionnaire_rendu = GestionnaireRendu(self.ecran, self.centre_x, self.centre_y, LARGEUR, HAUTEUR)

    def gerer_clic(self, pos):
        """Gère les clics de souris"""
        # Bouton unique Start/Stop - vérifie l'état pour savoir quelle action effectuer
        if self.gestionnaire_rendu.btn_start.collidepoint(pos):
            if not self.simulation_active:
                self.demarrer_simulation()
            else:
                self.arreter_simulation()
        elif self.gestionnaire_rendu.btn_pieton_nord.collidepoint(pos):
            self.demander_pieton("Nord")
        elif self.gestionnaire_rendu.btn_pieton_sud.collidepoint(pos):
            self.demander_pieton("Sud")
        elif self.gestionnaire_rendu.btn_pieton_est.collidepoint(pos):
            self.demander_pieton("Est")
        elif self.gestionnaire_rendu.btn_pieton_ouest.collidepoint(pos):
            self.demander_pieton("Ouest")
        elif hasattr(self.gestionnaire_rendu, 'btn_urgence') and self.gestionnaire_rendu.btn_urgence.collidepoint(pos):
            self.simuler_accident()
        elif hasattr(self.gestionnaire_rendu, 'btn_ambulance_nord') and self.gestionnaire_rendu.btn_ambulance_nord.collidepoint(pos):
            self.spawner_ambulance("N")
        elif hasattr(self.gestionnaire_rendu, 'btn_ambulance_sud') and self.gestionnaire_rendu.btn_ambulance_sud.collidepoint(pos):
            self.spawner_ambulance("S")
        elif hasattr(self.gestionnaire_rendu, 'btn_ambulance_est') and self.gestionnaire_rendu.btn_ambulance_est.collidepoint(pos):
            self.spawner_ambulance("E")
        elif hasattr(self.gestionnaire_rendu, 'btn_ambulance_ouest') and self.gestionnaire_rendu.btn_ambulance_ouest.collidepoint(pos):
            self.spawner_ambulance("O")
        elif hasattr(self.gestionnaire_rendu, 'btn_meteo') and self.gestionnaire_rendu.btn_meteo and self.gestionnaire_rendu.btn_meteo.collidepoint(pos):
            self.toggle_meteo()

    def toggle_meteo(self):
        """Bascule l'état météo entre normal et pluie"""
        nouvel_etat = meteo.toggle()
        if nouvel_etat == "rain":
            # NOUVEAU: Démarrer le son de pluie
            self.gestionnaire_rendu.effet_pluie.demarrer_son()
            self.gestionnaire_rendu.afficher_message("Meteo: PLUIE - Vitesse reduite, distance augmentee", BLEU)
        else:
            # NOUVEAU: Arrêter le son de pluie
            self.gestionnaire_rendu.effet_pluie.arreter_son()
            self.gestionnaire_rendu.afficher_message("Meteo: NORMAL - Conditions normales", VERT)

    def demarrer_simulation(self):
        """Démarre la simulation"""
        if not self.simulation_active:
            self.simulation_active = True
            self.cycle_count = 0
            self.temps_total_simulation = 0
            from feu_tricolore.constants import PHASE_NS_VERT
            self.phase_actuelle = PHASE_NS_VERT

            # Initialisation Nord-Sud vert, Est-Ouest rouge
            self.feu_nord.set_couleur("Vert")
            self.feu_sud.set_couleur("Vert")
            self.feu_est.set_couleur("Rouge")
            self.feu_ouest.set_couleur("Rouge")

            # Créer des voitures initiales pour avoir du trafic dès le début
            self.gestionnaire_voitures.spawn_voitures_initial()

            self.gestionnaire_rendu.afficher_message("Simulation demarree! Intersection intelligente active", VERT)

    def arreter_simulation(self):
        """Arrête la simulation"""
        self.simulation_active = False
        self.gestionnaire_rendu.afficher_message("⏹ Simulation arrêtée", ROUGE)

    def demander_pieton(self, sens):
        """Demande passage piéton pour une direction"""
        if not self.simulation_active:
            self.gestionnaire_rendu.afficher_message("Demarrez d'abord la simulation!", ORANGE)
            return

        if sens == "Nord":
            self.feu_nord.request_pieton()
            self.compteur_pietons_ns += 1
            self.gestionnaire_rendu.afficher_message("Demande pieton NORD enregistree", BLEU)
        elif sens == "Sud":
            self.feu_sud.request_pieton()
            self.compteur_pietons_ns += 1
            self.gestionnaire_rendu.afficher_message("Demande pieton SUD enregistree", BLEU)
        elif sens == "Est":
            self.feu_est.request_pieton()
            self.compteur_pietons_eo += 1
            self.gestionnaire_rendu.afficher_message("Demande pieton EST enregistree", BLEU)
        elif sens == "Ouest":
            self.feu_ouest.request_pieton()
            self.compteur_pietons_eo += 1
            self.gestionnaire_rendu.afficher_message("Demande pieton OUEST enregistree", BLEU)

    def simuler_accident(self):
        """Simule un accident au centre de l'intersection"""
        if not self.simulation_active:
            self.gestionnaire_rendu.afficher_message("Demarrez d'abord la simulation!", ORANGE)
            return

        if self.gestionnaire_voitures.mode_urgence:
            self.gestionnaire_rendu.afficher_message("Un accident est deja en cours!", ORANGE)
            return

        # Déclencher l'accident via le gestionnaire
        success = self.gestionnaire_voitures.simuler_accident()
        if success:
            # Bloquer toutes les voies (utiliser set_couleur pour reset temps_restant)
            self.feu_nord.set_couleur("Rouge")
            self.feu_sud.set_couleur("Rouge")
            self.feu_est.set_couleur("Rouge")
            self.feu_ouest.set_couleur("Rouge")
            self.gestionnaire_rendu.afficher_message("ACCIDENT SIMULE ! Intervention d'urgence declenchee", ROUGE)

    def spawner_ambulance(self, direction):
        """Spawne une ambulance dans une direction donnée"""
        self.gestionnaire_ambulances.spawner_ambulance(
            direction,
            self.gestionnaire_voitures.voitures_nord,
            self.gestionnaire_voitures.voitures_sud,
            self.gestionnaire_voitures.voitures_est,
            self.gestionnaire_voitures.voitures_ouest
        )
        self.gestionnaire_rendu.afficher_message(f"AMBULANCE spawned direction {direction}!", ROUGE)

    def update_simulation(self):
        """Met à jour la logique (chaque seconde)"""
        if not self.simulation_active:
            return

        self.temps_total_simulation += 1

        # Réduire temps pour tous les feux
        self.feu_nord.reduire_temps()
        self.feu_sud.reduire_temps()
        self.feu_est.reduire_temps()
        self.feu_ouest.reduire_temps()

        # PROLONGER le feu vert si ambulance active et temps presque écoulé
        if self.gestionnaire_ambulances.ambulance_active is not None:
            if self.gestionnaire_ambulances.ambulance_active in ["N", "S"]:
                if self.feu_nord.temps_restant < 3:
                    self.feu_nord.temps_restant = 10
                    self.feu_sud.temps_restant = 10
                    self.gestionnaire_rendu.afficher_message(f"AMBULANCE {self.gestionnaire_ambulances.ambulance_active}: Prolongation +10s", ORANGE)
            else:
                if self.feu_est.temps_restant < 3:
                    self.feu_est.temps_restant = 10
                    self.feu_ouest.temps_restant = 10
                    self.gestionnaire_rendu.afficher_message(f"AMBULANCE {self.gestionnaire_ambulances.ambulance_active}: Prolongation +10s", ORANGE)

        self.traiter_phase_normale()

    def traiter_phase_normale(self):
        """Gère les transitions entre phases avec intelligence adaptative"""
        # BLOQUER transitions si ambulance active
        if self.gestionnaire_ambulances.ambulance_active is not None:
            return

        if self.phase_actuelle == "NS_VERT":
            # Nord et Sud au vert

            # INTELLIGENCE ADAPTATIVE : Passage anticipé si plus de voitures
            voitures_ns = self.gestionnaire_voitures.compter_voitures_approchant_ns() + self.gestionnaire_voitures.compter_voitures_en_attente_ns()
            voitures_eo_attente = self.gestionnaire_voitures.compter_voitures_en_attente_eo()

            # Si plus aucune voiture N-S ET des voitures E-O en attente ET feu vert depuis > 5s
            if (voitures_ns == 0 and voitures_eo_attente > 0 and
                self.feu_nord.temps_restant < self.feu_nord.duree_verte_actuelle - 5):
                self.gestionnaire_rendu.afficher_message("SMART: Plus de voitures N-S - Passage anticipe E-O!", ORANGE)
                self.feu_nord.temps_restant = 0 # Force la transition immédiate

            if self.feu_nord.temps_restant == 0:
                self.feu_nord.set_couleur("Orange")
                self.feu_sud.set_couleur("Orange")
                # S'assurer que E-O reste rouge
                self.feu_est.set_couleur("Rouge")
                self.feu_ouest.set_couleur("Rouge")
                self.phase_actuelle = "NS_ORANGE"

        elif self.phase_actuelle == "NS_ORANGE":
            if self.feu_nord.temps_restant == 0:
                self.feu_nord.set_couleur("Rouge")
                self.feu_sud.set_couleur("Rouge")

                # Activer piétons si demandés (SANS bloquer la transition)
                if self.feu_nord.demande_pieton and not self.feu_nord.pieton_vert:
                    self.feu_nord.start_pieton_phase()
                if self.feu_sud.demande_pieton and not self.feu_sud.pieton_vert:
                    self.feu_sud.start_pieton_phase()

                # IMPORTANT: Passer DIRECTEMENT E-O au vert
                # (même si N-S a des piétons actifs)
                self.passer_eo_vert()

        elif self.phase_actuelle == "EO_VERT":
            # Est et Ouest au vert

            # INTELLIGENCE ADAPTATIVE : Passage anticipé si plus de voitures
            voitures_eo = self.gestionnaire_voitures.compter_voitures_approchant_eo() + self.gestionnaire_voitures.compter_voitures_en_attente_eo()
            voitures_ns_attente = self.gestionnaire_voitures.compter_voitures_en_attente_ns()

            # Si plus aucune voiture E-O ET des voitures N-S en attente ET feu vert depuis > 5s
            if (voitures_eo == 0 and voitures_ns_attente > 0 and
                self.feu_est.temps_restant < self.feu_est.duree_verte_actuelle - 5):
                self.gestionnaire_rendu.afficher_message("SMART: Plus de voitures E-O - Passage anticipe N-S!", ORANGE)
                self.feu_est.temps_restant = 0

            if self.feu_est.temps_restant == 0:
                self.feu_est.set_couleur("Orange")
                self.feu_ouest.set_couleur("Orange")
                # S'assurer que N-S reste rouge
                self.feu_nord.set_couleur("Rouge")
                self.feu_sud.set_couleur("Rouge")
                self.phase_actuelle = "EO_ORANGE"

        elif self.phase_actuelle == "EO_ORANGE":
            if self.feu_est.temps_restant == 0:
                self.feu_est.set_couleur("Rouge")
                self.feu_ouest.set_couleur("Rouge")

                # Activer piétons si demandés (SANS bloquer la transition)
                if self.feu_est.demande_pieton and not self.feu_est.pieton_vert:
                    self.feu_est.start_pieton_phase()
                if self.feu_ouest.demande_pieton and not self.feu_ouest.pieton_vert:
                    self.feu_ouest.start_pieton_phase()

                # IMPORTANT: Passer DIRECTEMENT N-S au vert
                # (même si E-O a des piétons actifs)
                self.passer_ns_vert()

    def passer_ns_vert(self):
        """Passe Nord-Sud au vert avec durée adaptative intelligente"""
        self.cycle_count += 1

        self.trafic_nord.simuler_trafic()
        self.trafic_sud.simuler_trafic()

        # INTELLIGENCE ADAPTATIVE : Compter les vraies voitures
        voitures_en_attente = self.gestionnaire_voitures.compter_voitures_en_attente_ns()
        voitures_approchant = self.gestionnaire_voitures.compter_voitures_approchant_ns()
        total_voitures = voitures_en_attente + voitures_approchant

        # Calcul dynamique de la durée verte selon le trafic réel
        if total_voitures == 0:
            duree = 10
            msg = f"Phase N-S (Cycle #{self.cycle_count}) - Aucune voiture (10s)"
        elif total_voitures <= 3:
            duree = 15
            msg = f"Phase N-S (Cycle #{self.cycle_count}) - Trafic faible: {total_voitures} voitures (15s)"
        elif total_voitures <= 7:
            duree = 25
            msg = f"Phase N-S (Cycle #{self.cycle_count}) - Trafic moyen: {total_voitures} voitures (25s)"
        else:
            duree = 35
            msg = f"Phase N-S (Cycle #{self.cycle_count}) - Trafic eleve: {total_voitures} voitures (35s)"

        # Appliquer la durée calculée
        self.feu_nord.duree_verte_actuelle = duree
        self.feu_sud.duree_verte_actuelle = duree

        # CRITIQUE: Mettre N-S au VERT et E-O au ROUGE
        self.feu_nord.set_couleur("Vert")
        self.feu_sud.set_couleur("Vert")
        self.feu_est.set_couleur("Rouge")
        self.feu_ouest.set_couleur("Rouge")

        self.phase_actuelle = "NS_VERT"
        self.historique_trafic_ns.append(total_voitures)

        self.gestionnaire_rendu.afficher_message(msg, VERT)

    def passer_eo_vert(self):
        """Passe Est-Ouest au vert avec durée adaptative intelligente"""
        self.trafic_est.simuler_trafic()
        self.trafic_ouest.simuler_trafic()

        # INTELLIGENCE ADAPTATIVE : Compter les vraies voitures
        voitures_en_attente = self.gestionnaire_voitures.compter_voitures_en_attente_eo()
        voitures_approchant = self.gestionnaire_voitures.compter_voitures_approchant_eo()
        total_voitures = voitures_en_attente + voitures_approchant

        # Calcul dynamique de la durée verte selon le trafic réel
        if total_voitures == 0:
            duree = 10
            msg = f"Phase E-O (Cycle #{self.cycle_count}) - Aucune voiture (10s)"
        elif total_voitures <= 3:
            duree = 15
            msg = f"Phase E-O (Cycle #{self.cycle_count}) - Trafic faible: {total_voitures} voitures (15s)"
        elif total_voitures <= 7:
            duree = 25
            msg = f"Phase E-O (Cycle #{self.cycle_count}) - Trafic moyen: {total_voitures} voitures (25s)"
        else:
            duree = 35
            msg = f"Phase E-O (Cycle #{self.cycle_count}) - Trafic eleve: {total_voitures} voitures (35s)"

        # Appliquer la durée calculée
        self.feu_est.duree_verte_actuelle = duree
        self.feu_ouest.duree_verte_actuelle = duree

        # CRITIQUE: Mettre E-O au VERT et N-S au ROUGE
        self.feu_est.set_couleur("Vert")
        self.feu_ouest.set_couleur("Vert")
        self.feu_nord.set_couleur("Rouge")
        self.feu_sud.set_couleur("Rouge")

        self.phase_actuelle = "EO_VERT"
        self.historique_trafic_eo.append(total_voitures)

        self.gestionnaire_rendu.afficher_message(msg, VERT)

    def run(self):
        """Boucle principale"""
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Gestion du scroll avec la molette
                    if event.button == 4:  # Molette vers le haut
                        self.gestionnaire_rendu.gerer_scroll("up")
                    elif event.button == 5:  # Molette vers le bas
                        self.gestionnaire_rendu.gerer_scroll("down")
                    else:
                        self.gerer_clic(event.pos)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_SPACE:
                        if self.simulation_active:
                            self.arreter_simulation()
                        else:
                            self.demarrer_simulation()

            # Update simulation (1 tick/seconde)
            self.temps_depuis_dernier_tick += self.horloge.get_time()
            if self.temps_depuis_dernier_tick >= 1000:
                self.temps_depuis_dernier_tick = 0
                self.update_simulation()

            # Update voitures (chaque frame)
            if self.simulation_active:
                self.gestionnaire_voitures.spawn_voitures(self.trafic_nord, self.trafic_sud, self.trafic_est, self.trafic_ouest)
                self.gestionnaire_voitures.update_voitures(self.feu_nord, self.feu_sud, self.feu_est, self.feu_ouest)

                # Détection d'ambulances approchant (priorité absolue)
                direction_ambulance = self.gestionnaire_ambulances.detecter_ambulance_approchant(
                    self.gestionnaire_voitures.voitures_nord,
                    self.gestionnaire_voitures.voitures_sud,
                    self.gestionnaire_voitures.voitures_est,
                    self.gestionnaire_voitures.voitures_ouest,
                    self.gestionnaire_voitures.mode_urgence
                )
                if direction_ambulance:
                    result = self.gestionnaire_ambulances.activer_priorite_ambulance(direction_ambulance, self.phase_actuelle)
                    if result:
                        self.gestionnaire_rendu.afficher_message(f"AMBULANCE detectee direction {result} - FEU VERT IMMEDIAT!", ROUGE)
                        # PRIORITÉ ABSOLUE : Forcer IMMÉDIATEMENT le feu vert pour l'ambulance
                        if result in ["N", "S"]:
                            self.feu_nord.set_couleur("Vert")
                            self.feu_nord.duree_verte_actuelle = 30
                            self.feu_nord.temps_restant = 30
                            self.feu_sud.set_couleur("Vert")
                            self.feu_sud.duree_verte_actuelle = 30
                            self.feu_sud.temps_restant = 30
                            self.feu_est.set_couleur("Rouge")
                            self.feu_ouest.set_couleur("Rouge")
                            self.phase_actuelle = "NS_VERT"
                        else:
                            self.feu_est.set_couleur("Vert")
                            self.feu_est.duree_verte_actuelle = 30
                            self.feu_est.temps_restant = 30
                            self.feu_ouest.set_couleur("Vert")
                            self.feu_ouest.duree_verte_actuelle = 30
                            self.feu_ouest.temps_restant = 30
                            self.feu_nord.set_couleur("Rouge")
                            self.feu_sud.set_couleur("Rouge")
                            self.phase_actuelle = "EO_VERT"

                # Vérifier si ambulance passée
                if self.gestionnaire_ambulances.verifier_ambulance_passee(
                    self.gestionnaire_voitures.voitures_nord,
                    self.gestionnaire_voitures.voitures_sud,
                    self.gestionnaire_voitures.voitures_est,
                    self.gestionnaire_voitures.voitures_ouest
                ):
                    self.gestionnaire_rendu.afficher_message("Ambulance passee - Retour au mode adaptatif", VERT)

                # Détection de collisions (seulement si pas déjà en mode urgence)
                if not self.gestionnaire_voitures.mode_urgence:
                    collision = self.gestionnaire_voitures.detecter_collisions()
                    if collision:
                        v1, v2, dir1, dir2 = collision
                        self.gestionnaire_voitures.declencher_accident(v1, v2, dir1, dir2)
                        self.gestionnaire_rendu.afficher_message("ACCIDENT ! Intervention d'urgence en cours...", ROUGE)
                        # Bloquer toutes les voies
                        self.feu_nord.set_couleur("Rouge")
                        self.feu_sud.set_couleur("Rouge")
                        self.feu_est.set_couleur("Rouge")
                        self.feu_ouest.set_couleur("Rouge")

                # Gérer l'accident si actif
                if self.gestionnaire_voitures.accident_actif:
                    accident_termine = self.gestionnaire_voitures.gerer_accident()
                    if accident_termine:
                        self.gestionnaire_rendu.afficher_message("Intervention terminee - Reprise du trafic", VERT)
                        # Remettre les feux avec recalcul adaptatif
                        voitures_ns = self.gestionnaire_voitures.compter_voitures_en_attente_ns() + self.gestionnaire_voitures.compter_voitures_approchant_ns()
                        voitures_eo = self.gestionnaire_voitures.compter_voitures_en_attente_eo() + self.gestionnaire_voitures.compter_voitures_approchant_eo()
                        if voitures_ns >= voitures_eo:
                            self.passer_ns_vert()
                        else:
                            self.passer_eo_vert()

            # Rendu
            self.gestionnaire_rendu.dessiner_interface(
                self.simulation_active,
                self.gestionnaire_voitures.mode_urgence,
                self.feu_nord, self.feu_sud, self.feu_est, self.feu_ouest,
                self.gestionnaire_voitures.voitures_nord,
                self.gestionnaire_voitures.voitures_sud,
                self.gestionnaire_voitures.voitures_est,
                self.gestionnaire_voitures.voitures_ouest,
                self.gestionnaire_voitures.accident_actif,
                self.gestionnaire_voitures.temps_clignotement,
                self.cycle_count,
                self.temps_total_simulation,
                self.compteur_pietons_ns,
                self.compteur_pietons_eo,
                self.gestionnaire_voitures.compteur_accidents,
                self.gestionnaire_ambulances.compteur_ambulances,
                self.gestionnaire_ambulances.ambulance_active,
                self.historique_trafic_ns,
                self.historique_trafic_eo
            )
            pygame.display.flip()
            self.horloge.tick(FPS)

        self.db.fermer_connexion()
        pygame.quit()
        sys.exit()


def main():
    sim = SimulationPygame()
    sim.run()


if __name__ == "__main__":
    main()
