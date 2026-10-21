# Comparaison ligne à ligne — visit_occurrence

Clé naturelle : person + ['visit_concept_id', 'visit_start_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 4089 lignes
  Chez la référence : 0 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 108

## Volumes après restriction aux patients communs
  Chez nous : 4089 lignes (0 exclues - patient non apparié)
  Chez la référence : 0 lignes (0 exclues - patient non apparié)

⚠️  CLÉ NON UNIQUE : 107 doublon(s) chez nous, 0 chez la référence, sur (person + ['visit_concept_id', 'visit_start_date']). Les comparaisons ci-dessous compareront des COMBINAISONS pour ces lignes, pas des lignes individuelles fiables - ajoutez un champ à la clé naturelle (ex: une date ou une heure) pour qu'elle identifie vraiment une seule ligne.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 0
  Clés UNIQUEMENT chez nous : 3982
  Clés UNIQUEMENT chez la référence : 0
    ex: [(86, 9202, datetime.date(2016, 1, 31)), (95, 581479, datetime.date(2021, 9, 16)), (95, 581479, datetime.date(2021, 9, 7))]

Lignes appariées (même personne + même clé naturelle) : 0

## visit_end_date : ignoré (toujours vide chez nous sur les lignes appariées)
## visit_source_value : ignoré (toujours vide chez nous sur les lignes appariées)
## visit_source_concept_id : ignoré (toujours vide chez nous sur les lignes appariées)