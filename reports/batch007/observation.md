# Comparaison ligne à ligne — observation

Clé naturelle : person + ['observation_concept_id', 'observation_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 39973 lignes
  Chez la référence : 29927 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 120

## Volumes après restriction aux patients communs
  Chez nous : 39973 lignes (0 exclues - patient non apparié)
  Chez la référence : 29927 lignes (0 exclues - patient non apparié)

⚠️  CLÉ NON UNIQUE : 261 doublon(s) chez nous, 25 chez la référence, sur (person + ['observation_concept_id', 'observation_date']). Les comparaisons ci-dessous compareront des COMBINAISONS pour ces lignes, pas des lignes individuelles fiables - ajoutez un champ à la clé naturelle (ex: une date ou une heure) pour qu'elle identifie vraiment une seule ligne.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 29788
  Clés UNIQUEMENT chez nous : 9924
  Clés UNIQUEMENT chez la référence : 114
    ex: [(95, 4304200, datetime.date(2020, 5, 13)), (117, 4256369, datetime.date(2021, 11, 18)), (77, 4085798, datetime.date(2019, 3, 11))]
    ex: [(89, 4125382, datetime.date(2010, 10, 1)), (6, 42539493, datetime.date(1968, 5, 2)), (60, 4290627, datetime.date(1962, 9, 25))]

Lignes appariées (même personne + même clé naturelle) : 29963

## value_as_number : 0/5068 lignes concordent (0.0%)
    ex: nous=1.0 vs référence=None
    ex: nous=1.0 vs référence=None
    ex: nous=0.0 vs référence=None

## value_as_string : 0/29963 lignes concordent (0.0%)
    ex: nous='Educated to high school level (finding)' vs référence=None
    ex: nous='Received higher education (finding)' vs référence=None
    ex: nous='Full-time employment (finding)' vs référence=None

## observation_source_value : 29963/29963 lignes concordent (100.0%)

## Résumé : lignes ENTIÈREMENT identiques (tous les champs vérifiés à la fois) : 0/29963 (0.0%)
