# Comparaison ligne à ligne — measurement

Clé naturelle : person + ['measurement_concept_id', 'measurement_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 46728 lignes
  Chez la référence : 46612 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 108

## Volumes après restriction aux patients communs
  Chez nous : 46728 lignes (0 exclues - patient non apparié)
  Chez la référence : 46612 lignes (0 exclues - patient non apparié)

⚠️  CLÉ NON UNIQUE : 1693 doublon(s) chez nous, 1687 chez la référence, sur (person + ['measurement_concept_id', 'measurement_date']). Les comparaisons ci-dessous compareront des COMBINAISONS pour ces lignes, pas des lignes individuelles fiables - ajoutez un champ à la clé naturelle (ex: une date ou une heure) pour qu'elle identifie vraiment une seule ligne.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 44925
  Clés UNIQUEMENT chez nous : 110
  Clés UNIQUEMENT chez la référence : 0
    ex: [(39, 3033727, datetime.date(2023, 5, 26)), (106, 3033727, datetime.date(2025, 6, 11)), (106, 3033727, datetime.date(2024, 5, 22))]

Lignes appariées (même personne + même clé naturelle) : 50010

## value_as_number : 36657/38084 lignes concordent (96.3%)
    ex: nous=3.9 vs référence=5.7
    ex: nous=5.1 vs référence=4.9
    ex: nous=11.5 vs référence=14.5

## unit_concept_id : 45672/50010 lignes concordent (91.3%)
    ex: nous=44777566 vs référence=0
    ex: nous=44777566 vs référence=0
    ex: nous=44777566 vs référence=0

## measurement_source_value : 50010/50010 lignes concordent (100.0%)

## Résumé : lignes ENTIÈREMENT identiques (tous les champs vérifiés à la fois) : 44931/50010 (89.8%)
