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
        "tr": "Geçmişe adım atmak için Enter'a bas...",
    },
    "splash.task.0": {
        "en": "Sweeping sand off the board...",
        "tr": "Tahtadan kum süpürülüyor...",
    },
    "splash.task.1": {
        "en": "Carving lapis lazuli...",
        "tr": "Lapislazuli oyuluyor...",
    },
    "splash.task.2": {
        "en": "Consulting the Oracles...",
        "tr": "Kehanetlere danışılıyor...",
    },
    "splash.task.3": {
        "en": "Rolling the tetrahedrons...",
        "tr": "Dört yüzlüler atılıyor...",
    },
    "splash.task.4": {
        "en": "Waking the Gods...",
        "tr": "Tanrılar uyandırılıyor...",
    },
    # ── Navigation ───────────────────────────────────────────────────────
    "nav.commands_hint": {
        "en": "  (Type 'menu' to return to main menu, 'quit' to quit)",
        "tr": "  (Ana menüye dönmek için 'menu', çıkmak için 'quit' yaz)",
    },
    "nav.ingame_commands_hint": {
        "en": "  (Type 'menu' to return to main menu, 'quit' to quit, 'help' for board labels and move hints)",
        "tr": "  ('menu' ana menü, 'quit' çıkış, 'help' tahta etiketleri ve hamle ipuçları)",
    },
    "nav.ingame_help_open_hint": {
        "en": "  (Type 'back' to hide labels, 'menu' to return to main menu, 'quit' to quit)",
        "tr": "  (Etiketleri gizlemek için 'back', 'menu' ana menü, 'quit' çıkış)",
    },
    "nav.select_option": {
        "en": "Select an option: ",
        "tr": "Bir seçenek seçin: ",
    },
    "nav.press_enter_menu": {
        "en": "\nPress Enter to return to the main menu: ",
        "tr": "\nAna menüye dönmek için Enter'a bas: ",
    },
    # ── Main menu ────────────────────────────────────────────────────────
    "menu.title": {
        "en": "THE ROYAL GAME OF UR",
        "tr": "UR'UN KRALIYET OYUNU",
    },
    "menu.play_vs_bot": {
        "en": "Play vs Bot",
        "tr": "Bot'a karşı oyna",
    },
    "menu.continue_vs_bot": {
        "en": "Continue vs Bot",
        "tr": "Bot'a karşı devam et",
    },
    "menu.host": {
        "en": "Host Multiplayer Game",
        "tr": "Çok oyunculu oyun kur",
    },
    "menu.join": {
        "en": "Join Multiplayer Game",
        "tr": "Çok oyunculu oyuna katıl",
    },
    "menu.tutorial": {
        "en": "How to Play (Tutorial)",
        "tr": "Nasıl oynanır (Öğretici)",
    },
    "menu.language": {
        "en": "Change Language",
        "tr": "Dili değiştir",
    },
    # ── Tutorial ─────────────────────────────────────────────────────────
    "tutorial.title": {
        "en": "HOW TO PLAY THE ROYAL GAME OF UR",
        "tr": "UR'UN KRALIYET OYUNU NASIL OYNANIR",
    },
    "tutorial.line1": {
        "en": "1. Objective: Move all 7 of your pieces across the board to the end before your opponent.",
        "tr": "1. Amaç: 7 taşının tamamını rakibinden önce tahtanın sonuna taşı.",
    },
    "tutorial.line2": {
        "en": "2. Movement: You roll 4 binary dice each turn, yielding a move of 0 to 4 spaces.",
        "tr": "2. Hareket: Her turda 4 ikili zar atarsın; 0 ile 4 kare arasında hareket edersin.",
    },
    "tutorial.line3": {
        "en": "3. Stacking: You cannot land on a square occupied by your own piece.",
        "tr": "3. Üst üste binme: Kendi taşının bulunduğu kareye inemezsin.",
    },
    "tutorial.line4": {
        "en": "4. Combat: Landing on an opponent's piece in the shared middle row 'captures' it,",
        "tr": "4. Savaş: Ortak orta sırada rakip taşın üzerine inersen onu 'ele geçirirsin',",
    },
    "tutorial.line4b": {
        "en": "   sending it back off-board to start over.",
        "tr": "   o taş başa döner.",
    },
    "tutorial.line5": {
        "en": "5. Rosettas: Landing on a Rosetta ({rosetta}) grants an extra turn immediately.",
        "tr": "5. Rozetler: Rozet ({rosetta}) üzerine inmek (Rozetlenmek) anında ekstra tur kazandırır.",
    },
    "tutorial.line5b": {
        "en": "   Additionally, the central Rosetta is a safe haven where your piece cannot be captured.",
        "tr": "   Ayrıca merkezdeki rozet güvenli bir limandır; oradaki taşın ele geçirilemez.",
    },
    # ── Bot selection ─────────────────────────────────────────────────────
    "bot.select_title": {
        "en": "SELECT OPPONENT",
        "tr": "RAKİP SEÇ",
    },
    "bot.random": {
        "en": "RandomBot    (Easy - Moves completely randomly)",
        "tr": "RandomBot    (Kolay - Tamamen rastgele hareket eder)",
    },
    "bot.greedy": {
        "en": "GreedyBot    (Medium - Always takes points or hits immediately)",
        "tr": "GreedyBot    (Orta - Her zaman anında puan alır veya vurur)",
    },
    "bot.strategic": {
        "en": "StrategicBot (Hard - Calculates probabilities of danger)",
        "tr": "StrategicBot (Zor - Tehlike olasılıklarını hesaplar)",
    },
    # ── Continue game ─────────────────────────────────────────────────────
    "continue.title": {
        "en": "CONTINUE GAME",
        "tr": "OYUNA DEVAM ET",
    },
    "continue.no_saves": {
        "en": "No local saves found.",
        "tr": "Yerel kayıt bulunamadı.",
    },
    # ── Join game ─────────────────────────────────────────────────────────
    "join.title": {
        "en": "JOIN GAME",
        "tr": "OYUNA KATIL",
    },
    "join.enter_ip": {
        "en": "Enter host IP address: ",
        "tr": "Sunucu IP adresini girin: ",
    },
    "join.enter_ip_last": {
        "en": "Enter host IP address [{last_ip}]: ",
        "tr": "Sunucu IP adresini girin [{last_ip}]: ",
    },
    # ── Host game ─────────────────────────────────────────────────────────
    "host.title": {
        "en": "HOST GAME",
        "tr": "OYUN KUR",
    },
    "host.new_game": {
        "en": "New game",
        "tr": "Yeni oyun",
    },
    "host.saved_lan_games": {
        "en": "Saved LAN games:",
        "tr": "Kaydedilmiş LAN oyunları:",
    },
    "host.enter_game_name": {
        "en": "Enter a game name (or press Enter to start fresh): ",
        "tr": "Oyun adı girin (yeni oyun için Enter'a basın): ",
    },
    "host.no_save_found": {
        "en": "No save found for '{name}'. Starting a new game.",
        "tr": "'{name}' için kayıt bulunamadı. Yeni oyun başlatılıyor.",
    },
    "host.game_name_label": {
        "en": "Game name: ",
        "tr": "Oyun adı: ",
    },
    "host.your_ip": {
        "en": "\nYour IP address : ",
        "tr": "\nIP adresin: ",
    },
    "host.listening": {
        "en": "Listening on port {port}...",
        "tr": "{port} portunda dinleniyor...",
    },
    "host.waiting": {
        "en": "Waiting for opponent to connect...\n",
        "tr": "Rakip bekleniyor...\n",
    },
    "host.opponent_connected": {
        "en": "Opponent connected from {ip}!\n",
        "tr": "{ip} adresinden rakip bağlandı!\n",
    },
    "host.resuming": {
        "en": "Resuming '{name}'...",
        "tr": "'{name}' devam ettiriliyor...",
    },
    # ── Match / in-game ───────────────────────────────────────────────────
    "match.your_turn": {
        "en": "Your turn.",
        "tr": "Senin sıran.",
    },
    "match.opponent_turn": {
        "en": "{name}'s turn.",
        "tr": "{name}'in sırası.",
    },
    "match.no_valid_moves": {
        "en": "No valid moves. Turn skipped.",
        "tr": "Geçerli hamle yok. Tur atlandı.",
    },
    "match.waiting_opponent": {
        "en": "Waiting for opponent to move...",
        "tr": "Rakibin hamlesi bekleniyor...",
    },
    "match.opponent_disconnected": {
        "en": "\nOpponent disconnected.",
        "tr": "\nRakip bağlantıyı kesti.",
    },
    "match.press_enter_menu": {
        "en": "\nPress Enter to return to the main menu: ",
        "tr": "\nAna menüye dönmek için Enter'a bas: ",
    },
    "match.connecting": {
        "en": "Connecting to {host}:{port}...",
        "tr": "{host}:{port} adresine bağlanılıyor...",
    },
    "match.failed_connect": {
        "en": "Failed to connect to host.",
        "tr": "Sunucuya bağlanılamadı.",
    },
    "match.connected": {
        "en": "Connected!\n",
        "tr": "Bağlandı!\n",
    },
    "match.opponent_turn_anim": {
        "en": "Opponent's turn.",
        "tr": "Rakibin sırası.",
    },
    "match.last_action": {
        "en": "Last action: ",
        "tr": "Son hamle: ",
    },
    "match.save_found": {
        "en": "Save found: ",
        "tr": "Kayıt bulundu: ",
    },
    # ── Board ─────────────────────────────────────────────────────────────
    "board.title": {
        "en": "THE ROYAL GAME OF UR",
        "tr": "UR'UN KRALIYET OYUNU",
    },
    # ── Game utils / move selection ───────────────────────────────────────
    "move.your_options": {
        "en": "Your options:",
        "tr": "Seçeneklerin:",
    },
    "move.off_board": {
        "en": "Off-board",
        "tr": "Tahta dışı",
    },
    "move.finish": {
        "en": "Finish",
        "tr": "Bitiş",
    },
    "move.square": {
        "en": "Square {letter}",
        "tr": "Kare {letter}",
    },
    "move.rosetta_first": {
        "en": "first",
        "tr": "birinci",
    },
    "move.rosetta_middle": {
        "en": "middle",
        "tr": "ortadaki",
    },
    "move.rosetta_last": {
        "en": "last",
        "tr": "sonuncu",
    },
    "move.scores_point": {
        "en": "Scores a point!",
        "tr": "Puan kazanıyor!",
    },
    "move.lands_rosetta": {
        "en": "Lands on Rosetta (Roll again!)",
        "tr": "Rozet (Tekrar at!)",
    },
    "move.captures": {
        "en": "Captures {name}'s piece!",
        "tr": "{name}'in taşını ele geçiriyor!",
    },
    "move.select_prompt": {
        "en": "\nSelect a piece to move (1-7)",
        "tr": "\nHareket ettirilecek taşı seç (1-7)",
    },
    "move.select_prompt_default": {
        "en": " [Enter for {id}]: ",
        "tr": " [Enter ile {id}]: ",
    },
    "move.select_prompt_end": {
        "en": ": ",
        "tr": ": ",
    },
    "move.invalid_choice": {
        "en": "Invalid choice. That piece cannot move right now.",
        "tr": "Geçersiz seçim. Bu taş şu an hareket edemiyor.",
    },
    "move.invalid_number": {
        "en": "Please enter a valid piece number.",
        "tr": "Lütfen geçerli bir taş numarası girin.",
    },
    # ── Action log ────────────────────────────────────────────────────────
    "action.game_started": {
        "en": "Game started.",
        "tr": "Oyun başladı.",
    },
    "action.you": {
        "en": "You",
        "tr": "Sen",
    },
    "action.rosetta_target": {
        "en": "the {label}",
        "tr": "{label}",
    },
    "action.skipped": {
        "en": "{subject} rolled {roll} and had no moves.",
        "tr": "{roll} — {subject} hamle yapamadı.",
    },
    "action.skipped_you": {
        "en": "{subject} rolled {roll} and had no moves.",
        "tr": "{roll} — hamle yapamadın.",
    },
    "action.scored_you": {
        "en": "{subject} rolled {roll} and piece {piece} scored!",
        "tr": "{roll} — {piece} taşınla puan kazandın!",
    },
    "action.scored_opp": {
        "en": "{subject} rolled {roll} and scored a piece!",
        "tr": "{roll} — {subject} bir taşla puan yaptı!",
    },
    "action.moved_you": {
        "en": "{subject} rolled {roll} and moved piece {piece} to {target}.",
        "tr": "{roll} — {piece} taşını {target} üzerine taşıdın.",
    },
    "action.moved_opp": {
        "en": "{subject} rolled {roll} and moved a piece to {target}.",
        "tr": "{roll} — {subject} bir taşı {target} üzerine taşıdı.",
    },
    "action.hit_you": {
        "en": "Took one of their pieces!",
        "tr": "Rakip taşı geri gönderildi!",
    },
    "action.hit_opp": {
        "en": "Took out one of your pieces!",
        "tr": "Taşın geri gönderildi!",
    },
    "action.rosetta_you": {
        "en": "It is your turn again!",
        "tr": "Tekrar senin sıran!",
    },
    "action.rosetta_opp": {
        "en": "It is their turn again!",
        "tr": "Tekrar onların sırası!",
    },
    # ── Language menu ─────────────────────────────────────────────────────
    "lang.title": {
        "en": "SELECT LANGUAGE",
        "tr": "DİL SEÇ",
    },
    "lang.english": {
        "en": "English",
        "tr": "İngilizce",
    },
    "lang.turkish": {
        "en": "Turkish",
        "tr": "Türkçe",
    },
    # ── Player names ──────────────────────────────────────────────────────
    "player.you": {
        "en": "You",
        "tr": "Sen",
    },
    "player.opponent": {
        "en": "Opponent",
        "tr": "Rakip",
    },
}

LANGUAGES: dict[str, str] = {
    "en": "English",
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
