# Persoenliche Abgabe-Checkliste

Diese Checkliste ist zum aktiven Ueben vor der Abgabe gedacht. Jeder Punkt
sollte nicht nur ausgefuehrt, sondern auch kurz erklaert werden koennen.

## Installation und Start

- [ ] Repository frisch in ein neues Verzeichnis geklont.
- [ ] Virtuelle Umgebung erstellt und aktiviert.
- [ ] `python -m pip install -r requirements-dev.txt` ausgefuehrt.
- [ ] `.env.example` nach `.env` kopiert.
- [ ] Eigenen lokalen `DJANGO_SECRET_KEY` generiert und in `.env` eingetragen.
- [ ] `DJANGO_DEBUG=True` nur fuer lokale Entwicklung gesetzt.
- [ ] `DJANGO_ALLOWED_HOSTS` und `CORS_ALLOWED_ORIGINS` in `.env` erklaert.
- [ ] `python manage.py migrate` erfolgreich ausgefuehrt.
- [ ] `python manage.py createsuperuser` ausgefuehrt und Rolle erklaert.
- [ ] `python manage.py runserver` gestartet.
- [ ] API-Basisadresse `http://127.0.0.1:8000/api/` im Browser oder Client
      geprueft.

## Authentifizierung und Profile

- [ ] Registrierung selbst durchgefuehrt und `RegistrationSerializer` erklaert.
- [ ] Passwortbestaetigung mit falschem Wert getestet.
- [ ] Erklaert, warum `set_password()` statt direkter Passwortspeicherung
      verwendet wird.
- [ ] Login selbst durchgefuehrt und Token-Response erklaert.
- [ ] Header `Authorization: Token <token>` in einem API-Client gesetzt.
- [ ] Eigenes Profil abgerufen und `ProfileSerializer` erklaert.
- [ ] Eigenes Profil aktualisiert.
- [ ] Versuch dokumentiert, ein fremdes Profil zu bearbeiten.
- [ ] `IsProfileOwnerOrReadOnly` im Code gezeigt und erklaert.

## Offers

- [ ] Business-User erstellt oder registriert.
- [ ] Customer-User erstellt oder registriert.
- [ ] Offer mit Basic, Standard und Premium erstellt.
- [ ] `Offer` und `OfferDetail` im Datenmodell erklaert.
- [ ] Erklaert, warum ein Offer drei Detailpakete erwartet.
- [ ] Ungueltige Offer-Details getestet.
- [ ] Offer-Liste mit `creator_id` gefiltert.
- [ ] Offer-Suche mit `search` demonstriert.
- [ ] Sortierung nach `min_price` oder `updated_at` demonstriert.
- [ ] Versuch dokumentiert, als Customer ein Offer zu erstellen.
- [ ] Versuch dokumentiert, ein fremdes Offer zu bearbeiten.

## Orders

- [ ] Order als Customer aus einem `offer_detail_id` erstellt.
- [ ] `OrderSerializer.create()` im Code gezeigt.
- [ ] Snapshot-Felder `title`, `price`, `features`, `revisions` und
      `delivery_time_in_days` erklaert.
- [ ] OfferDetail nach Order-Erstellung geaendert und gezeigt, dass die Order
      unveraendert bleibt.
- [ ] Order-Liste als Customer abgerufen.
- [ ] Order-Liste als beteiligter Business-User abgerufen.
- [ ] Fremdzugriff auf eine Order demonstriert.
- [ ] Statusaenderung als Business-User demonstriert.
- [ ] Verbotene Statusaenderung als Customer demonstriert.
- [ ] `IsOrderParticipant` und `CanCreateOrUpdateOrder` erklaert.
- [ ] Order-Count-Endpunkte fuer offene und abgeschlossene Orders getestet.

## Reviews

- [ ] Review als Customer erstellt.
- [ ] `Review`-Model und Unique-Constraint erklaert.
- [ ] Zweites Review fuer denselben Business-User getestet.
- [ ] Review mit ungueltigem Rating getestet.
- [ ] Versuch dokumentiert, einen Customer statt Business-User zu bewerten.
- [ ] Versuch dokumentiert, als Business-User ein Review zu erstellen.
- [ ] Eigenes Review bearbeitet.
- [ ] Fremdes Review zu loeschen versucht.
- [ ] `IsCustomerOrReadOnly` und `IsReviewerOrReadOnly` erklaert.
- [ ] Durchschnittsbewertung im Zusammenhang mit Profilen oder Base-Info
      erklaert.

## Tests und Qualitaet

- [ ] Einen Auth-Test aus `auth_app/tests/test_auth_api.py` erklaert.
- [ ] Einen Permission-Test aus `auth_app/tests/test_profile_api.py` erklaert.
- [ ] Einen Offer-Test aus `offers_app/tests/test_offer_api.py` erklaert.
- [ ] Einen Order-Snapshot-Test aus `orders_app/tests/test_order_api.py`
      erklaert.
- [ ] Einen Review-Validierungstest aus `reviews_app/tests/test_review_api.py`
      erklaert.
- [ ] Security-Regressionstests in `auth_app/tests/test_security_regressions.py`
      erklaert.
- [ ] `python manage.py test --verbosity 2` lokal ausgefuehrt.
- [ ] `coverage run manage.py test` lokal ausgefuehrt.
- [ ] `coverage report --fail-under=95 -m` erklaert.
- [ ] Coverage-Bericht gelesen und erklaert, warum 100 Prozent nicht zwingend
      das Ziel sind.
- [ ] `black --check .`, `isort --check-only .` und `flake8 .` ausgefuehrt.

## GitHub Actions und Sicherheit

- [ ] Backend-Quality-Workflow in `.github/workflows/backend-quality.yml`
      erklaert.
- [ ] Secret-Scan-Workflow in `.github/workflows/secret-scan.yml` erklaert.
- [ ] Aktuellen PR-Status auf GitHub geprueft.
- [ ] Erklaert, warum `.env` nicht committed werden darf.
- [ ] Erklaert, warum `.env.example` nur Platzhalter enthaelt.
- [ ] Erklaert, warum `DJANGO_SECRET_KEY` pro Umgebung eindeutig sein muss.
- [ ] Erklaert, warum `DJANGO_DEBUG=False` ausserhalb lokaler Entwicklung
      wichtig ist.
- [ ] Erklaert, warum CORS Origins explizit gesetzt werden.
- [ ] Erklaert, warum ein Secret aus der Git-Historie rotiert werden muesste,
      falls es je produktiv verwendet wurde.

## Pruefungsgespraech

- [ ] `core/urls.py` gezeigt und Request-Routing erklaert.
- [ ] `core/settings.py` gezeigt und Environment-Konfiguration erklaert.
- [ ] `auth_app/models.py` gezeigt und Custom User Model erklaert.
- [ ] Einen Serializer mit `validate()` und `validate_<field>()` erklaert.
- [ ] Ein ViewSet und seine Permissions erklaert.
- [ ] Einen Queryset-Filter mit `select_related()` oder `prefetch_related()`
      erklaert.
- [ ] Eine Migration gezeigt und den Bezug zum Model erklaert.
- [ ] Eine fachliche Annahme aus `docs/requirements-matrix.md` erklaert.
- [ ] Eine wichtige Designentscheidung aus `docs/code-walkthrough.md` geuebt.
- [ ] Kurz erklaert, welche Grenzen das Projekt hat und was fuer Produktion
      zusaetzlich noetig waere.
