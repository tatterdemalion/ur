"""
Internationalisation support for the Royal Game of Ur CLI.

Usage:
    from ur.cli.i18n import t, set_language, LANGUAGES

    t("key")          # returns translated string for current language
    set_language("de")  # switch to German
"""

from __future__ import annotations

_STRINGS: dict[str, dict[str, str]] = {
    # ── Splash screen ────────────────────────────────────────────────────
    "splash.press_enter": {
        "en": "Press Enter to step into the past...",
        "de": "Drücke Enter, um in die Vergangenheit einzutauchen...",
        "nl": "Druk op Enter om de geschiedenis in te stappen...",
        "es": "Pulsa Enter para adentrarte en el pasado...",
        "tr": "Geçmişe adım atmak için Enter'a bas...",
    },
    "splash.task.0": {
        "en": "Sweeping sand off the board...",
        "de": "Sand vom Spielbrett fegen...",
        "nl": "Zand van het bord vegen...",
        "es": "Barriendo la arena del tablero...",
        "tr": "Tahtadan kum süpürülüyor...",
    },
    "splash.task.1": {
        "en": "Carving lapis lazuli...",
        "de": "Lapislazuli schnitzen...",
        "nl": "Lazuursteen bewerken...",
        "es": "Tallando lapislázuli...",
        "tr": "Lapislazuli oyuluyor...",
    },
    "splash.task.2": {
        "en": "Consulting the Oracles...",
        "de": "Die Orakel befragen...",
        "nl": "De Orakels raadplegen...",
        "es": "Consultando a los Oráculos...",
        "tr": "Kehanetlere danışılıyor...",
    },
    "splash.task.3": {
        "en": "Rolling the tetrahedrons...",
        "de": "Die Tetraeder rollen...",
        "nl": "De tetraëders gooien...",
        "es": "Lanzando los tetraedros...",
        "tr": "Dört yüzlüler atılıyor...",
    },
    "splash.task.4": {
        "en": "Waking the Gods...",
        "de": "Die Götter wecken...",
        "nl": "De Goden wekken...",
        "es": "Despertando a los Dioses...",
        "tr": "Tanrılar uyandırılıyor...",
    },
    # ── Navigation ───────────────────────────────────────────────────────
    "nav.commands_hint": {
        "en": "  (Type 'menu' to return to main menu, 'exit' or 'quit' to quit)",
        "de": "  (Tippe 'menu' für das Hauptmenü, 'exit' oder 'quit' zum Beenden)",
        "nl": "  (Typ 'menu' voor hoofdmenu, 'exit' of 'quit' om af te sluiten)",
        "es": "  (Escribe 'menu' para volver al menú, 'exit' o 'quit' para salir)",
        "tr": "  (Ana menüye dönmek için 'menu', çıkmak için 'exit' veya 'quit' yaz)",
    },
    "nav.select_option": {
        "en": "Select an option: ",
        "de": "Option wählen: ",
        "nl": "Kies een optie: ",
        "es": "Selecciona una opción: ",
        "tr": "Bir seçenek seçin: ",
    },
    "nav.press_enter_menu": {
        "en": "\nPress Enter to return to the main menu: ",
        "de": "\nDrücke Enter, um zum Hauptmenü zurückzukehren: ",
        "nl": "\nDruk op Enter om terug te keren naar het hoofdmenu: ",
        "es": "\nPulsa Enter para volver al menú principal: ",
        "tr": "\nAna menüye dönmek için Enter'a bas: ",
    },
    # ── Main menu ────────────────────────────────────────────────────────
    "menu.title": {
        "en": "THE ROYAL GAME OF UR",
        "de": "DAS KÖNIGLICHE SPIEL VON UR",
        "nl": "HET KONINKLIJKE SPEL VAN UR",
        "es": "EL JUEGO REAL DE UR",
        "tr": "UR'UN KRALIYET OYUNU",
    },
    "menu.play_vs_bot": {
        "en": "Play vs Bot",
        "de": "Gegen Bot spielen",
        "nl": "Spelen tegen bot",
        "es": "Jugar contra el bot",
        "tr": "Bot'a karşı oyna",
    },
    "menu.continue_vs_bot": {
        "en": "Continue vs Bot",
        "de": "Spiel gegen Bot fortsetzen",
        "nl": "Verder spelen tegen bot",
        "es": "Continuar contra el bot",
        "tr": "Bot'a karşı devam et",
    },
    "menu.host": {
        "en": "Host Multiplayer Game",
        "de": "Mehrspieler-Spiel hosten",
        "nl": "Multiplayerspel hosten",
        "es": "Crear partida multijugador",
        "tr": "Çok oyunculu oyun kur",
    },
    "menu.join": {
        "en": "Join Multiplayer Game",
        "de": "Mehrspieler-Spiel beitreten",
        "nl": "Deelnemen aan multiplayerspel",
        "es": "Unirse a partida multijugador",
        "tr": "Çok oyunculu oyuna katıl",
    },
    "menu.tutorial": {
        "en": "How to Play (Tutorial)",
        "de": "Wie man spielt (Tutorial)",
        "nl": "Hoe te spelen (Tutorial)",
        "es": "Cómo jugar (Tutorial)",
        "tr": "Nasıl oynanır (Öğretici)",
    },
    "menu.language": {
        "en": "Change Language",
        "de": "Sprache ändern",
        "nl": "Taal wijzigen",
        "es": "Cambiar idioma",
        "tr": "Dili değiştir",
    },
    # ── Tutorial ─────────────────────────────────────────────────────────
    "tutorial.title": {
        "en": "HOW TO PLAY THE ROYAL GAME OF UR",
        "de": "WIE MAN DAS KÖNIGLICHE SPIEL VON UR SPIELT",
        "nl": "HOE HET KONINKLIJKE SPEL VAN UR TE SPELEN",
        "es": "CÓMO JUGAR AL JUEGO REAL DE UR",
        "tr": "UR'UN KRALIYET OYUNU NASIL OYNANIR",
    },
    "tutorial.line1": {
        "en": "1. Objective: Move all 7 of your pieces across the board to the end before your opponent.",
        "de": "1. Ziel: Bewege alle 7 Figuren vor deinem Gegner ans Ende des Bretts.",
        "nl": "1. Doel: Beweeg al je 7 stukken over het bord naar het einde voor je tegenstander.",
        "es": "1. Objetivo: Mueve tus 7 piezas al final del tablero antes que tu oponente.",
        "tr": "1. Amaç: 7 taşının tamamını rakibinden önce tahtanın sonuna taşı.",
    },
    "tutorial.line2": {
        "en": "2. Movement: You roll 4 binary dice each turn, yielding a move of 0 to 4 spaces.",
        "de": "2. Bewegung: Würfle jede Runde 4 binäre Würfel für 0 bis 4 Felder.",
        "nl": "2. Beweging: Gooi elke beurt 4 binaire dobbelstenen voor 0 tot 4 stappen.",
        "es": "2. Movimiento: Lanzas 4 dados binarios cada turno, obteniendo entre 0 y 4 pasos.",
        "tr": "2. Hareket: Her turda 4 ikili zar atarsın; 0 ile 4 kare arasında hareket edersin.",
    },
    "tutorial.line3": {
        "en": "3. Stacking: You cannot land on a square occupied by your own piece.",
        "de": "3. Stapeln: Du kannst nicht auf ein Feld ziehen, das bereits deine eigene Figur belegt.",
        "nl": "3. Stapelen: Je kunt niet landen op een veld dat al bezet is door je eigen stuk.",
        "es": "3. Apilamiento: No puedes caer en una casilla ocupada por tu propia pieza.",
        "tr": "3. Üst üste binme: Kendi taşının bulunduğu kareye inemezsin.",
    },
    "tutorial.line4": {
        "en": "4. Combat: Landing on an opponent's piece in the shared middle row 'captures' it,",
        "de": "4. Kampf: Landet eine Figur auf einer gegnerischen in der gemeinsamen Mittelreihe, wird sie 'geschlagen',",
        "nl": "4. Gevecht: Op een stuk van de tegenstander in de gedeelde middelste rij landen 'slaat' het,",
        "es": "4. Combate: Caer sobre una pieza enemiga en la fila central compartida la 'captura',",
        "tr": "4. Savaş: Ortak orta sırada rakip taşın üzerine inersen onu 'ele geçirirsin',",
    },
    "tutorial.line4b": {
        "en": "   sending it back off-board to start over.",
        "de": "   und sie muss von vorne beginnen.",
        "nl": "   waarna het teruggestuurd wordt om opnieuw te beginnen.",
        "es": "   enviándola de vuelta fuera del tablero para empezar de nuevo.",
        "tr": "   o taş başa döner.",
    },
    "tutorial.line5": {
        "en": "5. Rosettas: Landing on a Rosetta ({rosetta}) grants an extra turn immediately.",
        "de": "5. Rosetten: Auf einer Rosette ({rosetta}) landen gibt sofort einen Extrazug.",
        "nl": "5. Rozetten: Op een Rozet ({rosetta}) landen geeft direct een extra beurt.",
        "es": "5. Rosetones: Caer en un Rosetón ({rosetta}) concede un turno extra inmediatamente.",
        "tr": "5. Rozetler: Rozet ({rosetta}) üzerine inmek (Rozetlenmek) anında ekstra tur kazandırır.",
    },
    "tutorial.line5b": {
        "en": "   Additionally, the central Rosetta is a safe haven where your piece cannot be captured.",
        "de": "   Außerdem ist die mittlere Rosette ein sicherer Hafen, dort kann deine Figur nicht geschlagen werden.",
        "nl": "   Bovendien is het centrale Rozet een veilige haven waar je stuk niet geslagen kan worden.",
        "es": "   Además, el Rosetón central es un refugio seguro donde tu pieza no puede ser capturada.",
        "tr": "   Ayrıca merkezdeki rozet güvenli bir limandır; oradaki taşın ele geçirilemez.",
    },
    # ── Bot selection ─────────────────────────────────────────────────────
    "bot.select_title": {
        "en": "SELECT OPPONENT",
        "de": "GEGNER WÄHLEN",
        "nl": "TEGENSTANDER KIEZEN",
        "es": "SELECCIONAR OPONENTE",
        "tr": "RAKİP SEÇ",
    },
    "bot.random": {
        "en": "RandomBot    (Easy - Moves completely randomly)",
        "de": "RandomBot    (Leicht - Zieht völlig zufällig)",
        "nl": "RandomBot    (Makkelijk - Beweegt volledig willekeurig)",
        "es": "RandomBot    (Fácil - Se mueve completamente al azar)",
        "tr": "RandomBot    (Kolay - Tamamen rastgele hareket eder)",
    },
    "bot.greedy": {
        "en": "GreedyBot    (Medium - Always takes points or hits immediately)",
        "de": "GreedyBot    (Mittel - Nimmt sofort Punkte oder trifft)",
        "nl": "GreedyBot    (Gemiddeld - Pakt altijd direct punten of slaat)",
        "es": "GreedyBot    (Medio - Siempre toma puntos o golpea inmediatamente)",
        "tr": "GreedyBot    (Orta - Her zaman anında puan alır veya vurur)",
    },
    "bot.strategic": {
        "en": "StrategicBot (Hard - Calculates probabilities of danger)",
        "de": "StrategicBot (Schwer - Berechnet Gefahrenwahrscheinlichkeiten)",
        "nl": "StrategicBot (Moeilijk - Berekent gevaarskansen)",
        "es": "StrategicBot (Difícil - Calcula probabilidades de peligro)",
        "tr": "StrategicBot (Zor - Tehlike olasılıklarını hesaplar)",
    },
    # ── Continue game ─────────────────────────────────────────────────────
    "continue.title": {
        "en": "CONTINUE GAME",
        "de": "SPIEL FORTSETZEN",
        "nl": "SPEL VOORTZETTEN",
        "es": "CONTINUAR PARTIDA",
        "tr": "OYUNA DEVAM ET",
    },
    "continue.no_saves": {
        "en": "No local saves found.",
        "de": "Keine lokalen Speicherstände gefunden.",
        "nl": "Geen lokale opgeslagen spellen gevonden.",
        "es": "No se encontraron partidas guardadas.",
        "tr": "Yerel kayıt bulunamadı.",
    },
    # ── Join game ─────────────────────────────────────────────────────────
    "join.title": {
        "en": "JOIN GAME",
        "de": "SPIEL BEITRETEN",
        "nl": "SPEL DEELNEMEN",
        "es": "UNIRSE A PARTIDA",
        "tr": "OYUNA KATIL",
    },
    "join.enter_ip": {
        "en": "Enter host IP address: ",
        "de": "Host-IP-Adresse eingeben: ",
        "nl": "Voer het IP-adres van de host in: ",
        "es": "Introduce la dirección IP del anfitrión: ",
        "tr": "Sunucu IP adresini girin: ",
    },
    "join.enter_ip_last": {
        "en": "Enter host IP address [{last_ip}]: ",
        "de": "Host-IP-Adresse eingeben [{last_ip}]: ",
        "nl": "Voer het IP-adres van de host in [{last_ip}]: ",
        "es": "Introduce la dirección IP del anfitrión [{last_ip}]: ",
        "tr": "Sunucu IP adresini girin [{last_ip}]: ",
    },
    # ── Host game ─────────────────────────────────────────────────────────
    "host.title": {
        "en": "HOST GAME",
        "de": "SPIEL HOSTEN",
        "nl": "SPEL HOSTEN",
        "es": "CREAR PARTIDA",
        "tr": "OYUN KUR",
    },
    "host.new_game": {
        "en": "New game",
        "de": "Neues Spiel",
        "nl": "Nieuw spel",
        "es": "Nueva partida",
        "tr": "Yeni oyun",
    },
    "host.saved_lan_games": {
        "en": "Saved LAN games:",
        "de": "Gespeicherte LAN-Spiele:",
        "nl": "Opgeslagen LAN-spellen:",
        "es": "Partidas LAN guardadas:",
        "tr": "Kaydedilmiş LAN oyunları:",
    },
    "host.enter_game_name": {
        "en": "Enter a game name (or press Enter to start fresh): ",
        "de": "Spielnamen eingeben (oder Enter für ein neues Spiel): ",
        "nl": "Voer een spelnaam in (of druk op Enter voor een nieuw spel): ",
        "es": "Introduce un nombre de partida (o pulsa Enter para empezar de nuevo): ",
        "tr": "Oyun adı girin (yeni oyun için Enter'a basın): ",
    },
    "host.no_save_found": {
        "en": "No save found for '{name}'. Starting a new game.",
        "de": "Kein Speicherstand für '{name}' gefunden. Neues Spiel beginnt.",
        "nl": "Geen opgeslagen spel gevonden voor '{name}'. Nieuw spel starten.",
        "es": "No se encontró partida guardada para '{name}'. Iniciando nueva partida.",
        "tr": "'{name}' için kayıt bulunamadı. Yeni oyun başlatılıyor.",
    },
    "host.game_name_label": {
        "en": "Game name: ",
        "de": "Spielname: ",
        "nl": "Spelnaam: ",
        "es": "Nombre de partida: ",
        "tr": "Oyun adı: ",
    },
    "host.your_ip": {
        "en": "\nYour IP address : ",
        "de": "\nDeine IP-Adresse: ",
        "nl": "\nJouw IP-adres: ",
        "es": "\nTu dirección IP: ",
        "tr": "\nIP adresin: ",
    },
    "host.listening": {
        "en": "Listening on port {port}...",
        "de": "Warte auf Port {port}...",
        "nl": "Luisteren op poort {port}...",
        "es": "Escuchando en el puerto {port}...",
        "tr": "{port} portunda dinleniyor...",
    },
    "host.waiting": {
        "en": "Waiting for opponent to connect...\n",
        "de": "Warte auf Gegner...\n",
        "nl": "Wachten op tegenstander...\n",
        "es": "Esperando a que el oponente se conecte...\n",
        "tr": "Rakip bekleniyor...\n",
    },
    "host.opponent_connected": {
        "en": "Opponent connected from {ip}!\n",
        "de": "Gegner verbunden von {ip}!\n",
        "nl": "Tegenstander verbonden vanaf {ip}!\n",
        "es": "¡Oponente conectado desde {ip}!\n",
        "tr": "{ip} adresinden rakip bağlandı!\n",
    },
    "host.resuming": {
        "en": "Resuming '{name}'...",
        "de": "'{name}' wird fortgesetzt...",
        "nl": "'{name}' wordt hervat...",
        "es": "Reanudando '{name}'...",
        "tr": "'{name}' devam ettiriliyor...",
    },
    # ── Match / in-game ───────────────────────────────────────────────────
    "match.your_turn": {
        "en": "Your turn.",
        "de": "Dein Zug.",
        "nl": "Jouw beurt.",
        "es": "Tu turno.",
        "tr": "Senin sıran.",
    },
    "match.opponent_turn": {
        "en": "{name}'s turn.",
        "de": "{name}s Zug.",
        "nl": "Beurt van {name}.",
        "es": "Turno de {name}.",
        "tr": "{name}'in sırası.",
    },
    "match.no_valid_moves": {
        "en": "No valid moves. Turn skipped.",
        "de": "Keine gültigen Züge. Runde wird übersprungen.",
        "nl": "Geen geldige zetten. Beurt overgeslagen.",
        "es": "Sin movimientos válidos. Turno omitido.",
        "tr": "Geçerli hamle yok. Tur atlandı.",
    },
    "match.waiting_opponent": {
        "en": "Waiting for opponent to move...",
        "de": "Warte auf den Zug des Gegners...",
        "nl": "Wachten op zet van tegenstander...",
        "es": "Esperando el movimiento del oponente...",
        "tr": "Rakibin hamlesi bekleniyor...",
    },
    "match.opponent_disconnected": {
        "en": "\nOpponent disconnected.",
        "de": "\nGegner hat die Verbindung getrennt.",
        "nl": "\nTegenstander heeft de verbinding verbroken.",
        "es": "\nEl oponente se ha desconectado.",
        "tr": "\nRakip bağlantıyı kesti.",
    },
    "match.press_enter_menu": {
        "en": "\nPress Enter to return to the main menu: ",
        "de": "\nDrücke Enter, um zum Hauptmenü zurückzukehren: ",
        "nl": "\nDruk op Enter om terug te keren naar het hoofdmenu: ",
        "es": "\nPulsa Enter para volver al menú principal: ",
        "tr": "\nAna menüye dönmek için Enter'a bas: ",
    },
    "match.connecting": {
        "en": "Connecting to {host}:{port}...",
        "de": "Verbinde mit {host}:{port}...",
        "nl": "Verbinding maken met {host}:{port}...",
        "es": "Conectando a {host}:{port}...",
        "tr": "{host}:{port} adresine bağlanılıyor...",
    },
    "match.failed_connect": {
        "en": "Failed to connect to host.",
        "de": "Verbindung zum Host fehlgeschlagen.",
        "nl": "Verbinding met host mislukt.",
        "es": "Error al conectar con el anfitrión.",
        "tr": "Sunucuya bağlanılamadı.",
    },
    "match.connected": {
        "en": "Connected!\n",
        "de": "Verbunden!\n",
        "nl": "Verbonden!\n",
        "es": "¡Conectado!\n",
        "tr": "Bağlandı!\n",
    },
    "match.opponent_turn_anim": {
        "en": "Opponent's turn.",
        "de": "Zug des Gegners.",
        "nl": "Beurt van tegenstander.",
        "es": "Turno del oponente.",
        "tr": "Rakibin sırası.",
    },
    "match.last_action": {
        "en": "Last action: ",
        "de": "Letzter Zug: ",
        "nl": "Laatste actie: ",
        "es": "Última acción: ",
        "tr": "Son hamle: ",
    },
    "match.save_found": {
        "en": "Save found: ",
        "de": "Speicherstand gefunden: ",
        "nl": "Opgeslagen spel gevonden: ",
        "es": "Partida guardada encontrada: ",
        "tr": "Kayıt bulundu: ",
    },
    # ── Board ─────────────────────────────────────────────────────────────
    "board.title": {
        "en": "THE ROYAL GAME OF UR",
        "de": "DAS KÖNIGLICHE SPIEL VON UR",
        "nl": "HET KONINKLIJKE SPEL VAN UR",
        "es": "EL JUEGO REAL DE UR",
        "tr": "UR'UN KRALIYET OYUNU",
    },
    # ── Game utils / move selection ───────────────────────────────────────
    "move.your_options": {
        "en": "Your options:",
        "de": "Deine Optionen:",
        "nl": "Jouw opties:",
        "es": "Tus opciones:",
        "tr": "Seçeneklerin:",
    },
    "move.off_board": {
        "en": "Off-board",
        "de": "Nicht im Spiel",
        "nl": "Buiten het bord",
        "es": "Fuera del tablero",
        "tr": "Tahta dışı",
    },
    "move.finish": {
        "en": "Finish",
        "de": "Ziel",
        "nl": "Finish",
        "es": "Meta",
        "tr": "Bitiş",
    },
    "move.square": {
        "en": "Square {letter}",
        "de": "Feld {letter}",
        "nl": "Veld {letter}",
        "es": "Casilla {letter}",
        "tr": "Kare {letter}",
    },
    "move.rosetta_first": {
        "en": "first",
        "de": "erste",
        "nl": "eerste",
        "es": "primero",
        "tr": "birinci",
    },
    "move.rosetta_middle": {
        "en": "middle",
        "de": "mittlere",
        "nl": "middelste",
        "es": "central",
        "tr": "ortadaki",
    },
    "move.rosetta_last": {
        "en": "last",
        "de": "letzte",
        "nl": "laatste",
        "es": "último",
        "tr": "sonuncu",
    },
    "move.scores_point": {
        "en": "Scores a point!",
        "de": "Erzielt einen Punkt!",
        "nl": "Scoort een punt!",
        "es": "¡Anota un punto!",
        "tr": "Puan kazanıyor!",
    },
    "move.lands_rosetta": {
        "en": "Lands on Rosetta (Roll again!)",
        "de": "Landet auf Rosette (Nochmal würfeln!)",
        "nl": "Landt op Rozet (Nogmaals gooien!)",
        "es": "Cae en Rosetón (¡Vuelve a tirar!)",
        "tr": "Rozet (Tekrar at!)",
    },
    "move.captures": {
        "en": "Captures {name}'s piece!",
        "de": "Schlägt {name}s Figur!",
        "nl": "Slaat stuk van {name}!",
        "es": "¡Captura la pieza de {name}!",
        "tr": "{name}'in taşını ele geçiriyor!",
    },
    "move.select_prompt": {
        "en": "\nSelect a piece to move (1-7)",
        "de": "\nWähle eine Figur zum Bewegen (1-7)",
        "nl": "\nKies een stuk om te bewegen (1-7)",
        "es": "\nSelecciona una pieza para mover (1-7)",
        "tr": "\nHareket ettirilecek taşı seç (1-7)",
    },
    "move.select_prompt_default": {
        "en": " [Enter for {id}]: ",
        "de": " [Enter für {id}]: ",
        "nl": " [Enter voor {id}]: ",
        "es": " [Enter para {id}]: ",
        "tr": " [Enter ile {id}]: ",
    },
    "move.select_prompt_end": {
        "en": ": ",
        "de": ": ",
        "nl": ": ",
        "es": ": ",
        "tr": ": ",
    },
    "move.invalid_choice": {
        "en": "Invalid choice. That piece cannot move right now.",
        "de": "Ungültige Wahl. Diese Figur kann gerade nicht ziehen.",
        "nl": "Ongeldige keuze. Dit stuk kan nu niet bewegen.",
        "es": "Elección inválida. Esa pieza no puede moverse ahora.",
        "tr": "Geçersiz seçim. Bu taş şu an hareket edemiyor.",
    },
    "move.invalid_number": {
        "en": "Please enter a valid piece number.",
        "de": "Bitte eine gültige Figurennummer eingeben.",
        "nl": "Voer een geldig stuksnummer in.",
        "es": "Por favor introduce un número de pieza válido.",
        "tr": "Lütfen geçerli bir taş numarası girin.",
    },
    # ── Action log ────────────────────────────────────────────────────────
    "action.game_started": {
        "en": "Game started.",
        "de": "Spiel gestartet.",
        "nl": "Spel gestart.",
        "es": "Partida iniciada.",
        "tr": "Oyun başladı.",
    },
    "action.you": {
        "en": "You",
        "de": "Du",
        "nl": "Jij",
        "es": "Tú",
        "tr": "Sen",
    },
    "action.rosetta_target": {
        "en": "the {label}",
        "de": "die {label}",
        "nl": "het {label}",
        "es": "el {label}",
        "tr": "{label}",
    },
    "action.skipped": {
        "en": "{subject} rolled {roll} and had no moves.",
        "de": "{subject} hat {roll} gewürfelt und hatte keine Züge.",
        "nl": "{subject} gooide {roll} en had geen zetten.",
        "es": "{subject} sacó {roll} y no tuvo movimientos.",
        "tr": "{roll} — {subject} hamle yapamadı.",
    },
    "action.skipped_you": {
        "en": "{subject} rolled {roll} and had no moves.",
        "de": "{subject} hat {roll} gewürfelt und hatte keine Züge.",
        "nl": "Je gooide {roll} en had geen zetten.",
        "es": "Sacaste {roll} y no tuviste movimientos.",
        "tr": "{roll} — hamle yapamadın.",
    },
    "action.scored_you": {
        "en": "{subject} rolled {roll} and piece {piece} scored!",
        "de": "{subject} hat {roll} gewürfelt und Figur {piece} hat gepunktet!",
        "nl": "Je gooide {roll} en stuk {piece} scoorde!",
        "es": "Sacaste {roll} y la pieza {piece} anotó!",
        "tr": "{roll} — {piece} taşınla puan kazandın!",
    },
    "action.scored_opp": {
        "en": "{subject} rolled {roll} and scored a piece!",
        "de": "{subject} hat {roll} gewürfelt und eine Figur gepunktet!",
        "nl": "{subject} gooide {roll} en scoorde een stuk!",
        "es": "{subject} sacó {roll} y anotó una pieza!",
        "tr": "{roll} — {subject} bir taşla puan yaptı!",
    },
    "action.moved_you": {
        "en": "{subject} rolled {roll} and moved piece {piece} to {target}.",
        "de": "{subject} hat {roll} gewürfelt und Figur {piece} nach {target} gezogen.",
        "nl": "Je gooide {roll} en verplaatste stuk {piece} naar {target}.",
        "es": "Sacaste {roll} y moviste la pieza {piece} a {target}.",
        "tr": "{roll} — {piece} taşını {target} üzerine taşıdın.",
    },
    "action.moved_opp": {
        "en": "{subject} rolled {roll} and moved a piece to {target}.",
        "de": "{subject} hat {roll} gewürfelt und eine Figur nach {target} gezogen.",
        "nl": "{subject} gooide {roll} en verplaatste een stuk naar {target}.",
        "es": "{subject} sacó {roll} y movió una pieza a {target}.",
        "tr": "{roll} — {subject} bir taşı {target} üzerine taşıdı.",
    },
    "action.hit_you": {
        "en": "Took one of their pieces!",
        "de": "Eine ihrer Figuren geschlagen!",
        "nl": "Eén van hun stukken geslagen!",
        "es": "¡Capturaste una de sus piezas!",
        "tr": "Rakip taşı geri gönderildi!",
    },
    "action.hit_opp": {
        "en": "Took out one of your pieces!",
        "de": "Eine deiner Figuren wurde geschlagen!",
        "nl": "Eén van jouw stukken werd geslagen!",
        "es": "¡Capturó una de tus piezas!",
        "tr": "Taşın geri gönderildi!",
    },
    "action.rosetta_you": {
        "en": "It is your turn again!",
        "de": "Du bist nochmal dran!",
        "nl": "Jij bent weer aan de beurt!",
        "es": "¡Es tu turno de nuevo!",
        "tr": "Tekrar senin sıran!",
    },
    "action.rosetta_opp": {
        "en": "It is their turn again!",
        "de": "Sie sind nochmal dran!",
        "nl": "Zij zijn weer aan de beurt!",
        "es": "¡Es su turno de nuevo!",
        "tr": "Tekrar onların sırası!",
    },
    # ── Language menu ─────────────────────────────────────────────────────
    "lang.title": {
        "en": "SELECT LANGUAGE",
        "de": "SPRACHE WÄHLEN",
        "nl": "TAAL KIEZEN",
        "es": "SELECCIONAR IDIOMA",
        "tr": "DİL SEÇ",
    },
    "lang.english": {
        "en": "English",
        "de": "Englisch",
        "nl": "Engels",
        "es": "Inglés",
        "tr": "İngilizce",
    },
    "lang.german": {
        "en": "German",
        "de": "Deutsch",
        "nl": "Duits",
        "es": "Alemán",
        "tr": "Almanca",
    },
    "lang.dutch": {
        "en": "Dutch",
        "de": "Niederländisch",
        "nl": "Nederlands",
        "es": "Neerlandés",
        "tr": "Hollandaca",
    },
    "lang.spanish": {
        "en": "Spanish",
        "de": "Spanisch",
        "nl": "Spaans",
        "es": "Español",
        "tr": "İspanyolca",
    },
    "lang.turkish": {
        "en": "Turkish",
        "de": "Türkisch",
        "nl": "Turks",
        "es": "Turco",
        "tr": "Türkçe",
    },
    # ── Player names ──────────────────────────────────────────────────────
    "player.you": {
        "en": "You",
        "de": "Du",
        "nl": "Jij",
        "es": "Tú",
        "tr": "Sen",
    },
    "player.opponent": {
        "en": "Opponent",
        "de": "Gegner",
        "nl": "Tegenstander",
        "es": "Oponente",
        "tr": "Rakip",
    },
}

LANGUAGES: dict[str, str] = {
    "en": "English",
    "de": "German",
    "nl": "Dutch",
    "es": "Spanish",
    "tr": "Turkish",
}

_current_language: str = "en"


def set_language(lang: str) -> None:
    global _current_language
    if lang in LANGUAGES:
        _current_language = lang


def get_language() -> str:
    return _current_language


def t(key: str, **kwargs: str) -> str:
    """Return the translated string for *key* in the current language.

    Falls back to English when the key is missing in the active language.
    Supports simple ``{placeholder}`` substitution via keyword arguments.
    """
    entry = _STRINGS.get(key, {})
    text = entry.get(_current_language) or entry.get("en") or key
    if kwargs:
        text = text.format(**kwargs)
    return text
