# Comparaison ligne à ligne — death

Clé naturelle : person + ['death_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 9 lignes
  Chez la référence : 8 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 108

## Volumes après restriction aux patients communs
  Chez nous : 9 lignes (0 exclues - patient non apparié)
  Chez la référence : 8 lignes (0 exclues - patient non apparié)

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 1
  Clés UNIQUEMENT chez nous : 8
  Clés UNIQUEMENT chez la référence : 7
    ex: [(31, datetime.date(1991, 6, 6)), (14, datetime.date(2026, 5, 3)), (92, datetime.date(1961, 8, 23))]
    ex: [(14, datetime.date(2026, 5, 12)), (53, datetime.date(1998, 10, 17)), (58, datetime.date(2015, 9, 26))]

Lignes appariées (même personne + même clé naturelle) : 1

## death_datetime : 1/1 lignes concordent (100.0%)

## cause_concept_id : ignoré (toujours vide chez nous sur les lignes appariées)
## cause_source_value : ignoré (toujours vide chez nous sur les lignes appariées)
## Résumé : lignes ENTIÈREMENT identiques (tous les champs vérifiés à la fois) : 1/1 (100.0%)
