import customtkinter as ctk

import os, ctypes, winreg
import win32com.client

from pathlib import Path


CHANGELOG_CODE = "V14R"
APP_NAME = "Placeify"
AUDIO_EXTS = (".mp3", ".wav", ".ogg")


def make_shortcut(target, icon=None, name=APP_NAME):
    if icon is None:
        icon = target

    shell = win32com.client.Dispatch("WScript.Shell")
    desktop = shell.SpecialFolders("Desktop")

    lnk = shell.CreateShortcut(
        os.path.join(desktop, "Placeify.lnk")
    )

    lnk.TargetPath = str(target)
    lnk.WorkingDirectory = str(Path(target).parent)
    lnk.IconLocation = str(icon)
    lnk.Save()


def _reg_set(path, name="", value=""):
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, path) as k:
        winreg.SetValueEx(k, name, 0, winreg.REG_SZ, value)

def delete_tree(root, path):
    try:
        with winreg.OpenKey(root, path, 0, winreg.KEY_ALL_ACCESS) as key:
            while True:
                try:
                    subkey = winreg.EnumKey(key, 0)
                    delete_tree(root, path + "\\" + subkey)
                except OSError:
                    break
    except FileNotFoundError:
        return

    winreg.DeleteKey(root, path)

def unregister_open_with(exe):
    app = Path(exe).name

    delete_tree(
        winreg.HKEY_CURRENT_USER,
        rf"Software\Classes\Applications\{app}"
    )

    for ext in AUDIO_EXTS:
        try:
            winreg.DeleteKey(
                winreg.HKEY_CURRENT_USER,
                rf"Software\Classes\{ext}\OpenWithList\{app}"
            )
        except FileNotFoundError:
            pass

    ctypes.windll.shell32.SHChangeNotify(
        0x08000000,
        0,
        None,
        None
    )

def register_open_with(exe, name=APP_NAME):
    app = Path(exe).name

    _reg_set(
        rf"Software\Classes\Applications\{app}\shell\open\command",
        "",
        f'"{exe}" "%1"'
    )

    _reg_set(
        rf"Software\Classes\Applications\{app}",
        "FriendlyAppName",
        name
    )

    for ext in AUDIO_EXTS:
        _reg_set(
            rf"Software\Classes\Applications\{app}\SupportedTypes",
            ext,
            ""
        )

        _reg_set(
            rf"Software\Classes\{ext}\OpenWithList\{app}"
        )

    ctypes.windll.shell32.SHChangeNotify(
        0x08000000,
        0,
        None,
        None
    )


def show_startscreen(root: ctk.CTk, icon, callback, ico_path, exe_path):  # for new users
    def set_up():
        want_shortcut = bool(create_shortcut_check.get())
        want_openwith = bool(openwmenu.get())

        if want_shortcut:
            make_shortcut(exe_path)
        if want_openwith:
            register_open_with(exe_path)

        changelog.destroy()
        callback()

    changelog = ctk.CTkFrame(root, corner_radius=0)
    changelog.place(relwidth=1, relheight=1)

    icon_label = ctk.CTkLabel(changelog, text="", image=icon)
    icon_label.place(x=10, y=10)

    placeify_label = ctk.CTkLabel(changelog, text="Placeify", font=("Segoe UI", 24, "bold"))
    placeify_label.place(x=80, y=10)

    changelog_info = ctk.CTkLabel(changelog, text=f"{CHANGELOG_CODE} (Stable release)", font=("Segoe UI", 16, "normal"))
    changelog_info.place(x=80, y=40)

    # everything below is now parented to `changelog`, not `root`
    divider = ctk.CTkFrame(changelog, corner_radius=6, height=4, width=690, fg_color="#F4804F")
    divider.place(x=5, rely=0.2)

    changes_text = ctk.CTkLabel(changelog, justify="left",
        text="Thank you so much for downloading Placeify! \nSince it looks like you're new... Just a couple of things before we get started.")
    changes_text.place(x=9, rely=0.25)

    divider2 = ctk.CTkFrame(changelog, corner_radius=6, height=2, width=690, fg_color="#141414")
    divider2.place(x=5, rely=0.35)

    installation_title = ctk.CTkLabel(changelog, text="Installation Options", justify="left", font=("", 26, "bold"))
    installation_title.place(x=9, rely=0.38)

    checkbox_style = dict(bg_color="#2B2B2B", fg_color="#F4804F", hover_color="#9D502F")

    create_shortcut_check = ctk.CTkCheckBox(changelog, text="Create Desktop Shortcut", **checkbox_style)
    create_shortcut_check.place(x=25, rely=0.47)
    create_shortcut_check.select()

    openwmenu = ctk.CTkCheckBox(changelog, text="Add Placeify to 'Open With' menu", **checkbox_style)
    openwmenu.place(x=25, rely=0.54)
    openwmenu.select()

    continue_button = ctk.CTkButton(changelog, text="Continue", fg_color="#F4804F", text_color="#101010",
                                    bg_color="#2B2B2B", font=("", 13, "bold"), hover_color="#9D502F", command=set_up)
    continue_button.place(relx=0.75, rely=0.9)

#def v12_transfer_screen(root: ctk.CTk, icon, kickstart,transfer):  # for new users# for new users
def v12_transfer_screen(root: ctk.CTk, icon):  
    transfer_frame = ctk.CTkFrame(root, corner_radius=0)
    transfer_frame.place(relwidth=1, relheight=1)

    icon_label = ctk.CTkLabel(transfer_frame, text="", image=icon)
    icon_label.place(x=10, y=10)

    placeify_label = ctk.CTkLabel(transfer_frame, text="Placeify", font=("Segoe UI", 24, "bold"))
    placeify_label.place(x=80, y=10)

    changelog_info = ctk.CTkLabel(transfer_frame, text=f"{CHANGELOG_CODE} (Stable release) - Data Transfer", font=("Segoe UI", 16, "normal"))
    changelog_info.place(x=80, y=40)

    # everything below is now parented to `changelog`, not `root`
    divider = ctk.CTkFrame(transfer_frame, corner_radius=6, height=4, width=690, fg_color="#F4804F")
    divider.place(x=5, rely=0.2)

    changes_text = ctk.CTkLabel(transfer_frame, justify="left",
        text="Thank you upgrading Placeify! \nDue to a new song system, we will need to reformat some of your data.")
    changes_text.place(x=9, rely=0.25)

    divider2 = ctk.CTkFrame(transfer_frame, corner_radius=6, height=2, width=690, fg_color="#141414")
    divider2.place(x=5, rely=0.35)

    step_text = ctk.CTkLabel(transfer_frame, text="Creating Directory Snapshot...")
    step_text.pack(fill="both", pady=(180, 15))
    extra_text = ctk.CTkLabel(transfer_frame, text="")
    extra_text.pack(fill="both", pady=(5))
    progress = ctk.CTkProgressBar(transfer_frame, width=450, progress_color="#F4804F", fg_color="#141414")
    progress.pack()
    progress.set(0)

    return step_text, extra_text, progress, transfer_frame
