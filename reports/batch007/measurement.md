# Comparaison ligne à ligne — measurement

Clé naturelle : person + ['measurement_concept_id', 'measurement_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 64585 lignes
  Chez la référence : 64306 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 120

## Volumes après restriction aux patients communs
  Chez nous : 64585 lignes (0 exclues - patient non apparié)
  Chez la référence : 64306 lignes (0 exclues - patient non apparié)

⚠️  CLÉ NON UNIQUE : 1309 doublon(s) chez nous, 1309 chez la référence, sur (person + ['measurement_concept_id', 'measurement_date']). Les comparaisons ci-dessous compareront des COMBINAISONS pour ces lignes, pas des lignes individuelles fiables - ajoutez un champ à la clé naturelle (ex: une date ou une heure) pour qu'elle identifie vraiment une seule ligne.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 62997
  Clés UNIQUEMENT chez nous : 279
  Clés UNIQUEMENT chez la référence : 0
    ex: [(116, 3033727, datetime.date(2023, 8, 4)), (119, 3032240, datetime.date(2019, 3, 17)), (116, 3032240, datetime.date(2019, 10, 8))]

Lignes appariées (même personne + même clé naturelle) : 66928

## value_as_number : 51169/51917 lignes concordent (98.6%)
    ex: nous=222.1 vs référence=142.1
    ex: nous=221.0 vs référence=126.0
    ex: nous=169.5 vs référence=59.8

## unit_concept_id : 60163/66928 lignes concordent (89.9%)
    ex: nous=44777566 vs référence=0
    ex: nous=44777566 vs référence=0
    ex: nous=44777566 vs référence=0

## measurement_source_value : 66928/66928 lignes concordent (100.0%)

## Résumé : lignes ENTIÈREMENT identiques (tous les champs vérifiés à la fois) : 59994/66928 (89.6%)
