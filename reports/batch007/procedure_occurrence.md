# Comparaison ligne à ligne — procedure_occurrence

Clé naturelle : person + ['procedure_concept_id', 'procedure_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 13170 lignes
  Chez la référence : 11192 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 120

## Volumes après restriction aux patients communs
  Chez nous : 13170 lignes (0 exclues - patient non apparié)
  Chez la référence : 11192 lignes (0 exclues - patient non apparié)

⚠️  CLÉ NON UNIQUE : 21 doublon(s) chez nous, 21 chez la référence, sur (person + ['procedure_concept_id', 'procedure_date']). Les comparaisons ci-dessous compareront des COMBINAISONS pour ces lignes, pas des lignes individuelles fiables - ajoutez un champ à la clé naturelle (ex: une date ou une heure) pour qu'elle identifie vraiment une seule ligne.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 11171
  Clés UNIQUEMENT chez nous : 1978
  Clés UNIQUEMENT chez la référence : 0
    ex: [(100, 4132649, datetime.date(2022, 5, 20)), (80, 0, datetime.date(2019, 6, 18)), (29, 4036803, datetime.date(1997, 10, 11))]

Lignes appariées (même personne + même clé naturelle) : 11234

## procedure_source_value : 11234/11234 lignes concordent (100.0%)

## procedure_source_concept_id : 11234/11234 lignes concordent (100.0%)

## quantity : ignoré (toujours vide chez nous sur les lignes appariées)
## Résumé : lignes ENTIÈREMENT identiques (tous les champs vérifiés à la fois) : 11234/11234 (100.0%)
