# Comparaison ligne à ligne — observation

Clé naturelle : person + ['observation_concept_id', 'observation_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 31885 lignes
  Chez la référence : 24882 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 108

## Volumes après restriction aux patients communs
  Chez nous : 31885 lignes (0 exclues - patient non apparié)
  Chez la référence : 24882 lignes (0 exclues - patient non apparié)

⚠️  CLÉ NON UNIQUE : 103 doublon(s) chez nous, 14 chez la référence, sur (person + ['observation_concept_id', 'observation_date']). Les comparaisons ci-dessous compareront des COMBINAISONS pour ces lignes, pas des lignes individuelles fiables - ajoutez un champ à la clé naturelle (ex: une date ou une heure) pour qu'elle identifie vraiment une seule ligne.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 24775
  Clés UNIQUEMENT chez nous : 7007
  Clés UNIQUEMENT chez la référence : 93
    ex: [(73, 4304200, datetime.date(2022, 2, 22)), (28, 4301458, datetime.date(2025, 12, 8)), (54, 4054945, datetime.date(2018, 3, 4))]
    ex: [(57, 36713251, datetime.date(2001, 1, 3)), (90, 43530807, datetime.date(1990, 4, 16)), (52, 4122068, datetime.date(2005, 11, 11))]

Lignes appariées (même personne + même clé naturelle) : 24857

## value_as_number : 0/4276 lignes concordent (0.0%)
    ex: nous=42283.0 vs référence=None
    ex: nous=6.0 vs référence=None
    ex: nous=5.0 vs référence=None

## value_as_string : 0/24857 lignes concordent (0.0%)
    ex: nous='Received higher education (finding)' vs référence=None
    ex: nous='Full-time employment (finding)' vs référence=None
    ex: nous='Medication review due (situation)' vs référence=None

## observation_source_value : 24857/24857 lignes concordent (100.0%)

## Résumé : lignes ENTIÈREMENT identiques (tous les champs vérifiés à la fois) : 0/24857 (0.0%)
