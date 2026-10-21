# Comparaison ligne à ligne — drug_exposure

Clé naturelle : person + ['drug_concept_id', 'drug_exposure_start_date', 'drug_exposure_end_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 7399 lignes
  Chez la référence : 7193 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 120

## Volumes après restriction aux patients communs
  Chez nous : 7399 lignes (0 exclues - patient non apparié)
  Chez la référence : 7193 lignes (0 exclues - patient non apparié)

⚠️  CLÉ NON UNIQUE : 31 doublon(s) chez nous, 31 chez la référence, sur (person + ['drug_concept_id', 'drug_exposure_start_date', 'drug_exposure_end_date']). Les comparaisons ci-dessous compareront des COMBINAISONS pour ces lignes, pas des lignes individuelles fiables - ajoutez un champ à la clé naturelle (ex: une date ou une heure) pour qu'elle identifie vraiment une seule ligne.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 7161
  Clés UNIQUEMENT chez nous : 207
  Clés UNIQUEMENT chez la référence : 1
    ex: [(79, 37003436, datetime.date(2021, 5, 31), datetime.date(2021, 5, 31)), (56, 37003436, datetime.date(2021, 4, 29), datetime.date(2021, 4, 29)), (40, 37003518, datetime.date(2021, 2, 22), datetime.date(2021, 2, 22))]
    ex: [(84, 19021481, datetime.date(1971, 6, 29), datetime.date(1972, 6, 23))]

Lignes appariées (même personne + même clé naturelle) : 7254

## drug_source_value : 7254/7254 lignes concordent (100.0%)

## drug_source_concept_id : 7254/7254 lignes concordent (100.0%)

## quantity : 0/5727 lignes concordent (0.0%)
    ex: nous=1.0 vs référence=0.0
    ex: nous=1.0 vs référence=0.0
    ex: nous=1.0 vs référence=0.0

## Résumé : lignes ENTIÈREMENT identiques (tous les champs vérifiés à la fois) : 1527/7254 (21.1%)
