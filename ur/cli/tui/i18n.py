"""
Internationalisation support for the Royal Game of Ur CLI.

Usage:
    from ur.cli.i18n import t, set_language, LANGUAGES

    t("key")          # returns translated string for current language
    set_language("de")  # switch to German
"""

from __future__ import annotations

_STRINGS: dict[str, dict[str, str]] = {
    "new_game": {
        "en": "New Game",
        "tr": "Yeni Oyun",
    },

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
        "en": "  (Use arrow keys to select, Enter to confirm, 'Q' to go back)",
        "tr": "  (Seçmek için yön tuşlarını, onaylamak için Enter'ı, dönmek için 'Q'yu kullanın)",
    },
    "nav.ingame_commands_hint": {
        "en": "  (possible commands: menu, quit, help)",
        "tr": "  (verilebilecek komutlar: menu, quit, help)",
    },
    "nav.ingame_help_open_hint": {
        "en": "  (commands: back, menu, quit)",
        "tr": "  (commands: back, menu, quit)",
    },
    # ── Main menu ────────────────────────────────────────────────────────
    "menu.single_player": {
        "en": "Single Player",
        "tr": "Tek Oyuncu",
    },
    "menu.multi_player": {
        "en": "Multi Player",
        "tr": "Çok Oyuncu",
    },
    "menu.join": {
        "en": "Join Game",
        "tr": "Oyuna Katıl",
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
        "en": "Quit",
        "tr": "Çıkış",
    },
    "menu.back": {
        "en": "Back",
        "tr": "Geri",
    },
    # ── Bot selection ─────────────────────────────────────────────────────
    "bot.select_title": {
        "en": "SELECT OPPONENT",
        "tr": "RAKİP SEÇ",
    },
    "bot.random": {
        "en": "RandomBot                                       Easy",
        "tr": "RandomBot                                      Kolay",
    },
    "bot.greedy": {
        "en": "GreedyBot                                     Medium",
        "tr": "GreedyBot                                       Orta",
    },
    "bot.strategic": {
        "en": "StrategicBot                                    Hard",
        "tr": "StrategicBot                                     Zor",
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
    "match.no_valid_moves": {
        "en": "No valid moves. Turn skipped.",
        "tr": "Geçerli hamle yok. Tur atlandı.",
    },
    "match.waiting_opponent": {
        "en": "Waiting for opponent to move...",
        "tr": "Rakibin hamlesi bekleniyor...",
    },
    "match.disconnected": {
        "en": "\nDisconnected.",
        "tr": "\nBağlantı koptu.",
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
        "en": "\nSelect a piece to move",
        "tr": "\nHareket ettirilecek taşı seç",
    },
    "move.select_prompt_default": {
        "en": " [ Enter for {id} ]: ",
        "tr": " [ {id} için Enter ]: ",
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
        "en": "Welcome to {bold}THE ROYAL GAME OF UR{reset}!\n\nOne of the oldest board games ever discovered.\n\n{bold}Goal:{reset} move all 7 pieces off the board\nbefore your opponent does.",
        "tr": "{bold}UR'UN KRALIYET OYUNU{reset}'na hoş geldin!\n\nKeşfedilen en eski masa oyunlarından biri.\n\n{bold}Amaç:{reset} 7 taşını rakibinden önce\ntahtadan çıkar.",
    },
    "tuto.board_title": {
        "en": "THE BOARD",
        "tr": "TAHTA",
    },
    "tuto.path_p1": {
        "en": "Your pieces ({p1}①{reset} to {p1}⑦{reset}) are in cyan.",
        "tr": "Taşların ({p1}①{reset} ile {p1}⑦{reset}) mavi renkte.",
    },
    "tuto.path_p2": {
        "en": "{p2_name} plays with red ({p2}●{reset}) dots.",
        "tr": "{p2_name} kırmızı ({p2}●{reset}) taşlarla oynuyor.",
    },
    "tuto.dice_explainer": {
        "en": "Each turn, flip 4 coins to get a\nresult from 0 to 4.\n\nEvery outcome is possible —\nlet's see all of them.",
        "tr": "Her turda 4 para at — sonuç\n0 ile 4 arasında olur.\n\nHer sonuç mümkün —\nhepsine bakalım.",
    },
    "tuto.dice_demo_result": {
        "en": "→  {roll}",
        "tr": "→  {roll}",
    },
    "tuto.step1.hint": {
        "en": "STEP 1 — ENTERING THE BOARD\nYou flipped {roll}. Move {p1}①{reset} onto the board.",
        "tr": "ADIM 1 — TAHTAYA GİRİŞ\n{roll} attın. {p1}①{reset} taşını tahtaya taşı.",
    },
    "tuto.step1": {
        "en": "Piece {piece} is now on the board.",
        "tr": "{piece} taşı artık tahtada.",
    },
    "tuto.step2.hint": {
        "en": "STEP 2 — OPPONENT'S TURN\n{p2_name} rolls 1 and moves a piece to square a.",
        "tr": "ADIM 2 — RAKİBİN SIRASI\n{p2_name} 1 attı ve bir taşı a karesine taşıyor.",
    },
    "tuto.step2": {
        "en": "{p2_name} moved a piece onto the board.",
        "tr": "{p2_name} bir taşı tahtaya taşıdı.",
    },
    "tuto.step3.hint": {
        "en": "STEP 3 — THE ROSETTA\nYou rolled {roll}. Move {p1}①{reset} —\nit lands on a {rosetta}✿ Rosetta{reset}!\nRosettas give an extra turn and\nprotect your piece from capture.",
        "tr": "ADIM 3 — ROZET\n{roll} attın. {p1}①{reset} taşını hareket ettir —\n{rosetta}✿ Rozet{reset}'e inecek!\nRozetler ekstra tur kazandırır ve\ntaşını ele geçirilmekten korur.",
    },
    "tuto.step3": {
        "en": "You landed on {rosetta}✿ Rosetta{reset} — extra turn!",
        "tr": "{rosetta}✿ Rozet{reset}'e indin — bir tur daha!",
    },
    "tuto.step4.hint": {
        "en": "STEP 4 — EXTRA TURN\nThe Rosetta gives another roll.\nYou rolled {roll}. Pick any piece!\nType {bold}help{reset} to see your options.",
        "tr": "ADIM 4 — EKSTRİ TUR\nRozet sana bir tur daha veriyor.\n{roll} attın. İstediğin taşı seç!\nSeçenekler için {bold}help{reset} yaz.",
    },
    "tuto.step4": {
        "en": "Piece {piece} advanced. Extra turn done.",
        "tr": "{piece} taşı ilerledi. Ekstra tur bitti.",
    },
    "tuto.scene5": {
        "en": "Nice work! Let's skip ahead to show\ncapturing — your piece can take\none of {p2_name}'s.",
        "tr": "Güzel! Ele geçirmeyi göstermek için\nilerleyelim — taşın {p2_name}'ninkini\nalabilecek.",
    },
    "tuto.scene6": {
        "en": "Now: the safe haven rule.\n{p2_name} has a piece on the\ncentral {rosetta}✿ Rosetta{reset}.",
        "tr": "Şimdi: güvenli liman kuralı.\n{p2_name}'nin merkezi {rosetta}✿ Rozet{reset}'te\nbir taşı var.",
    },
    "tuto.scene7": {
        "en": "Last rule: scoring!\nYour piece is one roll from the finish.",
        "tr": "Son kural: puan kazanma!\nTaşın bitişe bir hamle uzakta.",
    },
    "tuto.step5.hint": {
        "en": "STEP 5 — CAPTURING\nYou rolled {roll}. Move {p1}①{reset} to\ncapture {p2_name}'s piece!\nThis sends their piece back to start.",
        "tr": "ADIM 5 — ELE GEÇİRME\n{roll} attın. {p1}①{reset} taşını hareket ettir —\n{p2_name}'nin taşını ele geçirecek!\nEle geçirilen taş başa döner.",
    },
    "tuto.step5": {
        "en": "You captured {p2_name}'s piece!\nSent back to the waiting area.",
        "tr": "{p2_name}'nin taşını ele geçirdin!\nBekleme alanına geri döndü.",
    },
    "tuto.step6.hint": {
        "en": "STEP 6 — SAFE HAVEN\n{p2_name}'s {p2_rosetta}●{reset} sits on the central {rosetta}✿ Rosetta{reset}.\nA piece on a Rosetta is safe —\nit cannot be captured.\nYou rolled {roll}. {p1}①{reset} is blocked.\nOnly your other piece can move.",
        "tr": "ADIM 6 — GÜVENLİ LİMAN\n{p2_name}'nin {p2_rosetta}●{reset} taşı merkezi {rosetta}✿ Rozet{reset}'te.\nRozet'teki bir taş güvende —\nele geçirilemez.\n{roll} attın. {p1}①{reset} engellenmiş.\nSadece diğer taşın hareket edebilir.",
    },
    "tuto.step6": {
        "en": "{piece} moved. {p1}①{reset} was blocked.\nCannot capture on a {rosetta}✿ Rosetta{reset}.",
        "tr": "{piece} hareket etti. {p1}①{reset} engellendi.\n{rosetta}✿ Rozet{reset}'teki taş ele geçirilemez.",
    },
    "tuto.step7.hint": {
        "en": "STEP 7 — SCORING\nTo score, land exactly on the finish.\nRolling too high won't count.\nYou rolled {roll}. Move {p1}①{reset} off!",
        "tr": "ADIM 7 — PUAN KAZANMA\nPuan için tam olarak bitişe inmek gerekir.\nFazla yüksek atmak geçmez.\n{roll} attın. {p1}①{reset} taşını çıkar!",
    },
    "tuto.step7": {
        "en": "Piece {piece} scored a point!",
        "tr": "{piece} taşı puan yaptı!",
    },
    "tuto.outro": {
        "en": "Well played! That's all you need to know.\n\nFirst player to score all 7 pieces wins.",
        "tr": "Güzel oynadın! Bilmen gereken her şey bu.\n\nTüm 7 taşını ilk çıkaran kazanır.",
    },
    "tuto.press_enter": {
        "en": "Press {bold}Enter{reset} to continue...",
        "tr": "Devam etmek için {bold}Enter{reset}'a bas...",
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
