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
        "en": "How to Play",
        "tr": "Nasıl Oynanır",
    },
    "menu.language": {
        "en": "Change Language",
        "tr": "Dili değiştir",
    },
    "menu.quit": {
        "en": "Quit to Desktop",
        "tr": "Çıkış",
    },
    "menu.back": {
        "en": "Back",
        "tr": "Geri",
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
        "tr": "Sıradaki oyuncu:{name}",
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
        "en": " [ Enter for {id} ]: ",
        "tr": " [ Enter ile {id} ]: ",
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
    # ── Interactive Tutorial ──────────────────────────────────────────────
    "tuto.intro": {
        "en": "Welcome to {bold}THE ROYAL GAME OF UR!{reset}\n\nOne of the oldest board games ever discovered.\n\n{bold}The goal:{reset} move all 7 of your pieces off the board before your opponent.",
        "tr": "{bold}UR'UN KRALIYET OYUNU{reset}'na hoş geldin!\n\nKeşfedilen en eski masa oyunlarından biri.\n\n{bold}Amaç:{reset} 7 taşını rakibinden önce tahtadan çıkar.",
    },
    "tuto.board_title": {
        "en": "THE BOARD",
        "tr": "TAHTA",
    },
    "tuto.path_p1": {
        "en": "You will play with numbered pieces in cyan from ({p1}①{reset} to {p1}⑦{reset}).",
        "tr": "Sen ({p1}①{reset} ile {p1}⑦{reset} arasında) numaralı mavi taşlarla oynayacaksın.",
    },
    "tuto.path_p2": {
        "en": "Your opponent is {p2_name}, she has small red ({p2}●{reset}) dots.",
        "tr": "Rakibin {p2_name}, onun taşları ise küçük kırmızı ({p2}●{reset}) daireler.",
    },
    "tuto.dice_explainer": {
        "en": "Each turn you flip 4 coins — heads or tails — giving a result between 0 and 4.\n\nEvery outcome is possible — let's see all of them.",
        "tr": "Her turda 4 para atarsın — yazı veya tura — sonuç 0 ile 4 arasında olur.\n\nHer sonuç mümkün — hepsine bakalım.",
    },    "tuto.dice_explainer": {
        "en": "Each turn you flip 4 coins — heads or tails — giving a result between 0 and 4.\n\nEvery outcome is possible — let's see all of them.",
        "tr": "Her turda 4 para atarsın — yazı veya tura — sonuç 0 ile 4 arasında olur.\n\nHer sonuç mümkün — hepsine bakalım.",
    },
    "tuto.dice_demo_result": {
        "en": "→  {roll}",
        "tr": "→  {roll}",
    },
    "tuto.step1.hint": {
        "en": "STEP 1 — ENTERING THE BOARD\nYou flipped a {roll}. Move piece {p1}①{reset} from the waiting area onto the board.",
        "tr": "ADIM 1 — TAHTAYA GİRİŞ\n{roll} attın. {p1}①{reset} taşını bekleme alanından tahtaya taşı.",
    },
    "tuto.step1": {
        "en": "Piece {piece} is now on the board.",
        "tr": "{piece} taşı artık tahtada.",
    },
    "tuto.step2.hint": {
        "en": "STEP 2 — OPPONENT'S TURN\n{p2_name} rolled one and she will move one of her piece to square a",
        "tr": "ADIM 2 — RAKİBİN SIRASI\n{p2_name} bir attı ve taşlarından birini a karesine taşıyacak.",
    },
    "tuto.step2": {
        "en": "{p2_name} moved a piece onto the board.",
        "tr": "{p2_name} bir taşı tahtaya taşıdı.",
    },
    "tuto.step3.hint": {
        "en": "STEP 3 — THE ROSETTA\nYou rolled a {roll}. Move piece {p1}①{reset} — it will land on a {rosetta}✿ Rosetta{reset}.\nRosettas grant an extra turn and protect your piece from capture!",
        "tr": "ADIM 3 — ROZET\n{roll} attın. {p1}①{reset} taşını hareket ettir — {rosetta}✿ Rozet{reset}'e inecek.\nRozetler ekstra tur kazandırır ve taşını ele geçirilmekten korur!",
    },
    "tuto.step3": {
        "en": "You landed on a {rosetta}✿ Rosetta{reset} — you get another turn!",
        "tr": "{rosetta}✿ Rozet{reset}'e indin — bir tur daha kazandın!",
    },
    "tuto.step4.hint": {
        "en": "STEP 4 — EXTRA TURN\nThe Rosetta grants you another roll. You rolled {roll}.\nYou have multiple pieces that can move — type {bold}help{reset} to see your options, then pick a piece.",
        "tr": "ADIM 4 — EKSTRİ TUR\nRozet sana bir tur daha veriyor. {roll} attın.\nHareket ettirebileceğin birden fazla taşın var — seçeneklerini görmek için {bold}help{reset} yaz, sonra bir taş seç.",
    },
    "tuto.step4": {
        "en": "Piece {piece} advanced. The extra turn is done.",
        "tr": "{piece} taşı ilerledi. Ekstra tur bitti.",
    },
    "tuto.scene5": {
        "en": "Nice work so far. To show you capturing, let's fast-forward to a position where your piece can take one of {p2_name}'s.",
        "tr": "Güzel gidiyor. Ele geçirmeyi göstermek için, taşının {p2_name}'ninkini alabileceği bir konuma atlayalım.",
    },
    "tuto.scene6": {
        "en": "Now let's look at the safe haven rule. We'll set up a position where {p2_name} has a piece on the central {rosetta}✿ Rosetta{reset}.",
        "tr": "Şimdi güvenli liman kuralına bakalım. {p2_name}'nin merkezi {rosetta}✿ Rozet{reset}'te taşı olduğu bir konum kuralım.",
    },
    "tuto.scene7": {
        "en": "Last rule: scoring. Let's place your piece one roll away from the finish.",
        "tr": "Son kural: puan kazanma. Taşını bitişe bir hamle kala koyalım.",
    },
    "tuto.step5.hint": {
        "en": "STEP 5 — CAPTURING\nYou rolled {roll}. Move piece {p1}①{reset} — it will land on {p2_name}'s piece in the shared zone!\nCapturing sends their piece back to the waiting area.\n\n(You have other pieces that could move, but for this demo only {p1}①{reset} is shown.)",
        "tr": "ADIM 5 — ELE GEÇİRME\n{roll} attın. {p1}①{reset} taşını hareket ettir — ortak bölgede {p2_name}'nin taşına inecek!\nEle geçirmek rakibin taşını bekleme alanına geri gönderir.\n\n(Hareket ettirebileceğin başka taşlar da var, ancak bu demo için yalnızca {p1}①{reset} gösteriliyor.)",
    },
    "tuto.step5": {
        "en": "You captured {p2_name}'s piece! It is sent back to the waiting area.",
        "tr": "{p2_name}'nin taşını ele geçirdin! Bekleme alanına geri döndü.",
    },
    "tuto.step6.hint": {
        "en": "STEP 6 — SAFE HAVEN\nSee {p2_name}'s {rosetta}●{reset} yellow piece on the central {rosetta}✿ Rosetta{reset}? Yellow means it is on a Rosetta and completely safe — it cannot be captured.\nYour piece {p1}①{reset} is right next to it but cannot land there. You rolled {roll} — only your other piece can move.",
        "tr": "ADIM 6 — GÜVENLİ LİMAN\n{p2_name}'nin merkezi {rosetta}✿ Rozet{reset}'teki {rosetta}●{reset} sarı taşını görüyor musun? Sarı renk, Rozet'te olduğu ve tamamen güvende olduğu anlamına gelir — ele geçirilemez.\n{p1}①{reset} taşın tam yanında ama oraya inemez. {roll} attın — sadece diğer taşın hareket edebilir.",
    },
    "tuto.step6": {
        "en": "Piece {piece} moved. Piece {p1}①{reset} was blocked — you cannot capture a piece sitting on the central {rosetta}✿ Rosetta{reset}.",
        "tr": "{piece} taşı hareket etti. {p1}①{reset} taşı engellendi — merkezi {rosetta}✿ Rozet{reset}'teki bir taşı ele geçiremezsin.",
    },
    "tuto.step7.hint": {
        "en": "STEP 7 — SCORING\nTo score, a piece must land exactly on the finish with the right roll. No overshooting.\nYou rolled {roll}. Move piece {p1}①{reset} off the board!",
        "tr": "ADIM 7 — PUAN KAZANMA\nPuan kazanmak için taşın doğru zarla tam olarak bitişe inmesi gerekir. Daha yüksek bir zarla geçemezsin.\n{roll} attın. {p1}①{reset} taşını tahtadan çıkar!",
    },
    "tuto.step7": {
        "en": "Piece {piece} scored!",
        "tr": "{piece} taşı puan yaptı!",
    },
    "tuto.outro": {
        "en": "Well played! That is everything you need to know.\nThe first player to move all 7 pieces off the board wins.",
        "tr": "Güzel oynadın! Bilmen gereken her şey bu kadar.\nTüm 7 taşını tahtadan ilk çıkaran kazanır.",
    },
    "tuto.press_enter": {
        "en": "Press {bold}Enter{reset} to continue...",
        "tr": "Devam etmek için {bold}Enter{reset}'a bas...",
    },
    "tuto.title": {
        "en": "HOW TO PLAY",
        "tr": "NASIL OYNANIR",
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
