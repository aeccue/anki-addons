import requests
from anki.hooks import addHook
from aqt import mw
from aqt.qt import *

config = mw.addonManager.getConfig(__name__)

KANA_FIELD = config["kanaField"]
KANJI_FIELD = config["kanjiField"]
AUDIO_FIELD = config["audioField"]

AUDIO_SOURCE = "https://assets.languagepod101.com/dictionary/japanese/audiomp3.php?kana={kana}&kanji={kanji}"


# ************************************************
#              Audio lookup function             *
# ************************************************

# gets audio file from online source
def find_audio(kana, kanji):
    resp = requests.get(AUDIO_SOURCE.format(kana=kana, kanji=kanji))
    # ignore audio that says that no audio is currently available (check based on file size)
    if len(resp.content) == 52288:
        raise NoAudioClipFoundException()

    return resp.content


class NoAudioClipFoundException(Exception):
    pass


# ************************************************
#                  Interface                     *
# ************************************************

# add menu entry to browser window
def setup_browser_menu(browser):
    a = QAction("Add Audio", browser)
    a.triggered.connect(lambda: add_audio(browser.selectedNotes()))
    browser.form.menuEdit.addSeparator()
    browser.form.menuEdit.addAction(a)


# ************************************************
#              Hooked functions                  *
# ************************************************

# adds audio to selected notes
def add_audio(nids):
    mw.checkpoint("Add Audio")
    mw.progress.start()

    for nid in nids:
        note = mw.col.get_note(nid)

        try:
            # finds audio, and if found, writes it to file in media directory
            audio = find_audio(note[KANA_FIELD], note[KANJI_FIELD])
            mw.col.media.write_data(f"{nid}.mp3", audio)
        except NoAudioClipFoundException:
            # if no audio is found, add no-audio tag
            note.add_tag("no-audio")
            note.flush()
            continue

        try:
            # writes audio file name to Anki note field
            note[AUDIO_FIELD] = f"[sound:{nid}.mp3]"
        except KeyError:
            pass

        note.flush()

    mw.progress.finish()
    mw.reset()


# ************************************************
#                    Main                        *
# ************************************************
addHook("browser.setupMenus", setup_browser_menu)
