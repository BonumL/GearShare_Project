```
                    QUERY PLAN
------------------------------------------------------------
 ``Seq Scan on items  (cost=0.00..4370.05 rows=1 width=74) (actual time=26.360..46.809 rows=1 loops=1)
   Filter: ((titre)::text = 'Item de test 123456'::text)
   Rows Removed by Filter: 200003
 Planning Time: 0.568 ms
 Execution Time: 46.906 ms
(5 rows)
```

Sans index pour se repérer, PostgreSQL doit lancer un scan séquentiel. La recherche prend 46,906 ms pour chercher dans les 200 004 lignes et en filtrer 200 003.

---
```
                    QUERY PLAN
------------------------------------------------------------
 Index Scan using idx_items_titre on items  (cost=0.42..8.44 rows=1 width=65) (actual time=0.151..0.153 rows=1 loops=1)
   Index Cond: ((titre)::text = 'Item de test 123456'::text)
 Planning Time: 0.310 ms
 Execution Time: 0.175 ms
```
Une fois l'index créé, le scan devient un Index Scan. Le temps d'execution reduit d'environ 270 fois. L'index accélère énormement la recherche.

---
```
                    QUERY PLAN
------------------------------------------------------------
 Seq Scan on items  (cost=0.00..4370.05 rows=20 width=65) (actual time=20.685..38.212 rows=1 loops=1)
   Filter: ((titre)::text ~~ '%123456'::text)
   Rows Removed by Filter: 200003
 Planning Time: 0.992 ms
 Execution Time: 38.245 ms
(5 rows)
```
Malgré l'index sur le titre, la recherche passe toujours sur les 200 004 lignes. Le temps d'execution reste élevé avec 38,245 ms.

---
```
                     QUERY PLAN
------------------------------------------------------------
 Seq Scan on items  (cost=0.00..3870.04 rows=200004 width=74) (actual time=0.017..33.176 rows=200004 loops=1)
   Filter: disponible
 Planning Time: 0.634 ms
 Execution Time: 42.325 ms
(4 rows)
```
Après l'ajout du filtre sur "disponible = TRUE" après l'indexation de "disponible", le nombre de ligne ne reduit pas. Il reste toujours 200 004 lignes à vérifier. La recherche reste donc séquentiel et le temps de recherche élevé avec 42.325 ms.

```
                     QUERY PLAN
------------------------------------------------------------
 Index Scan using idx_items_disponible on items  (cost=0.29..4.31 rows=1 width=74) (actual time=0.107..0.108 rows=0 loops=1)
   Index Cond: (disponible = false)
 Planning Time: 0.109 ms
 Execution Time: 0.141 ms
(4 rows)
```
La recherche avec un filtre "disponible == FALSE", donne un resultat très différent puisqu'aucune ligne ne reste dans le tableau. Le résultat est donné presque instantanément à 0.141 ms.

---

```
                     QUERY PLAN
------------------------------------------------------------
 Seq Scan on items  (cost=0.00..4370.05 rows=20 width=65) (actual time=18.447..28.692 rows=1 loops=1)
   Filter: ((titre)::text ~~ 'Item de test 123456%'::text)
   Rows Removed by Filter: 200003
 Planning Time: 0.144 ms
 Execution Time: 28.712 ms
(5 rows)
```

Le motif commence par un texte fixe il est donc plus simple pour le modèle de se retrouver. Le résultat reste de l'ordre de la recherche '%123456'.
