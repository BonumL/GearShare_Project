INSERT INTO users (email, password_hash, display_name)
VALUES
    ('alice@esiee.fr', 'fake-hash-alice', 'Alice'),
    ('bob@esiee.fr', 'fake-hash-bob', 'Bob'),
    ('chloe@esiee.fr', 'fake-hash-chloe', 'Chloé');

INSERT INTO items (owner_id, titre, description, tarif_jour)
VALUES
    (1, 'Vélo de ville', 'Cadre alu, panier avant', 8.50),
    (1, 'Perceuse', 'Avec jeu de mèches', 5.00),
    (2, 'Tente 2 places', NULL, 12.00),
    (2, 'Appareil photo', 'Reflex + objectif 50mm', 20.00);

INSERT INTO reservations (item_id, borrower_id, date_debut, date_fin, statut)
VALUES
    (1, 2, DATE '2026-09-01', DATE '2026-09-05', 'terminee'),
    (3, 1, DATE '2026-09-10', DATE '2026-09-12', 'active'),
    (4, 3, DATE '2026-09-15', DATE '2026-09-20', 'active');