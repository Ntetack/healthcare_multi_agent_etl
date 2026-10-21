# Comparaison ligne à ligne — drug_exposure

Clé naturelle : person + ['drug_concept_id', 'drug_exposure_start_date', 'drug_exposure_end_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 5446 lignes
  Chez la référence : 5207 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 108

## Volumes après restriction aux patients communs
  Chez nous : 5446 lignes (0 exclues - patient non apparié)
  Chez la référence : 5207 lignes (0 exclues - patient non apparié)

⚠️  CLÉ NON UNIQUE : 32 doublon(s) chez nous, 32 chez la référence, sur (person + ['drug_concept_id', 'drug_exposure_start_date', 'drug_exposure_end_date']). Les comparaisons ci-dessous compareront des COMBINAISONS pour ces lignes, pas des lignes individuelles fiables - ajoutez un champ à la clé naturelle (ex: une date ou une heure) pour qu'elle identifie vraiment une seule ligne.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 5174
  Clés UNIQUEMENT chez nous : 240
  Clés UNIQUEMENT chez la référence : 1
    ex: [(89, 40213291, datetime.date(2020, 3, 25), datetime.date(2020, 3, 25)), (25, 40213304, datetime.date(2023, 5, 31), datetime.date(2023, 5, 31)), (11, 40213291, datetime.date(2019, 3, 24), datetime.date(2019, 3, 24))]
    ex: [(31, 19021481, datetime.date(1982, 10, 1), datetime.date(1983, 9, 26))]

Lignes appariées (même personne + même clé naturelle) : 5270

## drug_source_value : 5270/5270 lignes concordent (100.0%)

## drug_source_concept_id : 5270/5270 lignes concordent (100.0%)

## quantity : ignoré (toujours vide chez nous sur les lignes appariées)
## Résumé : lignes ENTIÈREMENT identiques (tous les champs vérifiés à la fois) : 5270/5270 (100.0%)
