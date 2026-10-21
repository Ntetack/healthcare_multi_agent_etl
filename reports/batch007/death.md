# Comparaison ligne à ligne — death

Clé naturelle : person + ['death_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 20 lignes
  Chez la référence : 18 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 120

## Volumes après restriction aux patients communs
  Chez nous : 20 lignes (0 exclues - patient non apparié)
  Chez la référence : 18 lignes (0 exclues - patient non apparié)

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 0
  Clés UNIQUEMENT chez nous : 20
  Clés UNIQUEMENT chez la référence : 18
    ex: [(42, datetime.date(1984, 5, 27)), (112, datetime.date(2007, 9, 29)), (28, datetime.date(2000, 1, 30))]
    ex: [(104, datetime.date(2008, 8, 23)), (42, datetime.date(1984, 5, 30)), (29, datetime.date(2003, 5, 24))]

Lignes appariées (même personne + même clé naturelle) : 0

## death_datetime : ignoré (toujours vide chez nous sur les lignes appariées)
## cause_concept_id : ignoré (toujours vide chez nous sur les lignes appariées)
## cause_source_value : ignoré (toujours vide chez nous sur les lignes appariées)