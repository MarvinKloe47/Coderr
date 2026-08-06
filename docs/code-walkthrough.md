# Coderr Backend Code-Walkthrough

Diese Datei hilft dabei, das Backend vor der Abgabe aktiv zu verstehen und im
Pruefungsgespraech zu erklaeren. Sie beschreibt den tatsaechlichen Code im
Repository, nicht ein allgemeines Django-Beispiel.

## Projektuebersicht

Coderr ist ein Django-REST-Framework-Backend fuer einen Service-Marktplatz.
Business-Nutzer erstellen Angebote, Customer-Nutzer bestellen konkrete
Angebotspakete und koennen Business-Nutzer bewerten.

Die Apps sind bewusst fachlich getrennt:

- `auth_app`: Custom User Model, Registrierung, Login, Profile.
- `offers_app`: Angebote und Angebotsdetails.
- `orders_app`: Bestellungen aus einem Angebotsdetail.
- `reviews_app`: Bewertungen fuer Business-Nutzer.
- `core`: Settings, Haupt-URLs und der Base-Info-Endpunkt.

Die wichtigsten Abhaengigkeiten:

- `orders_app` verweist auf `auth_app.User` und `offers_app.OfferDetail`.
- `reviews_app` verweist auf `auth_app.User`.
- `offers_app.Offer` gehoert einem Business-User.
- `core.urls` bindet die URL-Dateien der Apps ein.

Request-Fluss:

1. Eine Anfrage kommt bei `core/urls.py` an.
2. Die passende App-URL leitet zur View oder zum ViewSet weiter.
3. DRF prueft Authentication und Permissions.
4. Die View waehlt Queryset und Serializer.
5. Der Serializer validiert Eingaben oder formatiert Ausgaben.
6. Models lesen oder speichern Daten in SQLite.
7. DRF erzeugt die HTTP-Response.

## Authentifizierung

Das Projekt nutzt ein Custom User Model in `auth_app/models.py`. Es erweitert
`AbstractUser` um Profilfelder und das Rollenfeld `type`.

Die zwei Rollen sind:

- `customer`: kann Orders erstellen und Reviews schreiben.
- `business`: kann Offers erstellen und Order-Status aktualisieren.

`UserManager.create_user()` normalisiert den Usernamen und ruft
`set_password()` auf. Dadurch wird nie ein Klartextpasswort gespeichert.
`create_superuser()` setzt Superuser automatisch auf die Business-Rolle und
prueft die Admin-Flags.

Registrierung:

- URL: `POST /api/registration/`
- View: `RegistrationView`
- Serializer: `RegistrationSerializer`
- Pflichtfelder: `username`, `email`, `password`, `repeated_password`, `type`
- Ergebnis: Token, User-ID und Username.

Login:

- URL: `POST /api/login/`
- View: `LoginView`
- Serializer: `LoginSerializer`
- Pruefung ueber `authenticate()`.
- Nur erfolgreiche Logins erzeugen oder liefern einen DRF Token.

Geschuetzte Endpoints verwenden DRF Token Authentication. Der Client sendet:

```http
Authorization: Token <token>
```

## Profile

Profile sind kein eigenes Model. Die Profilfelder liegen direkt auf dem Custom
User Model. Dadurch ist `User` gleichzeitig Login-Identitaet und Profilobjekt.

`ProfileSerializer` gibt nur explizit erlaubte Felder aus. Nicht enthalten sind
Passwort-Hash, Staff-Flags oder Superuser-Status.

Wichtige Felder:

- `user`: read-only ID des Users.
- `username`, `type`, `created_at`: read-only.
- `file`, `location`, `tel`, `description`, `working_hours`: Profilfelder.

`ProfileViewSet` erlaubt Detailansicht und Update. Die Permission
`IsProfileOwnerOrReadOnly` erlaubt Lesen, aber Schreibzugriff nur auf das eigene
Profil. Customer-Profile ignorieren beim Update Business-spezifische Felder.

Listen-Endpunkte:

- `/api/profiles/business/`
- `/api/profiles/customer/`

## Offers

`Offer` ist das Hauptangebot eines Business-Nutzers. `OfferDetail` beschreibt
die konkreten Pakete:

- `basic`
- `standard`
- `premium`

Ein Offer muss alle drei Detailtypen enthalten. Das prueft
`OfferSerializer.validate_details()`. Jedes Detail hat Titel, Revisionen,
Lieferzeit, Preis, Features und den Pakettyp.

Erstellung:

1. Ein Business-User sendet ein Offer mit drei verschachtelten Details.
2. `OfferSerializer.create()` erstellt das Offer fuer `request.user`.
3. `save_details()` legt die drei `OfferDetail`-Datensaetze an.

Filterung, Suche und Sortierung:

- `creator_id`: filtert Offers nach Business-User.
- `max_delivery_time`: filtert anhand der kuerzesten Detail-Lieferzeit.
- `search`: sucht in Titel und Beschreibung.
- `ordering`: erlaubt `updated_at`, `min_price`, `min_delivery_time`.

`OfferViewSet.get_queryset()` nutzt `select_related()`, `prefetch_related()` und
`annotate()`, damit User, Details und Minimum-Werte effizient geladen werden.

Berechtigungen:

- Nur authentifizierte User duerfen Offers lesen.
- Nur Business-User duerfen Offers erstellen.
- Nur der Offer-Owner darf Offers aendern oder loeschen.

## Orders

Eine Order entsteht aus genau einem `OfferDetail`. Der Customer sendet beim
Erstellen `offer_detail_id`.

Snapshot-Prinzip:

Beim Erstellen kopiert `OrderSerializer.create()` Titel, Revisionen,
Lieferzeit, Preis und Features aus dem OfferDetail in die Order. Diese Kopien
bleiben erhalten, wenn das Offer spaeter geaendert wird. Das ist wichtig, weil
eine Bestellung den Zustand zum Kaufzeitpunkt dokumentiert.

Zugriff:

- Customer sieht eigene Orders.
- Business sieht Orders, die zu seinen Offers gehoeren.
- Unbeteiligte User bekommen keinen Zugriff.

Status:

- Standardstatus ist `in_progress`.
- Nur der beteiligte Business-User darf den Status aendern.
- Der Status muss in `Order.Status.values` enthalten sein.

Statistik-Endpunkte:

- `/api/order-count/<business_user_id>/`: offene Orders.
- `/api/completed-order-count/<business_user_id>/`: abgeschlossene Orders.

## Reviews

Reviews verbinden einen Reviewer mit einem Business-User. Das Model hat eine
Unique-Constraint auf `reviewer` und `business_user`, damit ein Customer einen
Business-User nur einmal bewertet.

Validierungen im `ReviewSerializer`:

- Ziel muss ein Business-User sein.
- Bewertung muss zwischen 1 und 5 liegen.
- Doppelte Reviews werden abgelehnt.
- Selbstbewertungen werden defensiv verhindert.

Berechtigungen:

- Nur Customer duerfen Reviews erstellen.
- Lesen ist fuer authentifizierte User erlaubt.
- Nur der Reviewer darf sein Review aendern oder loeschen.

Durchschnittsbewertungen werden ueber Querysets und Aggregationen fuer Profile
und Base-Info genutzt.

## Sicherheit

Wichtige Settings liegen in `core/settings.py`:

- `DJANGO_SECRET_KEY` ist fuer normale Starts verpflichtend.
- Tests verwenden nur einen klar markierten Test-Key.
- `DJANGO_DEBUG` ist standardmaessig `False`.
- `DJANGO_ALLOWED_HOSTS` und `CORS_ALLOWED_ORIGINS` kommen aus Env-Werten.
- Production-HTTPS-Settings sind per Env aktivierbar.

Tokens:

- Tokens werden nur bei Registrierung und erfolgreichem Login ausgegeben.
- Fehlgeschlagene Logins enthalten kein Token.
- Tokens werden nicht in URLs oder Logs verwendet.

Secret Scanning:

- Lokal wurde Gitleaks genutzt.
- GitHub Actions fuehrt einen `Secret scan` aus.
- `.gitignore` schuetzt `.env`, Datenbanken, Backups, Logs, Coverage-Dateien
  sowie private Key- und Zertifikatsdateien.

## Tests

Die Tests liegen pro App in `tests/` und pruefen API-Verhalten direkt ueber
DRF-Testclients.

Testdaten sind fiktiv:

- `test_business`
- `test_customer`
- `other_business`
- `other_customer`
- `test-password`

Wichtige Testbereiche:

- Registrierung und Login.
- Passwort-Hashing im UserManager.
- Profilzugriff und Owner-Update.
- Offer-Erstellung, Filter, Update und Delete.
- Order-Erstellung, Snapshot und Zugriffsschutz.
- Review-Erstellung, doppelte Reviews und Permission-Verstoesse.
- Security-Regressions: keine Passwortfelder, keine Tokens bei Fehlern,
  sichere Test-Settings.

Coverage wird mit `coverage report --fail-under=95 -m` geprueft. GitHub Actions
fuehrt Django-Checks, Migration-Check, Format/Lint und Tests mit Coverage aus.

## Wichtige Designentscheidungen

### Custom User Model

- Entscheidung: `auth_app.User` erweitert `AbstractUser`.
- Warum: Rollen und Profilfelder gehoeren direkt zur Benutzeridentitaet.
- Alternative: separates Profile-Model mit OneToOneField.
- Vorteil: weniger Joins und einfachere Profile-Endpunkte.
- Nachteil: Das User-Model muss von Projektbeginn an korrekt gesetzt sein.

### Profilfelder auf dem User

- Entscheidung: Kein separates `Profile`-Model.
- Warum: Die API verwendet User-nahe Profile und rollenspezifische Felder.
- Alternative: `CustomerProfile` und `BusinessProfile`.
- Vorteil: weniger Models, gut erklaerbar.
- Nachteil: Einige Felder sind nur fuer Business fachlich relevant.

### DRF Token Authentication

- Entscheidung: `rest_framework.authtoken`.
- Warum: Die Referenz nutzt `Authorization: Token <token>`.
- Alternative: Session Authentication oder JWT.
- Vorteil: simpel und frontend-kompatibel.
- Nachteil: Tokens laufen nicht automatisch ab.

### Explizite Serializer-Felder

- Entscheidung: Alle Serializer listen `fields` explizit.
- Warum: Keine versehentliche Ausgabe sensibler Felder.
- Alternative: `fields = "__all__"`.
- Vorteil: klare API-Vertraege.
- Nachteil: Neue Felder muessen bewusst nachgetragen werden.

### Offer mit drei Details

- Entscheidung: Ein Offer enthaelt Basic, Standard und Premium.
- Warum: Das Frontend erwartet diese Paketstruktur.
- Alternative: frei viele Pakete.
- Vorteil: Validierung ist klar und vorhersehbar.
- Nachteil: weniger flexibel fuer andere Marktplatzmodelle.

### Order-Snapshot

- Entscheidung: Order kopiert Angebotsdaten beim Erstellen.
- Warum: Spaetere Offer-Aenderungen duerfen alte Bestellungen nicht veraendern.
- Alternative: Order liest immer live aus `OfferDetail`.
- Vorteil: historisch korrekte Bestellungen.
- Nachteil: redundante Daten in der Order.

### Queryset-basierter Zugriffsschutz

- Entscheidung: Orders werden bereits im Queryset auf beteiligte User begrenzt.
- Warum: Unbeteiligte User sollen Objekte gar nicht finden.
- Alternative: nur Object-Permissions.
- Vorteil: IDOR-Schutz und erwartbare 404-Antworten.
- Nachteil: Querysets sind etwas spezieller.

### Kleine Permission-Klassen

- Entscheidung: Pro fachlicher Regel kleine DRF-Permissions.
- Warum: Regeln bleiben testbar und direkt lesbar.
- Alternative: alle Regeln in Views pruefen.
- Vorteil: klare Trennung zwischen View und Zugriffsschutz.
- Nachteil: Kombinationen muessen verstanden werden.

### SQLite fuer die Abgabe

- Entscheidung: SQLite bleibt Standarddatenbank.
- Warum: Keine externe Infrastruktur fuer das Abschlussprojekt noetig.
- Alternative: PostgreSQL per `DATABASE_URL`.
- Vorteil: einfache Installation und Reproduzierbarkeit.
- Nachteil: nicht fuer hohe Produktionslast gedacht.

### Env-basierte Security Settings

- Entscheidung: Secret Key, Debug, Hosts, CORS und HTTPS-Flags kommen aus Env.
- Warum: Keine produktiven Werte im Repository.
- Alternative: hart codierte lokale Defaults.
- Vorteil: sicherer und deploymentfaehig.
- Nachteil: lokale Einrichtung braucht eine `.env`.

## Typische Prueferfragen

1. Warum wurde ein Custom User Model verwendet?
   Weil Rollen und Profilfelder direkt am User benoetigt werden und Django ein
   frueh gesetztes Custom User Model empfiehlt, wenn User-Daten erweitert werden.

2. Was macht `UserManager.create_user()`?
   Es normalisiert den Usernamen, erstellt den User und hasht das Passwort mit
   `set_password()`.

3. Warum wird `set_password()` verwendet?
   Damit kein Klartextpasswort in der Datenbank landet.

4. Was ist der Unterschied zwischen `validate()` und `validate_<field>()`?
   `validate_<field>()` prueft ein einzelnes Feld, `validate()` prueft
   Zusammenhaenge zwischen mehreren Feldern.

5. Warum prueft `RegistrationSerializer.validate()` beide Passwoerter?
   Weil `password` und `repeated_password` zusammenpassen muessen.

6. Warum werden Tokens nur bei Registrierung und Login ausgegeben?
   Weil nur diese Endpunkte Authentifizierung erzeugen sollen; normale Fehler
   oder Profilantworten duerfen keine Tokens enthalten.

7. Wie funktioniert DRF Token Authentication?
   Der Client sendet den Token im Header, DRF findet den passenden User und
   setzt `request.user`.

8. Warum sind Serializer-Felder explizit angegeben?
   Damit keine sensiblen oder undokumentierten Model-Felder versehentlich in der
   API erscheinen.

9. Wie wird verhindert, dass Passwort-Hashes ausgegeben werden?
   `ProfileSerializer` enthaelt kein `password`-Feld und Security-Tests pruefen
   genau dieses Verhalten.

10. Wie verhindert die Profil-Permission fremde Updates?
    `IsProfileOwnerOrReadOnly` erlaubt Schreibmethoden nur, wenn das Objekt der
    aktuelle User ist.

11. Warum gibt es `Offer` und `OfferDetail`?
    `Offer` beschreibt das Hauptangebot, `OfferDetail` die drei kaufbaren
    Pakete Basic, Standard und Premium.

12. Warum muss ein Offer alle drei Pakettypen enthalten?
    Die Frontend- und API-Anforderungen erwarten Basic, Standard und Premium.

13. Wann wird `select_related()` verwendet?
    Wenn ein ForeignKey-Objekt in derselben Query geladen werden soll, zum
    Beispiel der User eines Offers.

14. Wann wird `prefetch_related()` verwendet?
    Wenn mehrere verwandte Objekte geladen werden, zum Beispiel die Details
    eines Offers.

15. Warum nutzt `OfferViewSet` `annotate()`?
    Um `min_price` und `min_delivery_time` direkt aus den Details berechnen und
    sortieren zu koennen.

16. Warum wird ein Order-Snapshot gespeichert?
    Eine Bestellung soll den Stand zum Zeitpunkt der Bestellung behalten, auch
    wenn das Angebot spaeter geaendert wird.

17. Wie verhindert das Projekt IDOR bei Orders?
    `OrderViewSet.get_queryset()` gibt nur Orders zurueck, an denen der User als
    Customer oder Business beteiligt ist.

18. Warum sieht ein unbeteiligter User eine fremde Order nicht?
    Die Order ist nicht im Queryset enthalten und wird dadurch wie nicht
    vorhanden behandelt.

19. Wer darf den Order-Status aendern?
    Nur der beteiligte Business-User.

20. Warum duerfen Business-User keine Orders erstellen?
    Fachlich bestellt ein Customer ein Angebot; die Permission blockiert POST
    fuer Business-User.

21. Wie werden doppelte Reviews verhindert?
    Durch Serializer-Validierung und eine Datenbank-Unique-Constraint auf
    Reviewer plus Business-User.

22. Warum reicht Serializer-Validierung allein nicht immer aus?
    Weil parallele Requests oder direkte Datenbankzugriffe Validierung umgehen
    koennen; Constraints schuetzen zusaetzlich auf Datenbankebene.

23. Was bedeutet `on_delete=models.CASCADE`?
    Wird das referenzierte Objekt geloescht, werden abhaengige Objekte ebenfalls
    geloescht.

24. Warum ist `DJANGO_SECRET_KEY` verpflichtend?
    Ein bekannter Fallback-Key waere unsicher; jede Umgebung braucht einen
    eigenen geheimen Wert.

25. Warum ist ein Secret aus der Git-Historie als kompromittiert zu betrachten?
    Weil es nach einem Push nicht mehr verlaesslich geheim ist, selbst wenn es
    im aktuellen Code geloescht wurde.

26. Warum ist `DEBUG=False` der Default?
    Debug-Ausgaben koennen interne Informationen zeigen und sollen nur bewusst
    lokal aktiviert werden.

27. Warum stehen CORS Origins ohne abschliessenden Slash in `.env`?
    Django CORS Headers erwartet Origins im Format Schema plus Host und Port,
    nicht als URL-Pfad.

28. Warum nutzt die CI `coverage report --fail-under=95 -m`?
    Dadurch schlaegt der Workflow fehl, wenn die Coverage unter 95 Prozent
    faellt.

29. Warum gibt es einen Gitleaks-Workflow?
    Damit Pull Requests und Pushes automatisch auf versehentlich committed
    Secrets geprueft werden.

30. Welche Datei wuerdest du zuerst zeigen, um das Routing zu erklaeren?
    `core/urls.py`, weil dort alle App-Routen und Spezialendpunkte verbunden
    werden.
