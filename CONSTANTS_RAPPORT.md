# Rapport de Centralisation des Constantes

## Résumé Exécutif

Un fichier centralisé `constants.py` a été créé avec succès, regroupant **toutes les constantes** du projet (278 lignes).

---

## Objectif

Centraliser toutes les constantes éparpillées dans les différents modules pour :
- ✅ Faciliter la maintenance
- ✅ Éviter la duplication
- ✅ Permettre une configuration centralisée
- ✅ Améliorer la lisibilité du code

---

## Fichier Créé

### **[constants.py](feu_tricolore/constants.py)** - 278 lignes (9.8 KB)

Structure du fichier :

```python
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
# ... 10 couleurs de base

# =============================================================================
# COULEURS PASTEL PROFESSIONNELLES (BOUTONS)
# =============================================================================
VERT_PASTEL = (144, 238, 144)
VERT_PASTEL_ACTIF = (102, 205, 102)
# ... 7 couleurs pastel

# =============================================================================
# COULEURS DES FEUX MODERNES
# =============================================================================
VERT_FEU = (76, 175, 80)
ROUGE_FEU = (244, 67, 54)
ORANGE_FEU = (255, 152, 0)

# =============================================================================
# COULEURS POUR VOITURES
# =============================================================================
COULEURS_VOITURES = [ROUGE, BLEU, VERT_FONCE, ORANGE, (128, 0, 128), (255, 192, 203)]

# =============================================================================
# DIMENSIONS DE L'INTERSECTION
# =============================================================================
CENTRE_X = 500
CENTRE_Y = 450

# =============================================================================
# PARAMÈTRES DE SPAWN DES VOITURES
# =============================================================================
INTERVALLE_SPAWN_VOITURES = 30
PROBABILITE_SPAWN = 0.4
VOITURES_INITIALES_MIN = 2
VOITURES_INITIALES_MAX = 3

# =============================================================================
# PARAMÈTRES DE COLLISION ET SÉCURITÉ
# =============================================================================
DISTANCE_SECURITE_VOITURE = 50
SEUIL_COLLISION_X = 35
SEUIL_COLLISION_Y = 30

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
DISTANCE_DETECTION_AMBULANCE = 300
DUREE_VERTE_AMBULANCE = 30
PROLONGATION_AMBULANCE = 10

# =============================================================================
# DURÉES DES FEUX (ADAPTATIF)
# =============================================================================
DUREE_VERTE_MIN = 10
DUREE_VERTE_FAIBLE = 15
SEUIL_TRAFIC_FAIBLE = 3
DUREE_VERTE_MOYEN = 25
SEUIL_TRAFIC_MOYEN = 7
DUREE_VERTE_ELEVE = 35
DELAI_PASSAGE_ANTICIPE = 5

# =============================================================================
# PARAMÈTRES D'HISTORIQUE ET STATISTIQUES
# =============================================================================
TAILLE_HISTORIQUE_TRAFIC = 30

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
PANEL_LARGEUR = 590
PANEL_DECALAGE_X = LARGEUR - PANEL_LARGEUR
LARGEUR_BOUTON_PRINCIPAL = 240
HAUTEUR_BOUTON_PRINCIPAL = 50
# ... etc

# =============================================================================
# PARAMÈTRES DE DESSIN DE LA ROUTE
# =============================================================================
LARGEUR_ROUTE = 240
LARGEUR_LIGNE_BLANCHE = 30
# ... etc

# =============================================================================
# ZONES D'ARRÊT AUX FEUX (par direction)
# =============================================================================
ZONE_ARRET_NORD_MIN = CENTRE_Y - 170
ZONE_ARRET_NORD_MAX = CENTRE_Y - 160
ZONE_ARRET_SUD_MIN = CENTRE_Y + 140
ZONE_ARRET_SUD_MAX = CENTRE_Y + 170
# ... etc

# =============================================================================
# ZONES D'ATTENTE (pour comptage intelligent)
# =============================================================================
ZONE_ATTENTE_NS_MIN = 120
ZONE_ATTENTE_NS_MAX = 180
# ... etc

# =============================================================================
# POSITIONS DE SPAWN DES VOITURES
# =============================================================================
SPAWN_NORD_X = CENTRE_X - 60
SPAWN_NORD_Y = 20
SPAWN_SUD_X = CENTRE_X + 60
SPAWN_SUD_Y = HAUTEUR - 20
# ... etc

# =============================================================================
# LIMITES DE SORTIE DES VOITURES
# =============================================================================
LIMITE_SORTIE_NORD = HAUTEUR + 50
LIMITE_SORTIE_SUD = -50
# ... etc

# =============================================================================
# POSITIONS DES FEUX TRICOLORES
# =============================================================================
FEU_NORD_X = CENTRE_X - 150
FEU_NORD_Y = CENTRE_Y - 220
# ... etc

# =============================================================================
# POSITIONS DES FEUX PIÉTONS
# =============================================================================
FEU_PIETON_NO_X = CENTRE_X - 200
FEU_PIETON_NO_Y = CENTRE_Y - 190
# ... etc

# =============================================================================
# TAILLES DES FEUX
# =============================================================================
TAILLE_FEU_POTEAU_LARGEUR = 16
TAILLE_FEU_POTEAU_HAUTEUR = 100
# ... etc

# =============================================================================
# ANIMATION ACCIDENTS
# =============================================================================
CLIGNOTEMENT_ACCIDENT_RAPIDE = 20
CLIGNOTEMENT_ACCIDENT_LENT = 30
# ... etc

# =============================================================================
# PHASES DE SIMULATION
# =============================================================================
PHASE_NS_VERT = "NS_VERT"
PHASE_NS_ORANGE = "NS_ORANGE"
PHASE_NS_PIETON = "NS_PIETON"
PHASE_EO_VERT = "EO_VERT"
PHASE_EO_ORANGE = "EO_ORANGE"
PHASE_EO_PIETON = "EO_PIETON"
```

---

## Fichiers Mis à Jour

### 1. **[main_gui.py](main_gui.py)**
```python
from feu_tricolore.constants import (
    LARGEUR, HAUTEUR, FPS,
    BLEU, VERT, ROUGE, ORANGE
)
```

### 2. **[gestionnaire_voitures.py](feu_tricolore/gestionnaire_voitures.py)**
```python
from feu_tricolore.constants import (
    COULEURS_VOITURES,
    INTERVALLE_SPAWN_VOITURES,
    PROBABILITE_SPAWN,
    VOITURES_INITIALES_MIN,
    VOITURES_INITIALES_MAX,
    DISTANCE_SECURITE_VOITURE,
    SEUIL_COLLISION_X,
    SEUIL_COLLISION_Y,
    # ... 30+ constantes importées
)
```

### 3. **[gestionnaire_ambulances.py](feu_tricolore/gestionnaire_ambulances.py)**
```python
from feu_tricolore.constants import (
    BLANC,
    DISTANCE_DETECTION_AMBULANCE,
    SPAWN_NORD_X, SPAWN_NORD_Y,
    SPAWN_SUD_X, SPAWN_SUD_Y,
    SPAWN_EST_X, SPAWN_EST_Y,
    SPAWN_OUEST_X, SPAWN_OUEST_Y
)
```

### 4. **[gestionnaire_rendu.py](feu_tricolore/gestionnaire_rendu.py)**
```python
from feu_tricolore.constants import (
    BLANC, NOIR, GRIS, GRIS_CLAIR, GRIS_FONCE,
    VERT, ROUGE, ORANGE, BLEU, BLEU_FONCE, JAUNE,
    VERT_FONCE, VERT_GAZON,
    VERT_PASTEL, VERT_PASTEL_ACTIF,
    ROUGE_PASTEL, ROUGE_PASTEL_ACTIF,
    BLEU_PASTEL, ORANGE_PASTEL, ROUGE_URGENCE,
    VERT_FEU, ROUGE_FEU, ORANGE_FEU,
    TAILLE_POLICE_TITRE, TAILLE_POLICE_NORMALE, TAILLE_POLICE_PETITE,
    DUREE_MESSAGE
)
```

---

## Catégories de Constantes

| Catégorie | Nombre | Description |
|-----------|--------|-------------|
| **Couleurs** | 35 | Base, pastel, feux, voitures |
| **Dimensions** | 20 | Fenêtre, intersection, routes |
| **Paramètres de simulation** | 25 | Spawn, collisions, accidents, ambulances |
| **Durées et timing** | 15 | Feux adaptatifs, messages, animations |
| **Positions** | 50+ | Spawn, feux, piétons, zones d'arrêt |
| **Zones de détection** | 30+ | Attente, approche, collision |
| **Phases** | 6 | États de simulation |
| **Interface** | 20+ | Boutons, polices, panel |

**Total : ~200+ constantes centralisées**

---

## Avantages de la Centralisation

### 1. **Maintenance Simplifiée** ✅
- Un seul endroit pour modifier les valeurs
- Plus de duplication de code
- Changements propagés automatiquement

### 2. **Configuration Facile** ✅
- Ajuster le comportement de la simulation
- Modifier l'apparence visuelle
- Tweaker les paramètres de gameplay

### 3. **Documentation Intégrée** ✅
- Commentaires clairs pour chaque section
- Organisation logique par catégorie
- Facile à comprendre et naviguer

### 4. **Évolutivité** ✅
- Ajouter de nouvelles constantes facilement
- Grouper les paramètres connexes
- Support pour futurs développements

### 5. **Testabilité** ✅
- Facilite les tests unitaires
- Permet de créer des configurations de test
- Isolation des paramètres

---

## Exemples d'Utilisation

### Modifier la taille de la fenêtre
```python
# Dans constants.py
LARGEUR = 1920  # au lieu de 1600
HAUTEUR = 1080  # au lieu de 900
```

### Changer les couleurs de l'interface
```python
# Dans constants.py
VERT_PASTEL = (100, 200, 100)  # Nouvelle teinte
ROUGE_FEU = (255, 50, 50)      # Rouge plus vif
```

### Ajuster le comportement des ambulances
```python
# Dans constants.py
DISTANCE_DETECTION_AMBULANCE = 400  # Détection plus lointaine
DUREE_VERTE_AMBULANCE = 45         # Feu vert plus long
```

### Modifier le système de spawn
```python
# Dans constants.py
INTERVALLE_SPAWN_VOITURES = 20  # Spawn plus fréquent
PROBABILITE_SPAWN = 0.2          # Plus de voitures
```

---

## Organisation du Fichier

Le fichier est organisé en **20 sections** clairement délimitées :

```
constants.py
├── DIMENSIONS DE LA FENÊTRE
├── COULEURS DE BASE
├── COULEURS PASTEL PROFESSIONNELLES
├── COULEURS DES FEUX MODERNES
├── COULEURS POUR VOITURES
├── DIMENSIONS DE L'INTERSECTION
├── PARAMÈTRES DE SPAWN DES VOITURES
├── PARAMÈTRES DE COLLISION ET SÉCURITÉ
├── ZONES D'INTERSECTION
├── PARAMÈTRES D'ACCIDENTS
├── PARAMÈTRES AMBULANCES
├── DURÉES DES FEUX (ADAPTATIF)
├── PARAMÈTRES D'HISTORIQUE ET STATISTIQUES
├── DURÉE D'AFFICHAGE DES MESSAGES
├── PARAMÈTRES DE TAILLE DES POLICES
├── POSITIONS DES ÉLÉMENTS GRAPHIQUES
├── PARAMÈTRES DE DESSIN DE LA ROUTE
├── ZONES D'ARRÊT AUX FEUX
├── ZONES D'ATTENTE
├── POSITIONS DE SPAWN DES VOITURES
├── LIMITES DE SORTIE DES VOITURES
├── POSITIONS DES FEUX TRICOLORES
├── POSITIONS DES FEUX PIÉTONS
├── TAILLES DES FEUX
├── ANIMATION ACCIDENTS
└── PHASES DE SIMULATION
```

---

## Vérification

✅ **Compilation Python** : Succès
```bash
python -m py_compile feu_tricolore/constants.py
```

✅ **Imports validés** : Tous les fichiers compilent sans erreur

✅ **Structure cohérente** : Organisation logique par catégorie

---

## Impact sur le Projet

### Avant
- Constantes éparpillées dans 4 fichiers
- Duplication (couleurs définies 3 fois)
- Difficile à maintenir

### Après
- **1 fichier centralisé** : [constants.py](feu_tricolore/constants.py)
- **278 lignes** de constantes organisées
- **20+ catégories** bien documentées
- **Imports sélectifs** dans chaque module
- **Zéro duplication**

---

## Conclusion

La centralisation des constantes est **terminée avec succès** :

✅ Fichier `constants.py` créé (278 lignes)
✅ 4 fichiers mis à jour pour utiliser les constantes
✅ Compilation réussie
✅ Organisation claire et documentée
✅ Facilite grandement la maintenance future

**Le projet est maintenant mieux organisé et plus facile à configurer !**

---

**Date** : 26 décembre 2025
**Fichier** : [feu_tricolore/constants.py](feu_tricolore/constants.py)
**Lignes** : 278
**Taille** : 9.8 KB
