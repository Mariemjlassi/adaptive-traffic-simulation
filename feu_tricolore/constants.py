# feu_tricolore/constants.py
"""
Fichier centralisé de toutes les constantes du projet.
Regroupe les dimensions, couleurs, durées et paramètres de configuration.
"""

# =============================================================================
# DIMENSIONS DE LA FENÊTRE
# =============================================================================
LARGEUR = 1600
HAUTEUR = 900
FPS = 60

# =============================================================================
# COULEURS DE BASE
# =============================================================================
BLANC = (255, 255, 255)
NOIR = (0, 0, 0)
GRIS = (128, 128, 128)
GRIS_CLAIR = (200, 200, 200)
GRIS_FONCE = (80, 80, 80)
VERT = (0, 200, 0)
ROUGE = (255, 0, 0)
ORANGE = (255, 165, 0)
BLEU = (30, 144, 255)
BLEU_FONCE = (0, 51, 102)
JAUNE = (255, 255, 0)
VERT_FONCE = (0, 100, 0)
VERT_GAZON = (85, 170, 85)

# =============================================================================
# COULEURS PASTEL PROFESSIONNELLES (BOUTONS)
# =============================================================================
VERT_PASTEL = (144, 238, 144)
VERT_PASTEL_ACTIF = (102, 205, 102)
ROUGE_PASTEL = (255, 160, 160)
ROUGE_PASTEL_ACTIF = (220, 100, 100)
BLEU_PASTEL = (173, 216, 230)
ORANGE_PASTEL = (250, 172, 104)
ROUGE_URGENCE = (96, 139, 193)

# =============================================================================
# COULEURS DES FEUX MODERNES
# =============================================================================
VERT_FEU = (76, 175, 80)
ROUGE_FEU = (244, 67, 54)
ORANGE_FEU = (255, 152, 0)

# =============================================================================
# COULEURS POUR VOITURES
# =============================================================================
COULEURS_VOITURES = [
    ROUGE,
    BLEU,
    VERT_FONCE,
    ORANGE,
    (128, 0, 128),      # Violet
    (255, 192, 203)     # Rose
]

# =============================================================================
# DIMENSIONS DE L'INTERSECTION
# =============================================================================
CENTRE_X = 500
CENTRE_Y = 450

# =============================================================================
# PARAMÈTRES DE SPAWN DES VOITURES
# =============================================================================
INTERVALLE_SPAWN_VOITURES = 30  # frames entre chaque spawn
PROBABILITE_SPAWN = 0.4  # Probabilité de ne pas spawn (0.4 = 60% de chance)
VOITURES_INITIALES_MIN = 2
VOITURES_INITIALES_MAX = 3

# =============================================================================
# PARAMÈTRES DE COLLISION ET SÉCURITÉ
# =============================================================================
DISTANCE_SECURITE_VOITURE = 50  # Distance minimale entre voitures
SEUIL_COLLISION_X = 35  # Seuil de collision horizontal
SEUIL_COLLISION_Y = 30  # Seuil de collision vertical

# =============================================================================
# ZONES D'INTERSECTION
# =============================================================================
ZONE_INTERSECTION_DEMI_LARGEUR = 120
ZONE_INTERSECTION_DEMI_HAUTEUR = 120

# =============================================================================
# PARAMÈTRES D'ACCIDENTS
# =============================================================================
DUREE_INTERVENTION_ACCIDENT = 300  # frames (5 secondes à 60 FPS)

# =============================================================================
# PARAMÈTRES AMBULANCES
# =============================================================================
DISTANCE_DETECTION_AMBULANCE = 300  # pixels avant l'intersection
DUREE_VERTE_AMBULANCE = 30  # secondes de feu vert pour ambulance
PROLONGATION_AMBULANCE = 10  # secondes de prolongation si nécessaire

# =============================================================================
# DURÉES DES FEUX (ADAPTATIF)
# =============================================================================
# Durée verte minimale (aucune voiture)
DUREE_VERTE_MIN = 10

# Durée verte pour trafic faible (1-3 voitures)
DUREE_VERTE_FAIBLE = 15
SEUIL_TRAFIC_FAIBLE = 3

# Durée verte pour trafic moyen (4-7 voitures)
DUREE_VERTE_MOYEN = 25
SEUIL_TRAFIC_MOYEN = 7

# Durée verte pour trafic élevé (8+ voitures)
DUREE_VERTE_ELEVE = 35

# Délai pour passage anticipé (secondes depuis début du vert)
DELAI_PASSAGE_ANTICIPE = 5

# =============================================================================
# PARAMÈTRES D'HISTORIQUE ET STATISTIQUES
# =============================================================================
TAILLE_HISTORIQUE_TRAFIC = 30  # nombre de points dans le graphique

# =============================================================================
# DURÉE D'AFFICHAGE DES MESSAGES
# =============================================================================
DUREE_MESSAGE = 180  # frames (3 secondes à 60 FPS)

# =============================================================================
# PARAMÈTRES DE TAILLE DES POLICES
# =============================================================================
TAILLE_POLICE_TITRE = 40
TAILLE_POLICE_NORMALE = 28
TAILLE_POLICE_PETITE = 22

# =============================================================================
# POSITIONS DES ÉLÉMENTS GRAPHIQUES
# =============================================================================
# Panel de contrôle
PANEL_LARGEUR = 590
PANEL_DECALAGE_X = LARGEUR - PANEL_LARGEUR

# Dimensions des boutons
LARGEUR_BOUTON_PRINCIPAL = 240
HAUTEUR_BOUTON_PRINCIPAL = 50
LARGEUR_BOUTON_SECONDAIRE = 130
HAUTEUR_BOUTON_SECONDAIRE = 40
ESPACEMENT_BOUTONS = 10

# =============================================================================
# PARAMÈTRES DE DESSIN DE LA ROUTE
# =============================================================================
LARGEUR_ROUTE = 240
LARGEUR_LIGNE_BLANCHE = 30
HAUTEUR_LIGNE_BLANCHE = 10
ESPACEMENT_LIGNES = 50

# Passages piétons
LARGEUR_BANDE_PIETON = 20
ESPACEMENT_BANDES_PIETON = 25
NOMBRE_BANDES_PIETON = 9

# =============================================================================
# ZONES D'ARRÊT AUX FEUX (par direction)
# =============================================================================
# Nord (descendant)
ZONE_ARRET_NORD_MIN = CENTRE_Y - 170
ZONE_ARRET_NORD_MAX = CENTRE_Y - 160

# Sud (montant)
ZONE_ARRET_SUD_MIN = CENTRE_Y + 140
ZONE_ARRET_SUD_MAX = CENTRE_Y + 170

# Est (vers l'ouest)
ZONE_ARRET_EST_MIN = CENTRE_X + 130
ZONE_ARRET_EST_MAX = CENTRE_X + 190

# Ouest (vers l'est)
ZONE_ARRET_OUEST_MIN = CENTRE_X - 180
ZONE_ARRET_OUEST_MAX = CENTRE_X - 120

# =============================================================================
# ZONES D'ATTENTE (pour comptage intelligent)
# =============================================================================
# Nord-Sud
ZONE_ATTENTE_NS_MIN = 120
ZONE_ATTENTE_NS_MAX = 180

# Est-Ouest
ZONE_ATTENTE_EO_MIN = 120
ZONE_ATTENTE_EO_MAX = 180

# Zones d'approche (distance de détection)
ZONE_APPROCHE_DISTANCE = 300

# =============================================================================
# POSITIONS DE SPAWN DES VOITURES
# =============================================================================
SPAWN_NORD_X = CENTRE_X - 60
SPAWN_NORD_Y = 20

SPAWN_SUD_X = CENTRE_X + 60
SPAWN_SUD_Y = HAUTEUR - 20

SPAWN_EST_X = LARGEUR - 620
SPAWN_EST_Y = CENTRE_Y - 60

SPAWN_OUEST_X = 20
SPAWN_OUEST_Y = CENTRE_Y + 60

# =============================================================================
# LIMITES DE SORTIE DES VOITURES
# =============================================================================
LIMITE_SORTIE_NORD = HAUTEUR + 50
LIMITE_SORTIE_SUD = -50
LIMITE_SORTIE_EST = -50
LIMITE_SORTIE_OUEST = LARGEUR - 600

# =============================================================================
# POSITIONS DES FEUX TRICOLORES
# =============================================================================
FEU_NORD_X = CENTRE_X - 150
FEU_NORD_Y = CENTRE_Y - 220

FEU_SUD_X = CENTRE_X + 150
FEU_SUD_Y = CENTRE_Y + 140

FEU_EST_X = CENTRE_X + 130
FEU_EST_Y = CENTRE_Y - 150

FEU_OUEST_X = CENTRE_X - 205
FEU_OUEST_Y = CENTRE_Y + 150

# =============================================================================
# POSITIONS DES FEUX PIÉTONS
# =============================================================================
FEU_PIETON_NO_X = CENTRE_X - 200
FEU_PIETON_NO_Y = CENTRE_Y - 190

FEU_PIETON_SE_X = CENTRE_X + 200
FEU_PIETON_SE_Y = CENTRE_Y + 200

FEU_PIETON_NE_X = CENTRE_X + 190
FEU_PIETON_NE_Y = CENTRE_Y - 190

FEU_PIETON_SO_X = CENTRE_X - 190
FEU_PIETON_SO_Y = CENTRE_Y + 190

# =============================================================================
# TAILLES DES FEUX
# =============================================================================
TAILLE_FEU_POTEAU_LARGEUR = 16
TAILLE_FEU_POTEAU_HAUTEUR = 100
TAILLE_FEU_BOITIER_LARGEUR = 56
TAILLE_FEU_BOITIER_HAUTEUR = 90
RAYON_LUMIERE_FEU = 16
BORDER_RADIUS_FEU = 8

# =============================================================================
# ANIMATION ACCIDENTS
# =============================================================================
CLIGNOTEMENT_ACCIDENT_RAPIDE = 20  # frames pour un cycle
CLIGNOTEMENT_ACCIDENT_LENT = 30    # frames pour triangle
RAYON_CERCLE_ACCIDENT = 50
RAYON_CERCLE_ACCIDENT_INTERNE = 35
TAILLE_X_ACCIDENT = 40
TAILLE_TRIANGLE_ACCIDENT = 50

# =============================================================================
# PHASES DE SIMULATION
# =============================================================================
PHASE_NS_VERT = "NS_VERT"
PHASE_NS_ORANGE = "NS_ORANGE"
PHASE_NS_PIETON = "NS_PIETON"
PHASE_EO_VERT = "EO_VERT"
PHASE_EO_ORANGE = "EO_ORANGE"
PHASE_EO_PIETON = "EO_PIETON"

# =============================================================================
# PIETONS - RENDU VISUEL
# =============================================================================
PIETON_TETE_RAYON = 8
PIETON_CORPS_LARGEUR = 6
PIETON_CORPS_HAUTEUR = 12
PIETON_JAMBE_LONGUEUR = 10
PIETON_COULEUR_TETE = (50, 50, 50)
PIETON_COULEUR_CORPS = (100, 100, 100)
PIETON_COULEUR_CONTOUR = (255, 255, 255)
NOMBRE_PIETONS_SIMULTANES = 4
DUREE_TRAVERSEE_PIETON = 7  # Durée standard pour calculer la progression
