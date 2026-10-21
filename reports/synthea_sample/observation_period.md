# Comparaison ligne à ligne — observation_period

Clé naturelle : person + ['observation_period_start_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 108 lignes
  Chez la référence : 108 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 108

## Volumes après restriction aux patients communs
  Chez nous : 108 lignes (0 exclues - patient non apparié)
  Chez la référence : 108 lignes (0 exclues - patient non apparié)

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 107
  Clés UNIQUEMENT chez nous : 1
  Clés UNIQUEMENT chez la référence : 1
    ex: [(108, datetime.date(1955, 12, 11))]
    ex: [(108, datetime.date(1991, 5, 19))]

Lignes appariées (même personne + même clé naturelle) : 107

## observation_period_end_date : 91/107 lignes concordent (85.0%)
    ex: nous=datetime.date(2026, 5, 23) vs référence=datetime.date(2026, 5, 10)
    ex: nous=datetime.date(2026, 3, 7) vs référence=datetime.date(2026, 2, 18)
    ex: nous=datetime.date(2026, 6, 7) vs référence=datetime.date(2026, 6, 5)

## Résumé : lignes ENTIÈREMENT identiques (tous les champs vérifiés à la fois) : 91/107 (85.0%)
