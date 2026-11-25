| Point de contrôle | OK / KO | Ce que j'ai corrigé |
|---|---|---|
| Chaque table a une clé primaire | OK | Ajout d'une clé primaire à "avis" et "tags", et d'une clé primaire à "item_tags". |
| Les clés étrangères sont déclarées avec `REFERENCES` | OK | Déclaration des clés étrangères reliant "avis" à "reservations", et "item_tags" à "items" et "tags". |
| Les `ON DELETE` sont explicites et cohérents avec le métier | OK | Choix de CASCADE pour les avis et associations dépendants; "borrower_id" reste en NO ACTION |
| La règle « un seul avis par réservation » est garantie par une contrainte `UNIQUE` | OK | Ajout de UNIQUE (reservation_id) pour limiter chaque réservation à un avis. |
| La note est bornée par un `CHECK (note BETWEEN 1 AND 5)` | OK | Ajout du CHECK nommé "avis_note_valide" pour limiter les notes de 1 à 5. |
| La table de liaison item/tag a une clé primaire composite | OK | Définition de "item_tags_pkey" sur ("item_id", "tag_id") pour éviter les associations en double. |
| Le libellé de tag est `UNIQUE` | OK | Ajout de "tags_libelle_unique" et d'un CHECK imposant les minuscules. |
| Les contraintes sont nommées | OK | Attribution de noms explicites aux contraintes ajoutées, notamment aux clés étrangères et aux contraintes CHECK et EXCLUDE. |
| Des index existent sur les clés étrangères | OK | Ajout d'index sur "items.owner_id", "reservations.item_id", "reservations.borrower_id" et "item_tags.tag_id"; les clés primaires et l'unicité couvrent les autres références. |
| Le non-chevauchement est réellement garanti (contrainte) ou explicitement laissé à l'applicatif | OK | Ajout de "reservations_no_active_overlap", contrainte d'exclusion des réservations actives qui se chevauchent. |
| Aucun type flottant pour un montant, aucun `TIMESTAMP` sans fuseau | OK | Conservation de "NUMERIC" pour les montants et utilisation de "TIMESTAMPTZ" pour l'horodatage des avis. |