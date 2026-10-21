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
    ex: [(60, 4085798, datetime.date(2021, 8, 10)), (86, 4024741, datetime.date(2024, 1, 14)), (15, 4088569, datetime.date(2022, 1, 21))]
    ex: [(89, 4224654, datetime.date(2001, 8, 16)), (25, 4138133, datetime.date(2023, 11, 3)), (17, 43530807, datetime.date(2005, 6, 18))]

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
