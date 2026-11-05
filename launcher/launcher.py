import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, colorchooser
import subprocess
import json
import os
import platform

CONFIG_FILE = "launcher_config.json"

# ============================================================
# 50 THEMES PRÉDÉFINIS
# ============================================================

THEME_PRESETS = [
    {"name": "Neon Blue",   "bg": "#050608", "panel": "#0b1120", "accent": "#3b82f6", "text": "#e5e7eb"},
    {"name": "Neon Pink",   "bg": "#06040a", "panel": "#1a0b17", "accent": "#ec4899", "text": "#fce7f3"},
    {"name": "Neon Purple", "bg": "#0a0212", "panel": "#150325", "accent": "#a855f7", "text": "#ede9fe"},
    {"name": "Matrix",      "bg": "#000000", "panel": "#001100", "accent": "#00ff41", "text": "#d1ffd7"},
    {"name": "Cyberpunk",   "bg": "#0a0014", "panel": "#140028", "accent": "#f20089", "text": "#ffd6e8"},
    {"name": "Red Hell",    "bg": "#0a0000", "panel": "#200000", "accent": "#ff2d2d", "text": "#ffe5e5"},
    {"name": "Emerald",     "bg": "#00110b", "panel": "#002016", "accent": "#10b981", "text": "#d1fae5"},
    {"name": "Sunset",      "bg": "#120700", "panel": "#2a0f00", "accent": "#fb923c", "text": "#ffedd5"},
    {"name": "Minimal Dark","bg": "#0a0a0a", "panel": "#141414", "accent": "#808080", "text": "#ffffff"},
    {"name": "Space Blue",  "bg": "#030712", "panel": "#0f172a", "accent": "#60a5fa", "text": "#e2e8f0"},
]

extra_colors = [
    "#3b82f6", "#2563eb", "#a855f7", "#22c55e", "#eab308",
    "#ef4444", "#ec4899", "#14b8a6", "#6366f1", "#f97316"
]

while len(THEME_PRESETS) < 50:
    c = extra_colors[len(THEME_PRESETS) % len(extra_colors)]
    THEME_PRESETS.append({
        "name": f"Theme {len(THEME_PRESETS)}",
        "bg": "#050505",
        "panel": "#0f0f0f",
        "accent": c,
        "text": "#e5e5e5"
    })

CUSTOM_THEME = {
    "name": "Custom",
    "bg": "#000000",
    "panel": "#111111",
    "accent": "#00ffff",
    "text": "#ffffff",
}

current_theme_index = 0

# ============================================================
# CONFIG
# ============================================================

def load_config():
    global CUSTOM_THEME, current_theme_index
    if not os.path.exists(CONFIG_FILE):
        return [], [], 1
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        apps = data.get("apps", [])
        groups = data.get("groups", [])
        next_id = data.get("next_id", 1)
        current_theme_index = data.get("theme_index", 0)
        if "custom_theme" in data:
            CUSTOM_THEME.update(data["custom_theme"])
        for app in apps:
            app.setdefault("favorite", False)
            app.setdefault("tags", [])
        return apps, groups, next_id
    except:
        return [], [], 1

def save_config():
    data = {
        "apps": apps,
        "groups": groups,
        "next_id": next_id,
        "theme_index": current_theme_index,
        "custom_theme": CUSTOM_THEME,
    }
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

# ============================================================
# LAUNCH FUNCTION
# ============================================================

def run_program(path):
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    if platform.system() == "Windows":
        os.startfile(path)
    else:
        subprocess.Popen([path])

# ============================================================
# GLOBAL DATA
# ============================================================

apps = []
groups = []
next_id = 1

current_search = ""
current_tag = None
filtered_apps = []
favorite_apps = []

# ============================================================
# SCAN AUTO
# ============================================================

USEFUL_KEYWORDS = [
    "discord", "spotify", "steam", "epic", "riot",
    "chrome", "firefox", "opera", "brave",
    "code", "vscode", "pycharm",
    "minecraft", "roblox", "gta", "fortnite",
]

def auto_scan_apps():
    global apps, next_id

    if platform.system() != "Windows":
        messagebox.showerror("Scan auto", "Windows uniquement")
        return

    user = os.path.expanduser("~")
    roots = [
        r"C:\Program Files",
        r"C:\Program Files (x86)",
        os.path.join(user, "Desktop"),
        os.path.join(user, "AppData", "Local", "Programs"),
        os.path.join(user, "AppData", "Local", "Discord"),
        os.path.join(user, "AppData", "Local", "Microsoft", "WindowsApps"),
    ]

    existing = {a["path"].lower() for a in apps}
    added = 0

    for root in roots:
        if not os.path.isdir(root):
            continue
        for dp, dn, fn in os.walk(root):
            for f in fn:
                lf = f.lower()
                if not (lf.endswith(".exe") or lf.endswith(".bat")):
                    continue
                full = os.path.join(dp, f)
                if full.lower() in existing:
                    continue
                if not any(k in full.lower() for k in USEFUL_KEYWORDS):
                    continue
                apps.append({
                    "id": next_id,
                    "name": os.path.splitext(f)[0],
                    "path": full,
                    "favorite": False,
                    "tags": []
                })
                existing.add(full.lower())
                next_id += 1
                added += 1

    save_config()
    apply_filters()
    messagebox.showinfo("Scan automatique", f"{added} applications trouvées.")

# ============================================================
# APPS MANAGEMENT
# ============================================================

def choose_and_add_app():
    global apps, next_id
    path = filedialog.askopenfilename(
        title="Choisir .exe / .bat",
        filetypes=[("Applications", "*.exe;*.bat"), ("Tous", "*.*")]
    )
    if not path:
        return
    name = simpledialog.askstring("Nom", "Nom de l'application :")
    if not name:
        name = os.path.basename(path)
    apps.append({
        "id": next_id,
        "name": name,
        "path": path,
        "favorite": False,
        "tags": []
    })
    next_id += 1
    save_config()
    apply_filters()

def get_selected_app(lb, src):
    sel = lb.curselection()
    if not sel:
        return None
    i = sel[0]
    if i >= len(src):
        return None
    return src[i]

def delete_selected_app():
    global apps
    app = get_selected_app(apps_listbox, filtered_apps)
    if not app:
        return
    apps = [a for a in apps if a["id"] != app["id"]]
    for g in groups:
        g["app_ids"] = [i for i in g["app_ids"] if i != app["id"]]
    save_config()
    apply_filters()

def delete_multiple_apps():
    global apps
    sel = apps_listbox.curselection()
    if not sel:
        return
    ids = [filtered_apps[i]["id"] for i in sel]
    apps = [a for a in apps if a["id"] not in ids]
    for g in groups:
        g["app_ids"] = [i for i in g["app_ids"] if i not in ids]
    save_config()
    apply_filters()

def toggle_favorite():
    app = get_selected_app(apps_listbox, filtered_apps)
    if not app:
        return
    app["favorite"] = not app["favorite"]
    save_config()
    apply_filters()
    refresh_favorites_list()

def set_tags_for_app():
    app = get_selected_app(apps_listbox, filtered_apps)
    if not app:
        return
    txt = simpledialog.askstring("Tags", "Séparés par virgules :", initialvalue=",".join(app["tags"]))
    if txt is None:
        return
    app["tags"] = [t.strip() for t in txt.split(",") if t.strip()]
    save_config()
    refresh_tags_list()
    apply_filters()

def launch_selected_app():
    app = get_selected_app(apps_listbox, filtered_apps)
    if app:
        run_program(app["path"])

def launch_all_visible():
    for a in filtered_apps:
        try:
            run_program(a["path"])
        except:
            pass
    messagebox.showinfo("Launch All", f"{len(filtered_apps)} applications lancées.")

# ============================================================
# GROUPES
# ============================================================

def refresh_groups_list():
    group_listbox.delete(0, tk.END)
    for g in groups:
        group_listbox.insert(tk.END, g["name"])

def get_selected_group():
    sel = group_listbox.curselection()
    if not sel:
        return None
    return groups[sel[0]]

def create_group():
    name = simpledialog.askstring("Nouveau groupe", "Nom :")
    if not name:
        return
    if any(g["name"] == name for g in groups):
        messagebox.showerror("Erreur", "Nom déjà existant")
        return
    groups.append({"name": name, "app_ids": []})
    save_config()
    refresh_groups_list()

def delete_group():
    g = get_selected_group()
    if not g:
        return
    groups.remove(g)
    save_config()
    refresh_groups_list()

def add_app_to_group():
    g = get_selected_group()
    a = get_selected_app(apps_listbox, filtered_apps)
    if not g or not a:
        return
    if a["id"] not in g["app_ids"]:
        g["app_ids"].append(a["id"])
    save_config()

def remove_app_from_group():
    g = get_selected_group()
    a = get_selected_app(apps_listbox, filtered_apps)
    if not g or not a:
        return
    if a["id"] in g["app_ids"]:
        g["app_ids"].remove(a["id"])
    save_config()

def launch_group():
    g = get_selected_group()
    if not g:
        return
    for idd in g["app_ids"]:
        a = next((x for x in apps if x["id"] == idd), None)
        if a:
            try:
                run_program(a["path"])
            except:
                pass

def add_app_to_group_from_apps():
    """Depuis l'onglet Applications : choisir un groupe et ajouter l'app dedans."""
    app = get_selected_app(apps_listbox, filtered_apps)
    if not app:
        messagebox.showwarning("Groupe", "Sélectionne d'abord une application.")
        return

    if not groups:
        messagebox.showwarning(
            "Groupe",
            "Tu n'as encore aucun groupe.\nCrée un groupe dans l'onglet 'Groupes' d'abord."
        )
        return

    win = tk.Toplevel(root)
    win.title("Choisir un groupe")
    win.geometry("320x260")
    win.transient(root)
    win.grab_set()

    lbl = tk.Label(
        win,
        text=f"Ajouter '{app['name']}' à :",
        font=("Segoe UI", 9, "bold")
    )
    lbl.pack(pady=6)

    lb = tk.Listbox(win)
    for g in groups:
        lb.insert(tk.END, g["name"])
    lb.pack(fill="both", expand=True, padx=10, pady=4)

    def confirm():
        sel = lb.curselection()
        if not sel:
            return
        g = groups[sel[0]]
        if app["id"] not in g["app_ids"]:
            g["app_ids"].append(app["id"])
            save_config()
        win.destroy()
        messagebox.showinfo("Groupe", f"'{app['name']}' a été ajouté à '{g['name']}'.")

    btn_frame = tk.Frame(win)
    btn_frame.pack(pady=8)

    tk.Button(btn_frame, text="OK", command=confirm).pack(side="left", padx=6)
    tk.Button(btn_frame, text="Annuler", command=win.destroy).pack(side="left", padx=6)

# ============================================================
# FAVORIS
# ============================================================

def refresh_favorites_list():
    favorite_apps.clear()
    for a in apps:
        if a.get("favorite"):
            favorite_apps.append(a)
    fav_listbox.delete(0, tk.END)
    for a in favorite_apps:
        fav_listbox.insert(tk.END, a["name"])

def launch_selected_fav():
    sel = fav_listbox.curselection()
    if not sel:
        return
    run_program(favorite_apps[sel[0]]["path"])

# ============================================================
# TAGS + SEARCH
# ============================================================

def refresh_tags_list():
    tag_listbox.delete(0, tk.END)
    tag_listbox.insert(tk.END, "Tous")
    tags = set()
    for a in apps:
        for t in a["tags"]:
            tags.add(t)
    for t in sorted(tags):
        tag_listbox.insert(tk.END, t)

def on_search_change(event=None):
    global current_search
    current_search = search_var.get().lower().strip()
    apply_filters()

def on_tag_select(event=None):
    global current_tag
    sel = tag_listbox.curselection()
    if not sel:
        current_tag = None
    else:
        t = tag_listbox.get(sel[0])
        current_tag = None if t == "Tous" else t
    apply_filters()

def apply_filters():
    global filtered_apps
    s = current_search
    t = current_tag
    def match(a):
        if s and s not in a["name"].lower():
            return False
        if t and t not in a["tags"]:
            return False
        return True
    filtered_apps = [a for a in apps if match(a)]
    apps_listbox.delete(0, tk.END)
    for a in filtered_apps:
        star = "★ " if a["favorite"] else "  "
        apps_listbox.insert(tk.END, star + a["name"])
    refresh_favorites_list()

# ============================================================
# SPOTIFY
# ============================================================

def open_spotify():
    try:
        if platform.system() == "Windows":
            os.startfile("spotify")
        else:
            subprocess.Popen(["spotify"])
    except:
        messagebox.showerror("Spotify", "Impossible d'ouvrir Spotify")

def send_media_key(key):
    if platform.system() != "Windows":
        return
    mapping = {
        "play_pause": "{MEDIA_PLAY_PAUSE}",
        "next": "{MEDIA_NEXT_TRACK}",
        "prev": "{MEDIA_PREV_TRACK}",
    }
    cmd = f'(New-Object -ComObject WScript.Shell).SendKeys("{mapping[key]}")'
    subprocess.Popen(["powershell", "-Command", cmd])
# ============================================================
# ===========================  UI  ============================
# ============================================================

root = tk.Tk()
root.title("Launcher Ultra Dark")
root.geometry("1200x700")

try:
    if os.path.exists("launcher.ico"):
        root.iconbitmap("launcher.ico")
except:
    pass

# HEADER
header = tk.Frame(root)
header.pack(fill="x", pady=(10, 6))

title_label = tk.Label(header, text="LAUNCHER", font=("Segoe UI", 24, "bold"))
title_label.pack(side="left", padx=(16, 8))

subtitle_label = tk.Label(header, text="Ultra Dark / Neon", font=("Segoe UI", 10))
subtitle_label.pack(side="left", pady=4)

launch_all_btn = tk.Button(
    header,
    text="🚀 Launch All",
    command=launch_all_visible,
    font=("Segoe UI", 11, "bold")
)
launch_all_btn.pack(side="right", padx=(10, 20))

# TABS BAR
tabs_frame = tk.Frame(root)
tabs_frame.pack(fill="x", pady=(0, 6), padx=12)

# MAIN CONTENT
main_frame = tk.Frame(root)
main_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

# ============================================================
# LISTES POUR LE THEMING
# ============================================================

buttons_to_style = []
labels_to_style = []
listboxes_to_style = []
entries_to_style = []
frames_to_style = []

# header + tabs + main stylés
frames_to_style.extend([header, tabs_frame, main_frame])
labels_to_style.extend([title_label, subtitle_label])
launch_all_btn.role = "accent"
buttons_to_style.append(launch_all_btn)

# ============================================================
# FONCTIONS DE THEME
# ============================================================

def get_active_theme():
    """Retourne le thème actif (preset ou custom)."""
    if current_theme_index == -1:
        return CUSTOM_THEME
    return THEME_PRESETS[current_theme_index]


def apply_theme_to_widget(widget, role="panel"):
    """Applique un thème à un widget Tk."""
    t = get_active_theme()

    if role == "bg":
        bg = t["bg"]
        fg = t["text"]
    elif role == "accent":
        bg = t["accent"]
        fg = t["text"]
    elif role == "danger":
        bg = "#8b0000"
        fg = "#ffffff"
    else:
        bg = t["panel"]
        fg = t["text"]

    if isinstance(widget, tk.Frame):
        widget.configure(bg=bg)

    elif isinstance(widget, tk.Label):
        widget.configure(bg=bg, fg=fg)

    elif isinstance(widget, tk.Entry):
        widget.configure(bg=t["panel"], fg=fg, insertbackground=fg)

    elif isinstance(widget, tk.Listbox):
        widget.configure(
            bg=t["panel"], fg=fg,
            selectbackground=t["accent"],
            selectforeground=t["text"],
            highlightthickness=0,
            relief="flat"
        )

    elif isinstance(widget, tk.Button):
        widget.configure(
            bg=bg, fg=fg,
            activebackground=bg,
            activeforeground=fg,
            relief="flat"
        )


def apply_theme_everywhere():
    """Applique le thème à toute l’UI."""
    t = get_active_theme()
    root.configure(bg=t["bg"])

    for f in frames_to_style:
        apply_theme_to_widget(f, "panel")

    for lbl in labels_to_style:
        apply_theme_to_widget(lbl, "bg")

    for lb in listboxes_to_style:
        apply_theme_to_widget(lb)

    for e in entries_to_style:
        apply_theme_to_widget(e)

    for b in buttons_to_style:
        role = getattr(b, "role", "panel")
        apply_theme_to_widget(b, role)

# ============================================================
# HELPERS STYLÉS
# ============================================================

def styled_frame(parent, *args, **kwargs):
    f = tk.Frame(parent, *args, **kwargs)
    frames_to_style.append(f)
    return f

def styled_label(parent, *args, **kwargs):
    lbl = tk.Label(parent, *args, **kwargs)
    labels_to_style.append(lbl)
    return lbl

def styled_button(parent, text, cmd, role="panel"):
    b = tk.Button(parent, text=text, command=cmd)
    b.role = role  # on stocke le rôle en attribut Python
    buttons_to_style.append(b)
    return b

def styled_listbox(parent, *args, **kwargs):
    lb = tk.Listbox(parent, *args, **kwargs)
    listboxes_to_style.append(lb)
    return lb

def styled_entry(parent, *args, **kwargs):
    e = tk.Entry(parent, *args, **kwargs)
    entries_to_style.append(e)
    return e

# ============================================================
# TABS LOGIC
# ============================================================

tab_buttons = {}
current_tab = tk.StringVar(value="apps")

def switch_tab(name):
    current_tab.set(name)
    for n, b in tab_buttons.items():
        b.configure(relief="sunken" if n == name else "raised")

    for c in main_frame.winfo_children():
        c.pack_forget()

    if name == "apps":
        apps_tab.pack(fill="both", expand=True)
    elif name == "groups":
        groups_tab.pack(fill="both", expand=True)
    elif name == "favorites":
        fav_tab.pack(fill="both", expand=True)
    elif name == "spotify":
        spotify_tab.pack(fill="both", expand=True)
    elif name == "themes":
        themes_tab.pack(fill="both", expand=True)

def add_tab(name, text):
    b = tk.Button(tabs_frame, text=text, command=lambda: switch_tab(name),
                  font=("Segoe UI", 10, "bold"))
    b.role = "panel"
    buttons_to_style.append(b)
    b.pack(side="left", padx=4)
    tab_buttons[name] = b

add_tab("apps", "Applications")
add_tab("groups", "Groupes")
add_tab("favorites", "Favoris")
add_tab("spotify", "Spotify")
add_tab("themes", "Thèmes")

# ============================================================
# TAB : APPLICATIONS
# ============================================================

apps_tab = styled_frame(main_frame)

apps_left = styled_frame(apps_tab)
apps_left.pack(side="left", fill="y", padx=(4, 8), pady=6)

search_label = styled_label(apps_left, text="Recherche", font=("Segoe UI", 9, "bold"))
search_label.pack(anchor="w")

search_var = tk.StringVar()
search_entry = styled_entry(apps_left, textvariable=search_var)
search_entry.pack(anchor="w", padx=2, pady=(2, 10))
search_entry.bind("<KeyRelease>", on_search_change)

tag_label = styled_label(apps_left, text="Tags", font=("Segoe UI", 9, "bold"))
tag_label.pack(anchor="w", pady=(4, 4))

tag_listbox = styled_listbox(apps_left, height=12)
tag_listbox.pack(fill="y")
tag_listbox.bind("<<ListboxSelect>>", on_tag_select)

apps_right = styled_frame(apps_tab)
apps_right.pack(side="right", fill="both", expand=True, padx=(0, 6))

apps_label = styled_label(apps_right, text="Applications", font=("Segoe UI", 11, "bold"))
apps_label.pack(anchor="w", pady=(0, 6))

apps_listbox = styled_listbox(apps_right)
apps_listbox.pack(fill="both", expand=True)

apps_btn_frame = styled_frame(apps_right)
apps_btn_frame.pack(fill="x", pady=6)

def select_all_apps():
    apps_listbox.select_set(0, tk.END)

def deselect_all_apps():
    apps_listbox.select_clear(0, tk.END)

styled_button(apps_btn_frame, "Ajouter", choose_and_add_app).pack(side="left", padx=4)
styled_button(apps_btn_frame, "Scan auto", auto_scan_apps).pack(side="left", padx=4)
styled_button(apps_btn_frame, "Supprimer", delete_selected_app, role="danger").pack(side="left", padx=4)
styled_button(apps_btn_frame, "Supprimer sélection", delete_multiple_apps, role="danger").pack(side="left", padx=4)
styled_button(apps_btn_frame, "Tags", set_tags_for_app).pack(side="left", padx=4)
styled_button(apps_btn_frame, "★ Favori", toggle_favorite, role="accent").pack(side="left", padx=4)

# 👉 NOUVEAU BOUTON : Ajouter à un groupe
styled_button(apps_btn_frame, "Ajouter à un groupe", add_app_to_group_from_apps).pack(side="left", padx=4)

styled_button(apps_btn_frame, "Tout sélectionner", select_all_apps).pack(side="left", padx=4)
styled_button(apps_btn_frame, "Tout désélectionner", deselect_all_apps).pack(side="left", padx=4)

styled_button(apps_btn_frame, "Lancer", launch_selected_app, role="accent").pack(side="right", padx=4)

apps_listbox.bind("<Delete>", lambda e: delete_multiple_apps())
apps_listbox.bind("<Control-a>", lambda e: (select_all_apps(), "break"))
apps_listbox.bind("<Control-A>", lambda e: (select_all_apps(), "break"))

# ============================================================
# TAB : GROUPES
# ============================================================

groups_tab = styled_frame(main_frame)

groups_left = styled_frame(groups_tab)
groups_left.pack(side="left", fill="both", expand=True, padx=10, pady=10)

groups_right = styled_frame(groups_tab)
groups_right.pack(side="right", fill="y", padx=10, pady=10)

label_groups = styled_label(groups_left, text="Groupes", font=("Segoe UI", 12, "bold"))
label_groups.pack(anchor="w", pady=4)

group_listbox = styled_listbox(groups_left)
group_listbox.pack(fill="both", expand=True)

styled_button(groups_right, "Créer groupe", create_group).pack(fill="x", pady=4)
styled_button(groups_right, "Supprimer groupe", delete_group, role="danger").pack(fill="x", pady=4)
styled_button(groups_right, "Ajouter app (depuis sélection)", add_app_to_group).pack(fill="x", pady=4)
styled_button(groups_right, "Retirer app (depuis sélection)", remove_app_from_group).pack(fill="x", pady=4)
styled_button(groups_right, "Lancer groupe", launch_group, role="accent").pack(fill="x", pady=10)

# ============================================================
# TAB : FAVORIS
# ============================================================

fav_tab = styled_frame(main_frame)

fav_label = styled_label(fav_tab, text="Favoris", font=("Segoe UI", 12, "bold"))
fav_label.pack(anchor="w", padx=10, pady=10)

fav_listbox = styled_listbox(fav_tab)
fav_listbox.pack(fill="both", expand=True, padx=10)

styled_button(fav_tab, "Lancer", launch_selected_fav, role="accent").pack(pady=10)

# ============================================================
# TAB : SPOTIFY
# ============================================================

spotify_tab = styled_frame(main_frame)

spotify_label = styled_label(spotify_tab, text="Spotify", font=("Segoe UI", 14, "bold"))
spotify_label.pack(pady=20)

styled_button(spotify_tab, "Ouvrir Spotify", open_spotify, role="accent").pack(pady=6)

sp_frame = styled_frame(spotify_tab)
sp_frame.pack(pady=10)

styled_button(sp_frame, "⏮ Précédent", lambda: send_media_key("prev")).grid(row=0, column=0, padx=8)
styled_button(sp_frame, "⏯ Play / Pause", lambda: send_media_key("play_pause"), role="accent").grid(row=0, column=1, padx=8)
styled_button(sp_frame, "⏭ Suivant", lambda: send_media_key("next")).grid(row=0, column=2, padx=8)

# ============================================================
# TAB : THEMES
# ============================================================

themes_tab = styled_frame(main_frame)

themes_title_lbl = styled_label(themes_tab, text="Thèmes prédéfinis", font=("Segoe UI", 12, "bold"))
themes_title_lbl.pack(pady=10)

themes_list = styled_listbox(themes_tab, height=14)
themes_list.pack(side="left", fill="y", padx=12, pady=10)

for th in THEME_PRESETS:
    themes_list.insert(tk.END, th["name"])

def on_select_theme(e=None):
    global current_theme_index
    sel = themes_list.curselection()
    if not sel:
        return
    current_theme_index = sel[0]
    apply_theme_everywhere()
    save_config()

themes_list.bind("<<ListboxSelect>>", on_select_theme)

custom_frame = styled_frame(themes_tab)
custom_frame.pack(side="right", fill="both", expand=True, padx=30, pady=10)

custom_title_lbl = styled_label(custom_frame, text="Thème Custom", font=("Segoe UI", 12, "bold"))
custom_title_lbl.pack(pady=10)

def pick_custom_color(key):
    c = colorchooser.askcolor(title=f"Couleur {key}")[1]
    if not c:
        return
    CUSTOM_THEME[key] = c
    save_config()
    apply_theme_everywhere()

styled_button(custom_frame, "Fond (bg)", lambda: pick_custom_color("bg")).pack(fill="x", pady=5)
styled_button(custom_frame, "Panel", lambda: pick_custom_color("panel")).pack(fill="x", pady=5)
styled_button(custom_frame, "Accent", lambda: pick_custom_color("accent")).pack(fill="x", pady=5)
styled_button(custom_frame, "Texte", lambda: pick_custom_color("text")).pack(fill="x", pady=5)

def activate_custom():
    global current_theme_index
    current_theme_index = -1
    apply_theme_everywhere()
    save_config()

styled_button(custom_frame, "Activer le thème Custom", activate_custom, role="accent").pack(pady=20)
# ============================================================
# ===============  INIT + REFRESH + MAINLOOP  =================
# ============================================================

# Charger la config
apps, groups, next_id = load_config()

# Initialiser les listes / filtres
refresh_tags_list()
apply_filters()
refresh_groups_list()
refresh_favorites_list()

# Appliquer le thème au démarrage
apply_theme_everywhere()

# Onglet par défaut
switch_tab("apps")

# Boucle principale
root.mainloop()
