from aqt import mw
from aqt.qt import *
from anki.hooks import addHook

config = mw.addonManager.getConfig(__name__)

READING_FIELD = config["readingField"]
KANA_FIELD = config["kanaField"]


# ************************************************
#            Kana extraction function            *
# ************************************************
def extract_kana(reading):
    kana = ""
    for c in reading:
        if is_char_kana(c):
            kana += c
    return kana


HIRAGANA_START = 0x3041
HIRAGANA_END = 0x3096
KATAKANA_START = 0x30A1
KATAKANA_END = 0x30FC
KANJI_START = 0x4E00
KANJI_END = 0x9FAF
PROLONGED_SOUND_MARK = 0x30FC

def is_char_kana(char: str = "") -> bool:
    return is_char_hiragana(char) or is_char_katakana(char)


def is_char_hiragana(char: str = "") -> bool:
    if is_char_long_dash(char):
        return True
    return is_char_in_range(char, HIRAGANA_START, HIRAGANA_END)


def is_char_katakana(char: str = "") -> bool:
    if is_char_long_dash(char):
        return True
    return is_char_in_range(char, KATAKANA_START, KATAKANA_END)


def is_char_long_dash(char: str = "") -> bool:
    if is_empty(char):
        return False
    return ord(char[0]) == PROLONGED_SOUND_MARK


def is_empty(text: str) -> bool:
    return (not isinstance(text, str)) or (not text)


def is_char_in_range(char: str = "", start: int = 0, end: int = 0) -> bool:
    """Tests if a character is in a Unicode range."""
    if is_empty(char):
        return False
    code = ord(char[0])
    return start <= code <= end


# ************************************************
#                  Interface                     *
# ************************************************


# add menu entry to browser window
def setup_browser_menu(browser):
    a = QAction("Add Kana", browser)
    a.triggered.connect(lambda: extract(browser.selectedNotes()))
    browser.form.menuEdit.addSeparator()
    browser.form.menuEdit.addAction(a)


# ************************************************
#              Hooked functions                  *
# ************************************************

# extracts kana reading from reading field and add it as its own field
def extract(nids):
    mw.checkpoint("Add Kana")
    mw.progress.start()
    for nid in nids:
        note = mw.col.get_note(nid)
        kana = extract_kana(note[READING_FIELD])

        try:
            note[KANA_FIELD] = kana
        except KeyError:
            pass

        note.flush()

    mw.progress.finish()
    mw.reset()


# ************************************************
#                    Main                        *
# ************************************************
addHook("browser.setupMenus", setup_browser_menu)
