# Comparaison ligne à ligne — observation_period

Clé naturelle : person + ['observation_period_start_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 120 lignes
  Chez la référence : 120 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 120

## Volumes après restriction aux patients communs
  Chez nous : 120 lignes (0 exclues - patient non apparié)
  Chez la référence : 120 lignes (0 exclues - patient non apparié)

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 99
  Clés UNIQUEMENT chez nous : 21
  Clés UNIQUEMENT chez la référence : 21
    ex: [(7, datetime.date(1992, 3, 24)), (25, datetime.date(2016, 2, 8)), (56, datetime.date(1990, 5, 23))]
    ex: [(26, datetime.date(1966, 11, 4)), (97, datetime.date(2000, 10, 21)), (91, datetime.date(1981, 9, 5))]

Lignes appariées (même personne + même clé naturelle) : 99

## observation_period_end_date : 87/99 lignes concordent (87.9%)
    ex: nous=datetime.date(2026, 5, 30) vs référence=datetime.date(2026, 5, 7)
    ex: nous=datetime.date(2005, 7, 3) vs référence=datetime.date(2005, 7, 2)
    ex: nous=datetime.date(2026, 7, 29) vs référence=datetime.date(2026, 7, 15)

## Résumé : lignes ENTIÈREMENT identiques (tous les champs vérifiés à la fois) : 87/99 (87.9%)
