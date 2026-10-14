import _tkinter
import ast
import hashlib
import os
import tkinter as tk
from tkinter import ttk
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from playwright.sync_api import sync_playwright
import secrets
import time
# Eigene Krypto-Funktionen importieren
from Verschlüsseln import decrypt, encrypt

from FeldFinden import find_login_fields
# Globale Variablen im RAM vorbereiten
SALT = None
MASTER_HASH = None
KLARTEXT_MASTER = ""  # Hier merken wir uns das eingegebene PW für die Verschlüsselung
Alphabet =["a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z",
           "A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z",
           "1","2","3","4","5","6","7","8","9","0","!","§","$","%","&","/",")","(","=","?","ß","+","#","~",]
großbuchstaben = ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"]
kleinbuchstaben = ["a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z"]
sonderzeichen = ["!","§","$","%","&","/",")","(","=","?","ß","+","#","~"]

großbuchstaben = set(großbuchstaben)
kleinbuchstaben = set(kleinbuchstaben)
sonderzeichen = set(sonderzeichen)
def act():
    """Registrierungs-Logik: Wird nur aufgerufen, wenn die Datei leer ist."""
    p = eingabe.get().strip()
    if not p:
        return

    keinGroßbuuchstabe = True
    keinKleinbuchstabe = True
    keinSonderzeichen = True
    for i in p:
        if i in großbuchstaben:
            keinGroßbuuchstabe = False
        if i in kleinbuchstaben:
            keinKleinbuchstabe = False
        if i in sonderzeichen:
            keinSonderzeichen = False
        if not keinKleinbuchstabe and not keinGroßbuuchstabe and not keinSonderzeichen:
            break
    if  keinKleinbuchstabe or  keinGroßbuuchstabe or  keinSonderzeichen:
        if keinGroßbuuchstabe:
            labelR.config(text="Passwort hat keine Großbuchstaben", fg="red")
            time.sleep(1)
        if keinKleinbuchstabe:
            labelR.config(text="Passwort hat keine Kleinbuchstaben", fg="red")
            time.sleep(1)
        if keinSonderzeichen:
            labelR.config(text="Passwort benötigt Sonderzeichen", fg="red")
        return

    if len(p) < 12:
        labelR.config(text="Passwort ist zu kurz. Mindestens 12 Zeichen", fg="red")
        return

    zufall_salt = os.urandom(16)
    hash_wert = hashlib.pbkdf2_hmac("sha256", p.encode(), zufall_salt, 100000)

    with open("passwörter.txt", "w") as f:
        f.write(hash_wert.hex() + "\n")
        f.write(zufall_salt.hex() + "\n")

    root0.destroy()

def check():
    """Login-Logik: Überprüft das Master-Passwort."""
    global KLARTEXT_MASTER
    eingabe_text = eingabe.get().strip()

    # Hash des eingegebenen Passworts berechnen
    text_hash = hashlib.pbkdf2_hmac("sha256", eingabe_text.encode(), SALT, 100000)

    # Mit dem in der Datei gespeicherten Hash vergleichen
    if MASTER_HASH == text_hash.hex():
        KLARTEXT_MASTER = eingabe_text  # WICHTIG: Passwort im RAM für AES merken!

        root.destroy()  # Login-Fenster schließen
        open_main_window()  # Hauptfenster öffnen
    else:
        label2.config(text="Passwort ist falsch", fg="red")


def open_main_window():
    """Öffnet das Hauptfenster mit der Passwort-Liste."""
    root1 = tk.Tk()
    root1.title("Passwort Manager")
    root1.geometry("400x600")

    label_titel = tk.Label(
        root1, text="Deine Logins:", font=("Arial", 14, "bold")
    )
    label_titel.pack(pady=10)

    # Buttons für existierende Passwörter bauen
    if os.path.exists("Namen.txt"):
        with open("Namen.txt", "r") as n:
            for zeile in n:
                var = zeile.strip()
                if var:
                    btn = tk.Button(
                        root1, text=var, command=lambda i=var: enter(i)
                    )
                    btn.pack(fill="x", padx=20, pady=2)

    button_neu = tk.Button(
        root1,
        text="➕ Füge ein Passwort hinzu",
        command=lambda: newPassword(root1),
        bg="green",
        fg="white",
    )
    button_neu.pack(pady=20)

    root1.mainloop()


def enter(name):
    """Liest die Daten aus und startet Playwright zur Anmeldung."""
    global KLARTEXT_MASTER, SALT

    with open("passwörter.txt", "r") as e:
        # Überspringe die ersten beiden Zeilen (Master-Hash und Salt)
        e.readline()
        e.readline()

        # Suche den passenden Eintrag
        while True:
            zeile = e.readline()
            if not zeile:
                print("Eintrag nicht gefunden.")
                return
            if zeile.strip() == name.strip():
                break

        seite = e.readline().strip()
        email = e.readline().strip()
        line = e.readline().strip()

    encrypted_data = ast.literal_eval(line)

    # Der AES-Schlüssel wird LIVE aus dem echten Master-Passwort berechnet
    key = hashlib.pbkdf2_hmac("sha256", KLARTEXT_MASTER.encode(), SALT, 100000)

    # Entschlüsseln
    passwort = decrypt(encrypted_data, key)

    # Playwright Automation
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(seite)
        ufield, pfield = find_login_fields(page)
        if ufield and pfield:
            ufield.fill(email)
            pfield.fill(passwort)
        # Hält den Browser offen, bis du im Terminal Enter drückst
        input("Drücke Enter im Terminal, um den Browser zu schließen...")


def newPassword(parent_window):
    """Öffnet ein Unterfenster (Toplevel), um ein neues Passwort anzulegen."""
    # Toplevel statt tk.Tk(), damit es kein zweites Hauptfenster gibt
    root2 = tk.Toplevel(parent_window)
    root2.title("Neues Passwort")

    tk.Label(root2, text="Name (z.B. Google):").pack()
    Name = tk.Entry(root2)
    Name.pack()

    tk.Label(root2, text="Webseite (URL):").pack()
    Site = tk.Entry(root2)
    Site.pack()

    tk.Label(root2, text="Email / Username:").pack()
    Email = tk.Entry(root2)
    Email.pack()

    tk.Label(root2, text="Passwort:").pack()
    Pass = tk.Entry(root2, show="*")
    Pass.pack()


    def hinzu():
        global KLARTEXT_MASTER, SALT

        # Den AES-Schlüssel LIVE aus dem Master-Passwort generieren
        key = hashlib.pbkdf2_hmac(
            "sha256", KLARTEXT_MASTER.encode(), SALT, 100000
        )

        # Daten mit diesem Schlüssel verschlüsseln
        passwort_encrypted = encrypt(Pass.get(), key)

        # In passwörter.txt anhängen
        with open("passwörter.txt", "a") as nP:
            nP.write(Name.get() + "\n")
            nP.write(Site.get() + "\n")
            nP.write(Email.get() + "\n")
            nP.write(str(passwort_encrypted) + "\n")

        # In Namen.txt anhängen (für die GUI-Buttons)
        with open("Namen.txt", "a") as N:
            N.write(Name.get() + "\n")

        root2.destroy()
        # Hauptfenster neu laden, um den neuen Button anzuzeigen
        parent_window.destroy()
        open_main_window()
    def passwortGenerieren():
        createdPassword = ""
        for i in range(30):
            posi = secrets.randbelow(len(Alphabet))
            createdPassword += Alphabet[posi]
        print(createdPassword)
        Pass.insert(0, createdPassword)
        createdPassword = ""

    tk.Button(root2, text="Passwort erstellen", command=passwortGenerieren).pack()
    tk.Button(root2, text="Speichern", command=hinzu).pack(pady=10)



# =====================================================================
# PROGRAMMSTART & INITIALISIERUNG
# =====================================================================

# 1. Prüfen, ob die Datei existiert. Falls nicht, leer anlegen.
if not os.path.exists("passwörter.txt"):
    with open("passwörter.txt", "w") as f:
        pass

# 2. Prüfen, ob eine Registrierung notwendig ist
with open("passwörter.txt", "r") as f:
    erste_zeile = f.readline()

    if erste_zeile == "":
        # Registrierungs-Fenster öffnen
        root0 = tk.Tk()
        root0.geometry("400x200")
        root0.title("Registrierung")
        tk.Label(
            text="Ersteinrichtung: Bitte erstelle ein Master-Passwort"
        ).pack(pady=10)
        eingabe = tk.Entry(root0, show="*")
        eingabe.pack(pady=5)
        labelR = tk.Label(root0, text="")
        labelR.pack()
        tk.Button(root0, text="Registrieren", command=act).pack(pady=10)
        root0.mainloop()

# 3. Lade die Master-Krypto-Daten aus der Datei für die laufende Sitzung
with open("passwörter.txt", "r") as f:
    MASTER_HASH = f.readline().strip()
    salt_hex = f.readline().strip()
    SALT = bytes.fromhex(salt_hex)

# 4. Normales Login-Fenster anzeigen

root = tk.Tk()
if MASTER_HASH =="":
    root.destroy()
root.geometry("600x600")
root.title("Login")

label1 = tk.Label(text="Bitte gib dein Master-Passwort ein:")
label1.pack(pady=10)
eingabe = tk.Entry(root, show="*")
eingabe.pack(pady=5)

button = tk.Button(root, text="Einloggen", command=check)
button.pack(pady=10)

label2 = tk.Label(text="")
label2.pack()

root.mainloop()
