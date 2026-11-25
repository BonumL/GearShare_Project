-- Items disponible à moins de 10€/jour
SELECT id, titre, disponible, tarif_jour
FROM items 
WHERE (tarif_jour < 10) AND disponible
ORDER BY tarif_jour ASC;
/*
Result :
 id | titre          | disponible | tarif_jour
----+----------------+------------+------------
  2 | Perceuse       | true       |       5.00
  1 | Vélo de ville  | true       |       8.50
(2 rows)
*/

-- Items dont le titre contient "velo" insensible a la case
SELECT id, titre
FROM items 
WHERE (titre LIKE '%velo%');
/*
Result :
(0 rows : « Vélo » contient « é », qui est différent de « e ».)
*/

-- Items avec le display_name du propriétaire
SELECT items.id, items.titre, users.display_name AS proprietaire
FROM items 
LEFT JOIN users ON items.owner_id = users.id;
/*
Result :
 id | titre           | proprietaire
----+-----------------+-------------
  1 | Vélo de ville   | Alice
  2 | Perceuse        | Alice
  3 | Tente 2 places  | Bob
  4 | Appareil photo  | Bob
(4 rows ; ordre non garanti sans ORDER BY.)
*/

-- Tous les items, avec le nombre de réservations (0 compris)
SELECT items.titre, COUNT(reservations.id) AS nb_reservations
FROM items
LEFT JOIN reservations ON reservations.item_id = items.id
GROUP BY items.id, items.titre
ORDER BY nb_reservations DESC;
/*
Result :
 titre           | nb_reservations
-----------------+----------------
 Vélo de ville   | 1
 Tente 2 places  | 1
 Appareil photo  | 1
 Perceuse        | 0
(4 rows)
*/

-- Pour chaque utilisateur : son nom, son nombre d'items publiés, le tarif moyen de ses items. Uniquement ceux qui ont publié au moins un item.
SELECT users.display_name, COUNT(items.id) AS nb_items, AVG(tarif_jour)
FROM users
LEFT JOIN items ON users.id = items.owner_id
GROUP BY users.id, users.display_name
ORDER BY users.display_name ASC
HAVING COUNT(items.id) > 0;
/*
Result :
 display_name | nb_items | avg tarif_jour
--------------+----------+---------------
 Alice        |        2 |           6.75
 Bob          |        2 |          16.00
(2 rows)
*/

-- Reservations actives avec date_debut >= '2026-09-01'
SELECT reservations.id, reservations.statut, items.titre, users.display_name, reservations.date_debut
FROM reservations
LEFT JOIN items ON reservations.item_id = items.id
LEFT JOIN users ON reservations.borrower_id = users.id
WHERE reservations.date_debut >= DATE '2026-09-01' AND reservations.statut = 'active'
ORDER BY reservations.date_debut;
/*
Result :
 id | statut | titre          | display_name | date_debut
----+--------+----------------+--------------+------------
  2 | active | Tente 2 places | Alice        | 2026-09-10
  3 | active | Appareil photo | Chloé        | 2026-09-15
(2 rows)
*/

-- Les 2 items les plus chers, en sautant le premier
SELECT id, titre, tarif_jour
FROM items 
ORDER BY tarif_jour DESC
OFFSET 1 LIMIT 2;
/*
Result :
 id | titre          | disponible | tarif_jour
----+----------------+------------+------------
  3 | Tente 2 places | true       |      12.00
  1 | Vélo de ville  | true       |       8.50
(2 rows)
*/

-- Le chiffre d'affaires potentiel de chaque réservation active
SELECT reservations.id, items.titre, (reservations.date_fin - reservations.date_debut) AS nb_jours, items.tarif_jour AS Tarif, (items.tarif_jour * (reservations.date_fin - reservations.date_debut)) AS CA
FROM reservations 
LEFT JOIN items ON reservations.item_id = items.id
WHERE (reservations.statut = 'active')
ORDER BY CA DESC;
/*
Result :
 id | titre          | nb_jours | tarif |  ca
----+----------------+----------+-------+------
  3 | Appareil photo |        5 | 20.00 | 100.00
  2 | Tente 2 places |        2 | 12.00 |  24.00
(2 rows)
*/

