# Comparaison ligne à ligne — procedure_occurrence

Clé naturelle : person + ['procedure_concept_id', 'procedure_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 10272 lignes
  Chez la référence : 8560 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 108

## Volumes après restriction aux patients communs
  Chez nous : 10272 lignes (0 exclues - patient non apparié)
  Chez la référence : 8560 lignes (0 exclues - patient non apparié)

⚠️  CLÉ NON UNIQUE : 15 doublon(s) chez nous, 15 chez la référence, sur (person + ['procedure_concept_id', 'procedure_date']). Les comparaisons ci-dessous compareront des COMBINAISONS pour ces lignes, pas des lignes individuelles fiables - ajoutez un champ à la clé naturelle (ex: une date ou une heure) pour qu'elle identifie vraiment une seule ligne.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 8545
  Clés UNIQUEMENT chez nous : 1712
  Clés UNIQUEMENT chez la référence : 0
    ex: [(47, 4132649, datetime.date(1981, 8, 11)), (79, 4132649, datetime.date(2021, 11, 1)), (80, 4036803, datetime.date(2011, 3, 27))]

Lignes appariées (même personne + même clé naturelle) : 8590

## procedure_source_value : 8590/8590 lignes concordent (100.0%)

## procedure_source_concept_id : 8590/8590 lignes concordent (100.0%)

## quantity : ignoré (toujours vide chez nous sur les lignes appariées)
## Résumé : lignes ENTIÈREMENT identiques (tous les champs vérifiés à la fois) : 8590/8590 (100.0%)
