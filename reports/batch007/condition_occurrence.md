# Comparaison ligne à ligne — condition_occurrence

Clé naturelle : person + ['condition_concept_id', 'condition_start_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 2050 lignes
  Chez la référence : 2030 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 120

## Volumes après restriction aux patients communs
  Chez nous : 2050 lignes (0 exclues - patient non apparié)
  Chez la référence : 2030 lignes (0 exclues - patient non apparié)

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 2030
  Clés UNIQUEMENT chez nous : 20
  Clés UNIQUEMENT chez la référence : 0
    ex: [(86, 0, datetime.date(2022, 1, 24)), (75, 0, datetime.date(2022, 2, 13)), (43, 0, datetime.date(1992, 3, 31))]

Lignes appariées (même personne + même clé naturelle) : 2030

## condition_source_value : 2030/2030 lignes concordent (100.0%)

## condition_source_concept_id : 2030/2030 lignes concordent (100.0%)

## condition_end_date : 1398/1398 lignes concordent (100.0%)

## Résumé : lignes ENTIÈREMENT identiques (tous les champs vérifiés à la fois) : 2030/2030 (100.0%)
