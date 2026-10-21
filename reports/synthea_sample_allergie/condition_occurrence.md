# Comparaison ligne à ligne — condition_occurrence

Clé naturelle : person + ['condition_concept_id', 'condition_start_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 1728 lignes
  Chez la référence : 1717 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 108

## Volumes après restriction aux patients communs
  Chez nous : 1728 lignes (0 exclues - patient non apparié)
  Chez la référence : 1717 lignes (0 exclues - patient non apparié)

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 1717
  Clés UNIQUEMENT chez nous : 11
  Clés UNIQUEMENT chez la référence : 0
    ex: [(59, 0, datetime.date(2023, 12, 7)), (53, 0, datetime.date(1994, 9, 16)), (74, 0, datetime.date(1996, 12, 8))]

Lignes appariées (même personne + même clé naturelle) : 1717

## condition_source_value : 1717/1717 lignes concordent (100.0%)

## condition_source_concept_id : 1717/1717 lignes concordent (100.0%)

## condition_end_date : 1218/1218 lignes concordent (100.0%)

## Résumé : lignes ENTIÈREMENT identiques (tous les champs vérifiés à la fois) : 1717/1717 (100.0%)
