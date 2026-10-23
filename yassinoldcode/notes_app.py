import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

DB = r"yassinoldcode\notes.db"

# ---------- Base de données ----------
def requete(sql, params=(), ecrire=False):
    con = sqlite3.connect(DB)
    res = con.execute(sql, params).fetchall()
    if ecrire:
        con.commit()
    con.close()
    return res


def init_db():
    requete("""CREATE TABLE IF NOT EXISTS users(
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   nom TEXT, username TEXT UNIQUE, password TEXT, role TEXT)""", ecrire=True)
    requete("""CREATE TABLE IF NOT EXISTS notes(
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   etudiant_id INTEGER, matiere TEXT, note REAL)""", ecrire=True)

    if not requete("SELECT id FROM users"):  # comptes de test
        for nom, user, role in [("Prof. Alami", "prof", "professeur"),
                                ("Sara Benali", "sara", "etudiant"),
                                ("Omar Idrissi", "omar", "etudiant")]:
            requete("INSERT INTO users(nom, username, password, role) VALUES(?,?,?,?)",
                    (nom, user, "1234", role), ecrire=True)
        for etu_id, matiere, note in [(2, "Maths", 15), (2, "Physique", 13),
                                      (3, "Maths", 11), (3, "Physique", 14)]:
            requete("INSERT INTO notes(etudiant_id, matiere, note) VALUES(?,?,?)",
                    (etu_id, matiere, note), ecrire=True)


def verifier_login(username, mdp):
    res = requete("SELECT id, nom, role FROM users WHERE username=? AND password=?",
                  (username, mdp))
    return res[0] if res else None


def notes_etudiant(etudiant_id):
    return requete("SELECT matiere, note FROM notes WHERE etudiant_id=?", (etudiant_id,))


def toutes_les_notes():
    return requete("""SELECT notes.id, users.nom, notes.matiere, notes.note
                      FROM notes JOIN users ON users.id = notes.etudiant_id""")


def modifier_note(note_id, nouvelle_note):
    requete("UPDATE notes SET note=? WHERE id=?", (nouvelle_note, note_id), ecrire=True)


# ---------- Interface ----------
fen = tk.Tk()
fen.title("Plateforme de notes")
fen.geometry("480x400")


def vider():
    for widget in fen.winfo_children():
        widget.destroy()


def ecran_login():
    vider()
    tk.Label(fen, text="Connexion", font=("Arial", 16)).pack(pady=20)
    tk.Label(fen, text="Identifiant").pack()
    e_user = tk.Entry(fen)
    e_user.pack()
    tk.Label(fen, text="Mot de passe").pack(pady=(10, 0))
    e_mdp = tk.Entry(fen, show="*")
    e_mdp.pack()

    def se_connecter():
        user = verifier_login(e_user.get(), e_mdp.get())
        if user is None:
            messagebox.showerror("Erreur", "Identifiants incorrects")
            return
        id_, nom, role = user
        if role == "etudiant":
            ecran_etudiant(id_, nom)
        else:
            ecran_prof(nom)

    tk.Button(fen, text="Se connecter", command=se_connecter).pack(pady=20)


def ecran_etudiant(etudiant_id, nom):
    vider()
    tk.Label(fen, text=f"Bienvenue {nom}", font=("Arial", 14)).pack(pady=10)

    tab = ttk.Treeview(fen, columns=("matiere", "note"), show="headings", height=8)
    tab.heading("matiere", text="Matière")
    tab.heading("note", text="Note")
    tab.pack(padx=10, pady=10)
    for ligne in notes_etudiant(etudiant_id):
        tab.insert("", "end", values=ligne)

    tk.Button(fen, text="Déconnexion", command=ecran_login).pack(pady=10)


def ecran_prof(nom):
    vider()
    tk.Label(fen, text=f"Professeur : {nom}", font=("Arial", 14)).pack(pady=10)

    tab = ttk.Treeview(fen, columns=("id", "etudiant", "matiere", "note"),
                       show="headings", height=8)
    for col, titre in [("id", "ID"), ("etudiant", "Étudiant"),
                       ("matiere", "Matière"), ("note", "Note")]:
        tab.heading(col, text=titre)
        tab.column(col, width=100)
    tab.pack(padx=10, pady=10)

    def charger():
        tab.delete(*tab.get_children())
        for ligne in toutes_les_notes():
            tab.insert("", "end", values=ligne)

    tk.Label(fen, text="Nouvelle note (0 à 20) :").pack()
    e_note = tk.Entry(fen)
    e_note.pack()

    def modifier():
        selection = tab.selection()
        if not selection:
            messagebox.showwarning("Attention", "Sélectionnez une ligne")
            return
        try:
            valeur = float(e_note.get())
            if not 0 <= valeur <= 20:
                raise ValueError
        except ValueError:
            messagebox.showerror("Erreur", "Entrez une note entre 0 et 20")
            return
        modifier_note(tab.item(selection[0])["values"][0], valeur)
        charger()

    tk.Button(fen, text="Modifier", command=modifier).pack(pady=8)
    tk.Button(fen, text="Déconnexion", command=ecran_login).pack()
    charger()


# ---------- Lancement ----------
init_db()
ecran_login()
fen.mainloop()
