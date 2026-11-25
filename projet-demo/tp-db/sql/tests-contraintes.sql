BEGIN;

SAVEPOINT test_note;
INSERT INTO avis (reservation_id, note, commentaire)
VALUES (1, 6, 'Note volontairement invalide');
ROLLBACK TO SAVEPOINT test_note;

INSERT INTO avis (reservation_id, note, commentaire)
VALUES (1, 5, 'Avis de préparation au test');
SAVEPOINT test_avis_duplique;
INSERT INTO avis (reservation_id, note, commentaire)
VALUES (1, 4, 'Deuxième avis pour la même réservation');
ROLLBACK TO SAVEPOINT test_avis_duplique;

INSERT INTO tags (libelle)
VALUES ('tp-test-unique');
SAVEPOINT test_tag_duplique;
INSERT INTO tags (libelle)
VALUES ('tp-test-unique');
ROLLBACK TO SAVEPOINT test_tag_duplique;

SAVEPOINT test_avis_sans_reservation;
INSERT INTO avis (reservation_id, note, commentaire)
VALUES (2147483647, 3, 'Réservation inexistante');
ROLLBACK TO SAVEPOINT test_avis_sans_reservation;

SAVEPOINT test_reservations_chevauchees;
INSERT INTO reservations (item_id, borrower_id, date_debut, date_fin, statut)
VALUES (4, 1, DATE '2026-09-16', DATE '2026-09-18', 'active');
ROLLBACK TO SAVEPOINT test_reservations_chevauchees;

ROLLBACK;
