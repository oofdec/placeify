import math
import time
import shutil

import customtkinter as ctk
from tkinter import messagebox as mb
from tkinter import filedialog as fd
from PIL import Image
import pywinstyles

from mutagen.id3 import ID3
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
from pygame import mixer

import yt_dlp
import requests
from yt_dlp.utils import sanitize_filename

import io
import os, sys
from pathlib import Path
import threading

import asyncio
from pypresence import Presence

import json
import ctypes
import subprocess
import random
import re

from pprint import pprint

import assets.dependancies.changelogs as changelogs
import assets.dependancies.ui.home_ui as home_ui
import assets.dependancies.multinstance as mutinstance

#im so sad sonic originals is over :(
#BUT ITS THE SPOOKY-EST DAY OF THE SPOOKY MONTH SO IT'S OKAY!!!!!!!

# HIGHEST PRIORITY:
    #final release

# SECOND PRIORITY
    #add full support for all ext's (ogg, wav, and uh i think thats it actually...)
    #add a "..." button to the library menu, make it contain delete and renameing functions.

   # visualzier

# COMPLETELY OPTIONAL:
    # mutiscreen support


#sanity check:

#new users -  detected, works/
#transfered - works cleanly

app_arguments = sys.argv
def init_passes():
    mutinstance.main(app_arguments, open_import_menu)

    if sys.platform == "win32":
        CREATE_NO_WINDOW = subprocess.CREATE_NO_WINDOW
    else:
        CREATE_NO_WINDOW = 0
        mb.showwarning("Untested platform",f"You are running this app on a unsuported OS, ({sys.platform}) expect bugs and errors.")

APP_VERSION = 12
default_settings = {
                    "scroll_speed":0.08,
                    "blur_amount":0.25,
                    "infobar_opacity":1,
                    "use_disc":True,
                    "load_imgs":True,
                    "img_que":False,
                    "console_startup":False,
                    "version":APP_VERSION,
                    "openwidth_assigned":False
                    }

bookmarks = []
bookmark_frames = []  # for the ui elements

recent_songs = [] #a list of strings of song names
def safe_mkdir(dirname):
    if not os.path.exists(dirname):
        os.mkdir(dirname)
        print(f"✅path {dirname} created")
    else:
        print(f"ℹ️path {dirname} already exists")

appdata_path = os.getenv('APPDATA')

placeify_path = os.path.join(appdata_path,"placeify")
music_path = os.path.join(appdata_path,"placeify","music")
settings_path = os.path.join(placeify_path,"settings.json")
bookmarks_path = os.path.join(appdata_path,"placeify","bookmarks.json")
directorys_path = os.path.join(appdata_path,"placeify","directorys.json")
recents_path = os.path.join(appdata_path,"placeify","recents.json")

is_new_user = False
is_transfering = False
is_v12_format = False

if not os.path.exists(placeify_path):
    is_new_user = True

if not os.path.exists(recents_path) and not os.path.exists(directorys_path):
    is_transfering = True


def safe_create_appdata_save(path, default_value):
    if not os.path.exists(path):
        with open(path,"w") as f:
            f.write(json.dumps(default_value))
        print(f"✅{path} created")
    else:
        print(f"ℹ️{path} already exists")

def find_best_music_dir(): # this is so stable trust bro trust
    safe_mkdir(placeify_path)
    safe_mkdir(music_path)

    safe_create_appdata_save(settings_path,default_settings)
    safe_create_appdata_save(bookmarks_path,[])

    return music_path

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def get_specialapp_path(name):
    name = os.path.join("assets","downloading",name)
    appname = name + ".exe"

    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, appname)
    else:
        return os.path.join(appname)

def get_exe_path():
    if getattr(sys, "frozen", False):
        return Path(sys.executable)

    return Path(__file__).resolve()


def update_presence(state, details):
    if not failed_presense and saved_settings["use_disc"]:
        try:
            rpc.update(
                state=state,
                details=details,
                large_image="main",
                large_text="LARGE TEXT"
            )
        except:
            pass


def truncate_string(text, limit = 125):
    if len(text) <= limit:
        return text
    
    return text[:limit] + ("..." if limit > 3 else "")

def connect_presence():
    if safe_settings_grab("use_disc") == 1:
        global failed_presense, rpc_loop

        try:
            rpc_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(rpc_loop)

            rpc.connect()
            rpc.update(
                state="in the menus",
                details="chooseing a song",
                large_image="main",
                large_text="large text"
            )

            failed_presense = False
        except Exception as e:
            print("Presence failed:", e)
            failed_presense = True


#ORGANIZE!
#add post image grabbing que

#oh wow this is still here... uh i mean i think i should keep it its like a artifact at this point...

#-----------------------------------------------------------------------------------------------------------
#-----------music file stuff--------------------------------------------------------------------------------
def valid_audio_name(name):
    if ".mp3" in name: # or ".ogg" in name or ".wav" in name: commenting theese out for now until i add mofitication detection and support for other extentions.
        return True
    else:
        return False

def load_image_thread():
    global all_songs
    root.configure(cursor="watch")
    root.update()

    if safe_settings_grab("load_imgs") == 1: #if we want thumbnails at all
        starting_directory = GLOBAL_MUSIC_DIR

        for i in range(len(all_songs)):
            if starting_directory == GLOBAL_MUSIC_DIR: #make sure they didnt click off, if so, CANCEL ITTTT
                current_song_name = list(all_songs[i])[2]      #god my hate for tuples will never be matched.   WHY AM I STILL USEING THEM?????
        
                if valid_audio_name(current_song_name) :
                    current_songdir = os.path.join(music_path,current_song_name)
            
                    image_data = None
                    try:
                        audio = ID3(current_songdir)
                        
                        for tag in audio.values():
                            if tag.FrameID == "APIC":
                                image_data = tag.data
                                break
                    except Exception:
                        pass                                                                     

                    if image_data:
                        img = Image.open(io.BytesIO(image_data))

                        songdata = list(all_songs[i])
                        songdata[0] = img
                        all_songs[i] = tuple(songdata)
            else:  #wrong indent   -   why did i write this? what dose this even mean? what?
                return   #canel if dir changes while loading images
    else:
         for i in range(len(all_songs)):
            current_song = list(all_songs[i])
            current_song[0] = Image.new("RGBA",(1,1))

            all_songs[i] = tuple(current_song)
            song_frames[i][1].image_loaded = True
    root.configure(cursor="arrow")
                
def safeload_song(name, usedir=False):
    if usedir:
        song_dir = name
    else:
        song_dir = os.path.join(music_path,name)

    uploader = ""
    image_data = None

    try:
        audio = ID3(song_dir)

        try:
            uploader = audio.get("TPE1").text[0]
        except:
            pass
        try:
            for tag in audio.values():
                if tag.FrameID == "APIC":
                    image_data = tag.data
                    break                                                          
        except Exception:
            image_data = Image.new("RGB",(1,1))                                                                   
        if image_data:
            image_data = Image.open(io.BytesIO(image_data))
        else:
            image_data = Image.new("RGB",(1,1))
    except Exception as e:
        print(f"failed to grab song {name} due to the following exception: {e}")
        image_data = Image.new("RGB",(1,1),"#1E0000")
    return image_data, song_dir, name, uploader

def safe_settings_grab(name):
    if name in saved_settings:
        #print(f"✅recall setting name {name}") #OH MY GOD      SHUT. UP.
        return saved_settings[name]
    else:
        if name in default_settings:
            print(f"⚠️outdated save for '{name}', returning current default '{default_settings[name]}'")
            return default_settings[name]
        else:
            print(f"❌ invalid setting name '{name}', no references or defaults found.")
            return None

def play_current_selected_library_song():
    select_song(songdir=os.path.join(music_path,current_song_hover))

def maintain_library_aftermenu(): #i hate this bro why is it like this
    bg_frame.lift()
    library_menu_frame.lift()
    bg_frame.place(relwidth=1,relheight=1)
    pywinstyles.set_opacity(bg_frame, 0.8)

def close_delete_menu():
    animate_close_menu(delete_frame,0.15,1,False)
    
    root.after(400, maintain_library_aftermenu) #exactly 800

def delete_song(name:str):
    '''FULLY remove a song, from the library and everythin'''
    if CURRENT_TRACKDATA:
        if CURRENT_TRACKDATA[2] == name:
            mixer.music.stop()
            mixer.music.unload()

    try:
        pass
        os.remove(os.path.join(music_path,name))
    except:
        print("Failed to remove song due to permission errors.")
        return

    #ok i just wanna say that this is the most convoluted peice of code i have ever written and i love it

    copy_directorys = song_directorys.copy() #we can delete data WHILE iterateing over it.
    for directory in list(copy_directorys.keys()): # we need to do this DREADFUL loop thing since there can be mutiple songs in one directory :(
        for i in range(len(copy_directorys[directory])):
            if name in copy_directorys[directory]:
                song_index = copy_directorys[directory].index(name)
                song_directorys[directory].pop(song_index)

    reload_all_lib_songs()
    load_song_library()

    reload_current_directory_ui()
    close_delete_menu()


def delete_from_library_menu():
    delete_song_title.configure(text=current_song_hover.replace(".mp3",""))
    bg_frame.place(relwidth=1,relheight=1)

    bg_frame.lift()
    delete_frame.lift()

    close.place_forget()

    delete_song_btn.configure(command=lambda:delete_song(current_song_hover))
    animate_open_menu(delete_frame,-1,0.15,True)

current_song_hover = None
def hover_library_song(event, row,name):
    global current_song_hover
    row.configure(fg_color="#252525")

    add_song_to_library_button.place(in_=row, relx=0.8, y=5)
    play_song_from_library_button.place(in_=row, relx=0.6, y=5,relwidth=0.2)
    remove_song_from_library_button.place(in_=row, relx=0.4, y=5,relwidth=0.2)

    add_song_to_library_button.lift()  
    play_song_from_library_button.lift()
    remove_song_from_library_button.lift()

    current_song_hover = name

def leave_library_song(event, row):
    # i have abolsutely no clue what the hell this dose but it works so....
    x, y = row.winfo_pointerxy()
    under = row.winfo_containing(x, y)
    if under is not None and (under is row or str(under).startswith(str(row))
                              or under is add_song_to_library_button._canvas
                              or str(under).startswith(str(add_song_to_library_button))):
        return
    row.configure(fg_color="#121212")

    add_song_to_library_button.place_forget()
    play_song_from_library_button.place_forget()
    remove_song_from_library_button.place_forget()

def get_all_songs_used(dict:dict, include_folders=False):
    keys = list(dict.keys())
    result = []
    for key in keys:
        songs_in_cdir = dict[key]
        valid_songs = []

        if not include_folders:
            for item in songs_in_cdir:
                if valid_audio_name(item):
                    valid_songs.append(item)
        result.extend(valid_songs)
    return result

def library_song_ui_template(name):
    row = ctk.CTkFrame(library_song_menu, height=40, fg_color="#121212")
    row.pack(fill="x", pady=5)

    title = ctk.CTkLabel(row, text=name[:-4], justify="left", font=("Arial", 12))
    title.place(x=5, y=5)

    row.bind("<Enter>", lambda e, r=row, n=name: hover_library_song(e, r,n))
    row.bind("<Leave>", lambda e, r=row: leave_library_song(e, r))
    title.bind("<Enter>", lambda e, r=row, n=name: hover_library_song(e, r,n))
    title.bind("<Leave>", lambda e, r=row: leave_library_song(e, r))

    return row, title


def songframe_template(name):
    song_frame =  ctk.CTkFrame(root,width=300,height=40)
    image_label = ctk.CTkLabel(song_frame,width=300,height=40,text="")

    title_label = ctk.CTkLabel(song_frame, text=f" {name.replace(".mp3","")} ", font=("Arial", 20, "bold"), image=None if valid_audio_name(name) and name != "<< Back" else folder_image,compound="right")
    
    image_label.place(relx=0.5, rely=0.5, anchor="center")
    title_label.place(relx=0.5, rely=0.5, anchor="center")

    image_label.ctkimage = None

    return song_frame, image_label, title_label


library_songs = []
def load_song_library(): #only ran once, put the name and widget into library_songs    
    for widget, _, _ in library_songs:
        widget.destroy()
    library_songs.clear()

    reload_all_lib_songs()

    for name in all_library_songs:
        widget, label = library_song_ui_template(name)
        library_songs.append((widget,name,label))

    library_menu_info.configure(text=f"{len(all_library_songs)} Songs  ")

def rebind_all_songframes():
    global songframe_option_index
    songframe_option_index = None
    songframe_option_button.place_forget()

    for i in range(len(song_frames)):
        song_frame, image_label, title_label = song_frames[i]
        if i <= len(all_songs)-1: #if in range
            image_label.bind("<Button-1>", lambda event, idx=i: bind_songframe_button_thing(idx))
            title_label.bind("<Button-1>", lambda event, idx=i: bind_songframe_button_thing(idx))
            image_label.bind("<Enter>", lambda event, idx=i:enter_songframe(event,idx))
            title_label.bind("<Enter>", lambda event, idx=i:enter_songframe(event,idx))
            image_label.bind("<Leave>", bind_leave_cursor)
            title_label.bind("<Leave>",bind_leave_cursor)

        else:
            if title_label.cget("text") == "<< Back":
                song_frame.bind("<Button-1>", lambda event, idx="back": bind_songframe_button_thing(idx))
                title_label.bind("<Button-1>", lambda event, idx="back": bind_songframe_button_thing(idx))

            image_label.bind("<Enter>", bind_select_cursor)
            title_label.bind("<Enter>", bind_select_cursor)
            image_label.bind("<Leave>", bind_leave_cursor)
            title_label.bind("<Leave>", bind_leave_cursor)

def lw_add_song(name, include_cdir=False): #im calling theese "lightweight" functions, they're designed to replace the constant full cache refresh that is currently used.
    name = os.path.basename(name)+".mp4"
    library_song_widget, label = library_song_ui_template(name)
    library_song_widget.pack()

    library_songs.append((library_song_widget,name, label))

    if include_cdir:
        lw_append_song_to_cdir(name)
    rebind_all_songframes()


def lw_append_song_to_cdir(name): #im calling theese "lightweight" functions, they're designed to replace the constant full cache refresh that is currently used.
    songframe, image_label, title_label = songframe_template(name)

    i = len(all_songs)

    image_label.bind("<Button-1>", lambda event, idx=i: bind_songframe_button_thing(idx))
    title_label.bind("<Button-1>", lambda event, idx=i: bind_songframe_button_thing(idx))
    image_label.bind("<Enter>", lambda event, idx=i:enter_songframe(event,idx))
    title_label.bind("<Enter>", lambda event, idx=i:enter_songframe(event,idx))
    image_label.bind("<Leave>", bind_leave_cursor)
    title_label.bind("<Leave>",bind_leave_cursor)
    
    all_songs.append(safeload_song(name))
    song_frames.insert(i,(songframe, image_label, title_label))
    song_directorys[GLOBAL_MUSIC_DIR].append(name)
    song_directorys[GLOBAL_MUSIC_DIR].sort()

    bg_frame.lift()
    library_menu_frame.lift()
    library_menu_button.lift()

def direct_children(parent, paths):
    parent = Path(parent).resolve()
    return [p for p in paths if Path(p).resolve().parent == parent]

def get_song_list_from_dir(path:str):
    result = []

    keys = song_directorys.keys()  # Returns a dict_keys view
    keys = list(keys) 
    for i in range(len(keys)):
        if keys[i] == path:
            result.append(keys[i])

        direct_directorys = direct_children(keys[i],keys)
        if direct_directorys:
            result.extend(direct_directorys)
    return result

all_songs = []
def compile_music_cache(): #CHANGE THIS
    music_dir = song_directorys[GLOBAL_MUSIC_DIR] #list of all song names in selected dir

    all_songs.clear()

    for songname in music_dir: # filter mp3
        _, ext = os.path.splitext(songname) #gets the extention (.mp3, "" for direcotys)
        if valid_audio_name(ext):
            all_songs.append(safeload_song(songname))
        if ext == "":
            all_songs.append((Image.new("RGBA",size=(1,1)),None,songname,""))

def show_console():
    ctypes.windll.kernel32.AllocConsole()
    sys.stdout = open("CONOUT$", "w")
    sys.stderr = open("CONOUT$", "w")

def transfer_directory_to_library():
    song_directorys.clear()

    for droot, dirs, files in os.walk(GLOBAL_MUSIC_DIR): #1: reserve format
        directory_items = []

        directory_items.extend(files)
        directory_items.extend(dirs)

        song_directorys[droot] = directory_items

    for droot, dirs, files in os.walk(GLOBAL_MUSIC_DIR):  #2: move everything to music root
        for filename in files:
            try:
                shutil.move(os.path.join(droot,filename),music_path)
            except:
                pass

    for droot, dirs, files in os.walk(GLOBAL_MUSIC_DIR,topdown=False): #3: cleanup
        if droot != music_path:
            for filename in files:
                os.remove(os.path.join(droot,filename))
            try:
                os.rmdir(droot)
            except:
                print(f"Failed to remove {droot}")
    #i totally forgot, bookmarks dont use directorys, soo we dont gotta do anything :D

    safe_create_appdata_save(directorys_path,song_directorys)
    safe_create_appdata_save(recents_path,[])


# BASE INITS---MUSIC DIRS-----------------
GLOBAL_MUSIC_DIR = find_best_music_dir()
BASE_DIR = GLOBAL_MUSIC_DIR
song_directorys = {}
in_menu = False
mixer.init()

if not is_new_user and is_transfering:
    transfer_directory_to_library() #so there IS a menu for this but i'm not using it cuz 1. too fast- 2. root isnt defined yet and it'd look weird to do it later so its fine really but you can still emulate the screen if you want, it's in changelogs.py


#SETTINGS RECALL------------------------------

with open(settings_path,"r") as f:
    try:
        saved_settings = json.loads(f.read())
    except:
        print("⚠️ settings courrupted - could not read setting json. restoring defaults")
        saved_settings = default_settings #fallback if courrupted settings

        with open(settings_path, "w") as f:
            f.write(json.dumps(saved_settings))
        print("   └ ℹ️default settings restored.")

if safe_settings_grab("console_startup"):
    show_console()
    print("   🧰 DEBUG MODE ON --------------------------------------------------------\n   This console can only be created AFTER some logging has already occured, and are therefor hidden.\n for the full console, download the full open-source version of this program.\n----------------------------------------------------------- ")
print("GLOBAL DIR: "+GLOBAL_MUSIC_DIR)


with open(bookmarks_path,"r") as f:
    try:
        bookmarks = json.loads(f.read())
        print("✅ sucessfully loaded bookmarks")
    except:
        print("🔴 bookmarks courrupted - could not read json. Deleteing everything :(")

        with open(bookmarks_path, "w") as f:
            f.write(json.dumps([]))

        bookmarks = []

with open(directorys_path,"r") as f:
    try:
        song_directorys = json.loads(f.read())
        print("✅ sucessfully loaded directorys")
    except:
        mb.showerror("Directorys courrupted","The directorys.json file has been courrupted and cannot be read correctly. Your file will be preserved for now, hovever data cannot be read. If you changed this file yourself, please undo that change, or find a online 'json repair tool.'")
        song_directorys = {}

with open(recents_path,"r") as f:
    try:
        recent_songs = json.loads(f.read())
        print("✅ sucessfully loaded recents")
    except:
        print("🔴 recents courrupted - could not read json")

        with open(recents_path, "w") as f:
            f.write(json.dumps([]))

        recent_songs = []

#DISCORD------------------
CLIENT_ID = "1532524855130587216"
rpc = Presence(CLIENT_ID)
failed_presense = False
threading.Thread(target=connect_presence, daemon=True).start()

def cubic_bounce(start, end, t, bounce_mult=0.25):
    if t < 0: t = 0
    if t > 1: t = 1

    base = 1 - (1 - t)**3
    bounce = math.sin(t * math.pi) * (1 - t) * bounce_mult

    return start + (end - start) * (base + bounce)

def cubic_in(t, start, end):
    return start + (end - start) * (t ** 3)

def cubic_out(t, start, end):
    return start + (end - start) * (1 - (1 - t) ** 3)


ffmpeg_path = get_specialapp_path("ffmpeg")
deno_path = get_specialapp_path("deno")

def check_specalpath(path):
    if os.path.exists(path):
        print(f"✅ {path} Exists")
    else:
        print(f"❌ {path} not found")

print("🌟 special paths: -----------------")
check_specalpath(deno_path)
check_specalpath(ffmpeg_path)
print("⚙️ settings recall: -----------------")

ANSI_RE = re.compile(r'\x1b\[[0-9;]*m') #adachi rei?  no?  they sound alike..
def download_progress_hook(d):
    def update_ui():

        yt_import_console.configure(state="normal")

        if d['status'] == 'downloading':
            print(d.get('_percent_str') or d.get('progress'))
            percent = d.get('_percent_str') or d.get('progress')\
            
            if percent:
                yt_import_console.insert(ctk.END, f"{percent}\n")

        elif d['status'] == 'finished':
            yt_import_console.insert(ctk.END, "✅ Download finished, post-processing...\n") #stright outta the docs 😭😭

        yt_import_console.see(ctk.END)
        yt_import_console.configure(state="disabled")

    root.after(0, update_ui) #force ui to update


def reload_all_lib_songs():
    all_library_songs.clear()

    songs = os.listdir(music_path)
    for current_song in songs:
        all_library_songs.append(current_song)

def download_youtube(url):
    yt_import_console.insert(ctk.END,"Starting download...")
    root.update()

    ydl_opts = {
        "format": "bestaudio/best",
        "postprocessors": [
            {"key": "FFmpegExtractAudio", "preferredcodec": "mp3"},
            {"key": "FFmpegThumbnailsConvertor", "format": "jpg"},
            {"key": "EmbedThumbnail"},
            {"key": "FFmpegMetadata"},
        ],
        "writethumbnail": True,
        "ffmpeg_location": ffmpeg_path,
        "outtmpl": f"{music_path}/%(title)s.%(ext)s",
        "js_runtime": f"deno:{deno_path}",
        "remote_components": ["ejs:github"],
        "progress_hooks": [download_progress_hook],
        "noplaylist": not yt_playlist_check.get()
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)   # download and get info in one call
        final_path = ydl.prepare_filename(info)       # this normally ends in .webm (original ext)
        final_path = os.path.splitext(final_path)[0] + ".mp3"

    return info, final_path


#-----------------------------------------------------------------------------------------------------------
#-----------UI Stuff--------------------------------------------------------------------------------
root = ctk.CTk("#000000")
root.geometry("700x400")
root.title("placeify")
root.resizable(width=False,height=False)

ctk.set_appearance_mode("dark")

root_w = 700
root_h = 400

folder_obj = Image.open(resource_path("assets/folder.png"))
folder_image = ctk.CTkImage(folder_obj,size=(23,16))

more_options_obj = Image.open(resource_path("assets/more_options.png"))
more_options_image = ctk.CTkImage(more_options_obj,size=(9,32))

placeify_ico = resource_path("assets/placeify.ico")

pause_state = ctk.BooleanVar(value=False) # unpaused
FOCUS_INDEX = 0 # internal index
RENDER_INDEX = 0 # UI index- for offset
PLAYING_INDEX = None # for ui state holding
CURRENT_TRACKDATA = ()
song_frames = [] # a list containing all of the ui elemets for showing the songs
recent_frames = [] #only for recent songs, i mean its not wrong since it techianlly not apart of the scrolling thing... again, if you read the v12 changlog- i still dont have a name for it.
all_library_songs = []

current_music_lenght = 0
playing_xoffset = 0 #an offset applyed to the current played song
global_x_offset = 0 # applys to all widgets for switching diretorys

seek_offset = 0      # position (seconds) within the track where playback last started/resumed
play_start_time = 0  # time.time() when playback last started/resumed

seed = random.randint(0,10000000) #i doooooooooo kinda need that for laterrrr....
random.seed(seed) # i dunno, it didnt really feel random for me before \_=-=_/

#--------------------------------------------------------------------------------
#FUNCTIONS ----------------------------------------------------------------------
#--------------------------------------------------------------------------------
def get_current_track_pos():
    """Current position in the track, in seconds. Safe to call whether playing or paused."""
    if pause_state.get():
        return seek_offset
    return seek_offset + (time.time() - play_start_time)

def manage_pause(customstate=None):
    global seek_offset
    global play_start_time

    if CURRENT_TRACKDATA == (): # no track loaded
        return

    if customstate == None:
        current_state = not(pause_state.get())
    else:
        current_state = customstate

    if current_state: # true = paused
        # fold whatever time has passed since the last play/resume into seek_offset,
        # so we "freeze" the exact position instead of losing track of it

        #yeah whatever you say anthropic

        seek_offset = get_current_track_pos()
        mixer.music.pause()
        pause_butt.configure(text="▶️")
    else:
        mixer.music.play(start=seek_offset)
        play_start_time = time.time()
        pause_butt.configure(text="⏸️")

    pause_state.set(current_state)


def skip_next_song():
    global PLAYING_INDEX
    global FOCUS_INDEX

    if PLAYING_INDEX != None:
        sus_index = (PLAYING_INDEX+1)%(len(all_songs))

        PLAYING_INDEX = (PLAYING_INDEX+1)%(len(all_songs))
        FOCUS_INDEX = PLAYING_INDEX

        if valid_audio_name(all_songs[sus_index][2]):
            select_song(PLAYING_INDEX)


def skip_backwards_song():
    global PLAYING_INDEX
    global FOCUS_INDEX

    if PLAYING_INDEX != None:
        sus_index = (PLAYING_INDEX-1)%(len(all_songs))

        PLAYING_INDEX = (PLAYING_INDEX-1)%(len(all_songs))
        FOCUS_INDEX = PLAYING_INDEX

        if valid_audio_name(all_songs[sus_index][2]):
            select_song(PLAYING_INDEX)



def find_random_valid_song_in_dir(): #its messy- but still better then theoretically looping indefinitely.
    global PLAYING_INDEX
    
    current_song = CURRENT_TRACKDATA[2] if CURRENT_TRACKDATA else None
    #print(all_songs)

    valid_dirs = []
    for song in all_songs:
        song_name = song[2]
        if valid_audio_name(song_name) and song_name != current_song:
            valid_dirs.append(song_name)

    if len(valid_dirs) < 1:
        return None

    return random.choice(valid_dirs)


def restart_current_song():
    if CURRENT_TRACKDATA != ():
        select_song(songdir=CURRENT_TRACKDATA[1])


def random_song():
    global PLAYING_INDEX
    global FOCUS_INDEX

    random_song = find_random_valid_song_in_dir()

    song_index = 0
    for i in range(len(all_songs)):
        songname = all_songs[i][2]
        if random_song == songname:
            song_index = i
    
    if random_song:
        PLAYING_INDEX = song_index
        FOCUS_INDEX = song_index

        #select_song(songdir=os.path.join(music_path,random_song)) #it actually dosnt matter which one u do
        select_song(song_index)

def seek_pos(event):
    if CURRENT_TRACKDATA != (): #make sure that there is even a song loaded
        global seek_offset

        manage_pause(True) # pause while scrubbing so nothing else fights over seek_offset 
        current_s = get_current_track_pos()

        if current_music_lenght > 0:
            seek_offset = timeline_slider.get() * (current_music_lenght / 1000)
            slider_value = current_s / (current_music_lenght / 1000)
            slider_value = max(0, min(1, slider_value)) # clamp so it can't run past the end of the track

            timelime_label.configure(text=f"{calulate_seconds_strtime(current_s)} / {calulate_seconds_strtime(current_music_lenght//1000)}")

#--------------------------------------------------------------------------------
#UI FUNCTIONS -------------------------------------------------------------------
#--------------------------------------------------------------------------------
def animate_open_menu(widget,start,final,use_opacity=False,time=0):
    global in_menu
    in_menu = True

    if time <= 50:
        widget.place(rely=cubic_out(time/50,start,final))
        if use_opacity:
            pywinstyles.set_opacity(widget,cubic_out(time/50,0,1))
            pywinstyles.set_opacity(bg_frame,cubic_out(time/50,0,0.8))
        time += 2
        root.after(16,lambda:animate_open_menu(widget,start,final,use_opacity,time))

def animate_close_menu(widget,start,final,use_opacity=False,time=0):
    global in_menu
    in_menu = False

    if time <= 50:
        widget.place(rely=cubic_out(time/50,start,final))
        if use_opacity:
            pywinstyles.set_opacity(widget,cubic_out(time/50,1,0))
            pywinstyles.set_opacity(bg_frame,cubic_out(time/50,0.8,0))
    time += 2
    if time > 50:
        close_focus_menus()
        pywinstyles.set_opacity(bg_frame,1)

        return
    
    root.after(16,lambda:animate_close_menu(widget,start,final,use_opacity,time))

def show_settings_menu():
    settmenu.place(relwidth=1,relheight=1,rely=1)
    settmenu.lift()


    root.after(0,lambda: animate_open_menu(settmenu,-1,0,True))

def close_focus_menus():
    bg_frame.place_forget()

    musicmenu.place_forget()
    create_directory_frame.place_forget()

    settmenu.place_forget()
    

def save_settings():
    global saved_settings

    saved_settings = {
        "scroll_speed":scroll_speed_slider.get(),
        "blur_amount": bg_blur_slider.get(),
        "use_disc":use_disc_check.get(),
        "load_imgs":use_thumbnails_check.get(),
        "console_startup":show_console_startup.get(),
        "infobar_opacity":infobar_opacity_slider.get(),
        "version":default_settings["version"],
        "openwidth_assigned":openwith_menu_check.get()
        }
    print(saved_settings)
    try:
        with open(settings_path, "w") as f:
            f.write(json.dumps(saved_settings))
        print("✅settings saved successfully!")
    except Exception as e:
        print("❌uh oh, couldnt save settings bc "+str(e))

def close_settings_menu():
    animate_close_menu(settmenu,0,1,True)

def tween_linear(start, end, t):
    return start + (end - start) * t


def update_preview_tracktime(event=None):
    tracklenght = current_music_lenght//1000


    current_bookmark_tracktime = tween_linear(0,tracklenght,bookmark_track.get())

    bookmark_timestamp_preview.configure(text=f"{calulate_seconds_strtime(current_bookmark_tracktime)} / {calulate_seconds_strtime(tracklenght)}")

def find_bookmark_index_from_name(name):
    for i in range(len(bookmarks)):
        current_bookmark = bookmarks[i]
        if current_bookmark['song'] == name:
            return i
    return None

def remove_timestamp(index):
    current_song = find_bookmark_index_from_name(CURRENT_TRACKDATA[2])

    bookmarks[current_song]["timestamps"].pop(index)
    bookmarks[current_song]["names"].pop(index)

    reload_bookmark_manager_timestamps()
    reload_bookmarks()

bookmark_manager_frames = [] #i hate this so much..     AND I HAATTEEE IIIIIIITTTTTT      i hate the way you make me feel.. SO ILL BREAK IITTTTT!!!!11!!!! ill break, ANYTHING THATS REAL!!!!!!
def reload_bookmark_manager_timestamps():
    for bookmark in bookmark_manager_frames:
        bookmark.destroy()
    bookmark_manager_frames.clear()  #.clear() is a mutation, no need for global declaration


    bookmark_data = find_bookmarks_from_songname(CURRENT_TRACKDATA[2])
    if bookmark_data: #if any data exists for this song
        timestamps = bookmark_data["timestamps"]

        for i in range(len(timestamps)):
            indicator = ctk.CTkButton(bookmark_track_frame,width=10,text="X",text_color="black",fg_color="white",corner_radius=3,height=25,command=lambda index=i:remove_timestamp(index),hover_color="#FF8888")
            indicator.place(relx=timestamps[i],rely=0.3) # timestamp is recorded in the slider (0-1) on the manager, and so is relx (0-1), so this becomes really easy

            bookmark_manager_frames.append(indicator) # so they can be removed later
            indicator.bind("<Enter>",lambda event,index=i:timestamp_hover(event,index,150))
            indicator.bind("<Leave>",hover_timestamp_leave)


def show_bookmark_manager():
    manage_pause(customstate=True)
    if CURRENT_TRACKDATA != ():
        global bookmark_current_s 
        bookmark_menu.place(relwidth=1,relheight=1,rely=1)
        bookmark_menu.lift()

        bookmark_target.configure(text=f" -  '{CURRENT_TRACKDATA[2].replace('.mp3',"")}'")
        bookmark_track.set(timeline_slider.get())
      
        update_preview_tracktime()
        reload_bookmark_manager_timestamps()


        root.after(0,lambda: animate_open_menu(bookmark_menu,-1,0,True))


def close_bookmark_manager():
    root.after(0,lambda: animate_close_menu(bookmark_menu,0,1,True))

def restore_default_settings():
    scroll_speed_slider.set(default_settings["scroll_speed"])
    bg_blur_slider.set(default_settings["blur_amount"])
    infobar_opacity_slider.set(default_settings["infobar_opacity"])

    use_disc_check.select() if default_settings["use_disc"] else use_disc_check.deselect()
    use_thumbnails_check.select() if default_settings["load_imgs"] else use_thumbnails_check.deselect()
    show_console_startup.select() if default_settings["console_startup"] else show_console_startup.deselect()
    openwith_menu_check.select() if default_settings["openwidth_assigned"] else openwith_menu_check.deselect()


library_loaded = False
library_open = False
def toggle_libary_menu():
    global library_open, library_loaded, in_menu

    if not library_loaded:
        root.configure(cursor="watch")
        root.update_idletasks()
        load_song_library()
        library_loaded = True
        root.configure(cursor="arrow")

    library_open = not(library_open)

    if library_open:
            in_menu = True
            library_menu_frame.place(relheight=1,x=-250,y=0)
            bg_frame.place(relwidth=1,relheight=1)
            close.place_forget()

            bg_frame.lift()
            library_menu_frame.lift()
            library_menu_button.lift()
            
            

    animate_library_menu_open()

    if not library_open:
        in_menu = False
        library_menu_frame.place_forget()
        bg_frame.place_forget()
        close.place(relx=0.95,rely=0.01)

def animate_library_menu_open(time=0): #help why is everyone so mad... its hard to focus
    if time < 50:
        time += 1

        if library_open: #then play open animation
            library_menu_frame.place(x=cubic_out(time/50,-250,0),relheight=1)
            library_menu_button.place(x=cubic_out(time/50,0,250))
            pywinstyles.set_opacity(bg_frame,cubic_out(time/50,0,0.8))

        else: #then open it
            library_menu_frame.place(x=cubic_out(time/50,0,-250),relheight=1)
            library_menu_button.place(x=cubic_out(time/50,250,0))
            pywinstyles.set_opacity(bg_frame,cubic_out(time/50,0.8,0))

        root.after(8,lambda:animate_library_menu_open(time))

current_view_mode = "playlists"
save_playlist_view_directory = GLOBAL_MUSIC_DIR

def find_first_song_origin(name):
    '''find the directory of the first apperance of this song (expected small dir... song.mp3)'''
    directorys = list(song_directorys.keys())
    for cdir in directorys:
        if name in song_directorys[cdir]:
            return cdir
    return None

def crop_square_image(img: Image.Image, size=120):
    width, height = img.size

    scale = max(size / width, size / height)
    new_width = int(width * scale)
    new_height = int(height * scale)

    img = img.resize((new_width, new_height), Image.LANCZOS)

    left = (new_width - size) // 2
    top = (new_height - size) // 2
    right = left + size
    bottom = top + size

    img = img.crop((left, top, right, bottom)) #ok so this is just a thing now i guess.. okay bro

    return img

def clean_directorys_from_sample(songs:list):
    results = []
    for song in songs:
        if valid_audio_name(song):
            results.append(song)
    return results

def clear_recent_playlists(): #and everything else...
    for playlistdata in recent_playlists_widgets:
        song_image,playlist_frame,playlist_title, playlist_lenght = playlistdata

        del song_image
        playlist_frame.destroy()
        playlist_title.destroy()
        playlist_lenght.destroy()

def request_recent_playlist(dir:str):
    global RENDER_INDEX; RENDER_INDEX = 50 #i dont care
    playlists_directory_viewer(customdir=dir)

recent_playlists_widgets = [] #just so i can delete them later
def load_recent_playlists():
    recent_directorys = [] #is the TECHNIAL term for it....

    for recent_song in recent_songs:
        song_origin = find_first_song_origin(recent_song)
        if not song_origin in recent_directorys and song_origin:
            recent_directorys.append(song_origin)

    recent_directorys = recent_directorys[0:5] #is epstin- i mean einstine really dead????
 
    for i in range(len(recent_directorys)):
        current_playlist = recent_directorys[i]
        _, current_playlist_name = os.path.split(current_playlist)
        current_playlist_name = current_playlist_name.replace(".mp3","") #sometimes the thing can glitch out and os.path.splitext returns none...
        target_playlist_contents = clean_directorys_from_sample(song_directorys[current_playlist])
        
        random.seed(seed) #cave jhonson here. the boys back at the lab said that this should get us into some for of "lock system"? Never sure what they're talkin about am i right ah ha.... uhhhggg but uhm anyways 
        song_image_index = random.randint(0,len(target_playlist_contents)-1) #this makes it so that the playlist icon ONLY changes when the progam is reloaded.

        target_song_name = target_playlist_contents[song_image_index]
        song_image, _, _, _ = safeload_song(target_song_name)

        song_image = crop_square_image(song_image)

        song_image = ctk.CTkImage(song_image,size=(120,120)) #i'm running out of names... again..

        playlist_frame = ctk.CTkLabel(recent_playlists_frame,width=120,height=120,corner_radius=5,text="",image=song_image)
        playlist_frame.bind("<Button-1>",lambda event, n=current_playlist: request_recent_playlist(n))
        playlist_frame.bind("<Enter>",bind_select_cursor)
        playlist_frame.bind("<Leave>",bind_leave_cursor)

        playlist_frame.place(x=10+(i*135))

        playlist_title = ctk.CTkLabel(recent_playlists_frame,text=truncate_string(current_playlist_name,18))
        playlist_title.place(x=19+(i*135),y=120)

        playlist_lenght = ctk.CTkLabel(recent_playlists_frame,text=f"{len(target_playlist_contents)} Song{"s" if len(target_playlist_contents) > 1 or len(target_playlist_contents) == 0 else ""}",height=10,font=("",10,"normal"))
        playlist_lenght.place(x=19+(i*135),y=139)

        recent_playlists_widgets.append((song_image,playlist_frame,playlist_title, playlist_lenght))

        random.seed(time.time()) #uh cave jhonson here again... yeah it just works.



def home_directory_viewer():
    #i have a theory-   a song theory.... AAAHHHHHHHHHHHHHHHHHHHHHH

    #ok but fr though i think we can determine the recent playlists without needing
    #to store them somewhere else... lemme think about this for a second

    #done.     and yes, you can do that. so let do it!!1!!!1!! OKOK!

    #ok back here for a second, here is now we gonna choose the image- we make a seed random each time we open teh program...
    #when we choose a random image based off of the name. im thinking maybe like the lenght

    global PLAYING_INDEX, FOCUS_INDEX, GLOBAL_MUSIC_DIR, current_view_mode, save_playlist_view_directory

    if current_view_mode != "home":
        save_playlist_view_directory = GLOBAL_MUSIC_DIR #save for later when the playlist viewer is relaoded, we save where we were
        current_view_mode = "home"

        GLOBAL_MUSIC_DIR = music_path #root dir, prevents backreading, also, i forget to mention this but even since my swtich to vs, i really like the color of constants.. (it just needs to be fully capitolized...) 
        PLAYING_INDEX = None #havent touched this one in a LONNNNNGGG time...
        FOCUS_INDEX = 0

        library_menu_button.configure(state="disabled", image=None)
        add_music_butt.configure(state="disabled")
        home_view_button.configure(fg_color="#4D4D4D")
        directory_view_button.configure(fg_color="#000000")
        home_ui.place_homeframe(homeframe)

        opacity = 1
        pywinstyles.set_opacity(song_title_text,opacity)
        pywinstyles.set_opacity(song_creator_text,opacity)
        pywinstyles.set_opacity(library_menu_button,opacity)
        pywinstyles.set_opacity(directory_view_frame,opacity)

        #reload recent playlists
        clear_recent_playlists()
        load_recent_playlists()

        #recent songs
        #compile all_songs to be recent_songs, but the format should stay the same, theyre just rendered differently...
        all_songs.clear()

        for songname in recent_songs: 
            _, ext = os.path.splitext(songname) #gets the extention (.mp3, "" for directorys)
            if valid_audio_name(ext):
                all_songs.append(safeload_song(songname))
            if ext == "":
                all_songs.append((Image.new("RGBA",size=(1,1)),None,songname,""))

        reload_recents_directory_ui() #dont use regular GLOBAL_MUSIC_DIR
        songframe_option_button.place_forget()


def playlists_directory_viewer(customdir=None):
    global current_view_mode, GLOBAL_MUSIC_DIR, PLAYING_INDEX, RENDER_INDEX, FOCUS_INDEX

    if current_view_mode != "playlists":
        current_view_mode = "playlists"
        update_infobar_opacity()
        homeframe.place_forget()
        library_menu_button.configure(state="normal", image=library_menu_image)
        add_music_butt.configure(state="normal")

        clear_recent_playlists()
        for songframe in recent_frames:
            songframe.destroy()

        home_view_button.configure(fg_color="#000000")
        directory_view_button.configure(fg_color="#4D4D4D")

        if customdir: #used for when a playlist is requested from home menu
            GLOBAL_MUSIC_DIR = customdir
        else:
            GLOBAL_MUSIC_DIR = save_playlist_view_directory

        PLAYING_INDEX = None
        FOCUS_INDEX = 0
        RENDER_INDEX = 100

        reload_current_directory_ui()

def open_appdata_song_dir():
    os.startfile(music_path)


external_import_menu = ctk.CTkFrame(root,border_width=1)

external_menu_close = ctk.CTkButton(external_import_menu,text="❌",fg_color="#2A2A2A",width=30,hover_color="#3C3C3C",command=lambda:animate_close_menu(external_import_menu,0.1,1,True))
external_menu_close.place(relx=0.93,rely=0.02)

external_menu_title = ctk.CTkLabel(external_import_menu,text="Import External File",font=("ariel",18,"bold"))
external_menu_title.place(relx=0.02,rely=0.02)

external_details_frame = ctk.CTkFrame(external_import_menu,fg_color="#1C1C1C")
external_details_frame.place(relx=0.05,relwidth=0.9,rely=0.2,relheight=0.6)

external_song_imagelabel = ctk.CTkLabel(external_details_frame,text="",fg_color="#101010",width=100,height=100,corner_radius=5)
external_song_imagelabel.place(relx=0.02,rely=0.05)

external_song_songtitle = ctk.CTkEntry(external_details_frame,placeholder_text="Song Title",font=("ariel",19,"bold"),width=300,border_width=1,border_color="#949A9F")
external_song_songtitle.place(relx=0.02,rely=0.05,x=115)
external_song_songauthor = ctk.CTkLabel(external_details_frame,text="songauthor",font=("ariel",13,"bold"))
external_song_songauthor.place(relx=0.02,rely=0.2,x=115)
external_song_path = ctk.CTkLabel(external_details_frame,text="songpath",font=("ariel",13,"bold"))
external_song_path.place(relx=0.02,rely=0.3,x=115)

external_song_import_feedback = ctk.CTkLabel(external_details_frame,text="",font=("ariel",13,"bold"),text_color="red")
external_song_import_feedback.place(relx=0.02,rely=0.4,x=115)

external_song_add_to_cdir_check = ctk.CTkCheckBox(external_import_menu,text="Add to Current Directory")
external_song_add_to_cdir_check.place(relx=0.05,rely=0.85)
external_song_add_to_cdir_check.select()

external_song_import_youtube_button = ctk.CTkButton(external_import_menu,text="Import",border_width=1,fg_color="#2B2B2B",hover_color="#1C1B1B")
external_song_import_youtube_button.place(relx=0.7,rely=0.85)

external_import_menu.place(relx=0.1,relwidth=0.8,rely=1,relheight=0.8)

def import_external_song(path,name):
    if all_songs == []:
        kickstart_song_systems()

    external_song_import_feedback.configure(text="")
    fullname = name.get()+".mp3"
    if name.get().strip() == "":
        external_song_import_feedback.configure(text="Song name cannot be empty.")
    else:    
        try:
            shutil.copy(path,os.path.join(music_path,fullname))

            lw_add_song(fullname,external_song_add_to_cdir_check.get())
            animate_close_menu(external_import_menu,0.1,1,True)
        except Exception as e:
            external_song_import_feedback.configure(text=f"An error occurred: \n{e}")
    



def open_import_menu(path:str): #called from mutinstance callback
    root.focus_force()
    root.attributes("-topmost",True)
    root.attributes("-topmost",False)

    songname = os.path.splitext(os.path.basename(path))[0]
    song = safeload_song(path,usedir=True)

    external_song_image = ctk.CTkImage(crop_square_image(song[0],size=100),size=(100,100))
    external_song_imagelabel.configure(image=external_song_image)

    external_song_songtitle.delete(0,ctk.END)
    external_song_songtitle.insert(ctk.END,songname)

    external_song_songauthor.configure(text=song[3])
    external_song_path.configure(text=path)

    external_song_import_youtube_button.configure(command=lambda:import_external_song(path,external_song_songtitle))

    bg_frame.place(relwidth=1,relheight=1)
    close.place_forget()

    bg_frame.lift()
    external_import_menu.lift()
    animate_open_menu(external_import_menu,-1,0.1,True)
    

#-----------------------------------------------------------------------
#UI ELEMENTS-----------------------------------------------------------------------
#-----------------------------------------------------------------------
bgimage = ctk.CTkImage(Image.new("RGB",size=(1,1)),size=(1,1))
bglabel = ctk.CTkLabel(root,image=bgimage,text="")
bglabel.place(relwidth=1,relheight=1,x=0,y=0)

bottom_options_bar = ctk.CTkFrame(root,width=300,height=35,border_width=2,bg_color="#474747")
bottom_options_bar.place(relx=-0.02,rely=0.86)

bottom_timeline_bar = ctk.CTkFrame(root,width=400,height=35,border_width=2,bg_color="#474747")
bottom_timeline_bar.place(relx=-0.02,rely=0.93)

song_title_text = ctk.CTkLabel(root,font=("ariel",35,"bold"),text="",anchor="w")
song_title_text.place(relx=0,rely=0,x=30,relwidth=1)

song_creator_text = ctk.CTkLabel(root,font=("ariel",19,"bold"),text="",anchor="w")
song_creator_text.place(relx=0,y=41,x=30,relwidth=1)

directory_view_frame = ctk.CTkFrame(root,fg_color="#000000",height=68,corner_radius=0)
directory_view_frame.place(relx=0.75,rely=0,x=30,relwidth=0.25)
directory_view_frame.propagate(False)

home_view_button = ctk.CTkButton(directory_view_frame,text="Home",fg_color="#000000",hover_color="#232323",width=95,height=20,command=home_directory_viewer)
home_view_button.place(x=10,y=10)
directory_view_button = ctk.CTkButton(directory_view_frame,text="Playlists",fg_color="#4D4D4D",hover_color="#232323",width=95,height=20,command=playlists_directory_viewer)
directory_view_button.place(x=10,y=37)

library_menu_image = ctk.CTkImage(Image.open(resource_path("assets/libarary_menu.png")), size=(16,16))
library_menu_button = ctk.CTkButton(root,corner_radius=0,text="",image=library_menu_image,width=30,fg_color="#000000",height=69,hover_color="#2B2B2B",command=toggle_libary_menu)
library_menu_button.place(x=0,y=0)

homeframe, recent_songs_frame, recent_playlists_frame = home_ui.main(root)
###---------------------------------------------------------------------------------
###BOTTOM OPTIONS BAR:  ------------------------------------------------------------------------

seek_previous_song_image = ctk.CTkImage(Image.open(resource_path("assets/previous_focus.png")), size=(14,14))
seek_previous_song_butt = ctk.CTkButton(bottom_options_bar,text="",image=seek_previous_song_image,fg_color="#2B2B2B",hover_color="#1a1a1a",width=5,command=skip_backwards_song)
seek_previous_song_butt.place(relx=0.12,rely=0.05)

seek_next_song_image = ctk.CTkImage(Image.open(resource_path("assets/next_focus.png")), size=(14,14))
seek_next_song_butt = ctk.CTkButton(bottom_options_bar,text="",image=seek_next_song_image,fg_color="#2B2B2B",hover_color="#1a1a1a",width=5,command=skip_next_song)
seek_next_song_butt.place(relx=0.195,rely=0.05)

random_song_butt_image = ctk.CTkImage(Image.open(resource_path("assets/shuffle v2.png")), size=(14,14))
random_song_butt = ctk.CTkButton(bottom_options_bar,text="",fg_color="#2B2B2B",hover_color="#1a1a1a",width=5,command=random_song,image=random_song_butt_image)
random_song_butt.place(relx=0.27,rely=0.05)

restart_song_image = ctk.CTkImage(Image.open(resource_path("assets/restart.png")), size=(14,14))
restart_song_button = ctk.CTkButton(bottom_options_bar,fg_color="#2B2B2B",text="",hover_color="#1a1a1a",image=restart_song_image,width=5,command=restart_current_song)
restart_song_button.place(relx=0.345,rely=0.05)

bookmark_manager_image = ctk.CTkImage(Image.open(resource_path("assets/bookmark.png")), size=(14,14))
bookmark_manager_button = ctk.CTkButton(bottom_options_bar,fg_color="#2B2B2B",text="",hover_color="#1a1a1a",image=bookmark_manager_image,width=5,command=show_bookmark_manager)
bookmark_manager_button.place(relx=0.505,rely=0.05)

settings_button = ctk.CTkButton(bottom_options_bar,fg_color="#2B2B2B",hover_color="#1a1a1a",text="⚙️",width=25,command=show_settings_menu,height=15,font=("ariel",15,"bold"))
settings_button.place(relx=0.59,rely=0.05)

after_song_mode = ctk.CTkOptionMenu(bottom_options_bar,values=("Shuffle","Loop","Next","Wait"),fg_color="#1a1a1a",dropdown_fg_color="#1a1a1a",button_color="#1a1a1a",button_hover_color="#333333")
after_song_mode.place(relx=0.7,relwidth=0.29,rely=0.09,relheight=0.67)

###---------------------------------------------------------------------------------
###BOTTOM TIMELINE BAR---------------------------------------------------------------------------------

pause_butt = ctk.CTkButton(bottom_timeline_bar,text="▶️",fg_color="#2B2B2B",hover_color="#1a1a1a",width=5,command=manage_pause)
pause_butt.place(relx=0.04,rely=0.05)

timeline_slider = ctk.CTkSlider(bottom_timeline_bar,command=seek_pos)
timeline_slider.place(relx=0.1,rely=0.2,relwidth=0.7)
timeline_slider.set(0)

timelime_label = ctk.CTkLabel(bottom_timeline_bar,fg_color="transparent",text="")
timelime_label.place(relx=0.79,rely=0.05,relwidth=0.2)
timeline_slider.lift()

def export_song_directorys():
    export_target = fd.askdirectory(mustexist=True,title="Select Export Location").replace("\\","/")

    if export_target:
        mixer.music.stop()
        mixer.music.unload()

        export_directorys = list(song_directorys.keys())
        export_directorys = sorted(export_directorys, key=len)

        safe_mkdir(os.path.join(export_target,"music"))
        for cdir in export_directorys:
            cdir = cdir.replace(placeify_path,"").replace("\\","/").lstrip("/")
            target_export_directory = os.path.join(export_target,cdir)

            safe_mkdir(target_export_directory)

        for cdir in export_directorys:
            cdir_songs = song_directorys[cdir]

            cdir = cdir.replace(placeify_path,"").replace("\\","/").lstrip("/")
            target_export_directory = os.path.join(export_target,cdir)
            
            for song in cdir_songs:
                source_location = os.path.join(music_path,song)
                export_location = os.path.join(target_export_directory,song)
                if valid_audio_name(song):
                    try:
                        shutil.copy(source_location,export_location)
                    except:
                        pass

###---------------------------------------------------------------------------------
###SETTINGS MENU---------------------------------------------------------------------------------
def update_scrollspeed_text(event=None):
    scroll_speed_title.configure(text=f"Scroll Interpolation: {round(scroll_speed_slider.get()*100)}")
def update_bluramount_text(event=None):
    bg_blur_title.configure(text=f"BG Blur Amount: {round(bg_blur_slider.get()*100)}")
def update_infobar_opacity(event=None):
    opacity = round(infobar_opacity_slider.get()*100,2)
    infobar_opacity_title.configure(text=f"Info Bar Opacity: {opacity}")
    
    pywinstyles.set_opacity(song_title_text,opacity)
    pywinstyles.set_opacity(song_creator_text,opacity)
    pywinstyles.set_opacity(library_menu_button,opacity)
    pywinstyles.set_opacity(directory_view_frame,opacity)

settmenu = ctk.CTkScrollableFrame(root,border_width=2,bg_color="#474747")

setting_title = ctk.CTkLabel(settmenu,text="Settings",font=("aeril",28,"bold"))
setting_title.pack(anchor="w")

settings_title_separator = ctk.CTkFrame(settmenu,width=650,height=2,fg_color="#666666")
settings_title_separator.pack(padx=10,pady=(4,2))

setting_title = ctk.CTkLabel(settmenu,text="Visibility and UI",font=("aeril",28,"normal"))
setting_title.pack(anchor="w",pady=(25,9))

scroll_speed_title = ctk.CTkLabel(settmenu,text=f"Scroll Interpolation: {8}",font=("aeril",19,"normal"))
scroll_speed_title.pack(anchor="w")

scroll_speed_slider = ctk.CTkSlider(settmenu,width=600,command=update_scrollspeed_text,from_=0, to=0.20)
scroll_speed_slider.pack(anchor="w")
scroll_speed_slider.set(safe_settings_grab("scroll_speed"))

infobar_opacity_title = ctk.CTkLabel(settmenu,text=f"Info Bar Opacity: {0}",font=("aeril",19,"normal"))
infobar_opacity_title.pack(anchor="w")

infobar_opacity_slider = ctk.CTkSlider(settmenu,width=600,command=update_infobar_opacity,from_=0, to=0.01)
infobar_opacity_slider.pack(anchor="w")
infobar_opacity_slider.set(safe_settings_grab("infobar_opacity"))

bg_blur_title = ctk.CTkLabel(settmenu,text=f"BG Blur Amount: {25}",font=("aeril",19,"normal"))
bg_blur_title.pack(anchor="w")

bg_blur_slider = ctk.CTkSlider(settmenu,width=600,command=update_bluramount_text,from_=0.01, to=0.35)
bg_blur_slider.pack(anchor="w")
bg_blur_slider.set(safe_settings_grab("blur_amount"))

#lowk useless and didnt work so uh..        deprecated lmao
#img_load_meathod_title = ctk.CTkLabel(settmenu,text=f"Thumbnail loading method:",font=("aeril",19,"normal"))
#img_load_meathod_title.pack(anchor="w")

#img_load_meathod_dropdown = ctk.CTkOptionMenu(settmenu,width=600,command=update_bluramount_text,values=["Utilize image Queue","Wait for images, then update"],fg_color="#4A4D50",button_color="#696969",button_hover_color="#202020")
#img_load_meathod_dropdown.pack(anchor="w")


privacy_title_separator = ctk.CTkFrame(settmenu,width=650,height=2,fg_color="#666666")
privacy_title_separator.pack(padx=10,pady=(25,7))

privacy_title = ctk.CTkLabel(settmenu,text="Privacy",font=("aeril",28,"normal"))
privacy_title.pack(anchor="w",pady=(25,9))

def notify_disc_restart():
    if safe_settings_grab("use_disc") != use_disc_check.get():
        use_disc_check.configure(text="Use Discord Rich Presence *requires restart to take effect")
    else:
        use_disc_check.configure(text="Use Discord Rich Presence")
use_disc_check = ctk.CTkCheckBox(settmenu,text=f"Use Discord Rich Presence",font=("aeril",19,"normal"),command=notify_disc_restart)
use_disc_check.pack(anchor="w")
if safe_settings_grab("use_disc"):
    use_disc_check.select()

use_thumbnails_check = ctk.CTkCheckBox(settmenu,text=f"Load Thumbnails",font=("aeril",19,"normal"))
use_thumbnails_check.pack(anchor="w")
if safe_settings_grab("load_imgs"):
    use_thumbnails_check.select()

show_console_startup = ctk.CTkCheckBox(settmenu,text=f"Open Console on startup",font=("aeril",19,"normal"))
show_console_startup.pack(anchor="w")
if safe_settings_grab("console_startup"):
    show_console_startup.select()

update_bluramount_text()
update_scrollspeed_text()
update_infobar_opacity()

close_settings_menu_butt = ctk.CTkButton(settmenu,text="❌",fg_color="#2B2B2B",hover_color="grey",bg_color="#2B2B2B",width=20,command=close_settings_menu)

restor_default_settings_butt = ctk.CTkButton(settmenu,text="Restore Defaults",fg_color="#2B2B2B",hover_color="grey",bg_color="#2B2B2B",width=20,command=restore_default_settings)

#THEMES!!!! - actually- no. im too lazy for that rn.. i mean.. who REALLY needs those anyways?
#setting_title_separator = ctk.CTkFrame(settmenu,width=650,height=2,fg_color="#666666")
#setting_title = ctk.CTkLabel(settmenu,text="Themes",font=("aeril",28,"normal"))
#setting_title.pack(anchor="w",pady=(25,9))

setting_title_separator = ctk.CTkFrame(settmenu,width=650,height=2,fg_color="#666666")
setting_title_separator.pack(padx=10,pady=(25,7))
setting_title = ctk.CTkLabel(settmenu,text="Data Management",font=("aeril",28,"normal"))
setting_title.pack(anchor="w",pady=2)

yt_location_title = ctk.CTkLabel(settmenu,text="Download Location:")
yt_location_title.pack(anchor="w")

yt_location_entry = ctk.CTkEntry(settmenu,border_width=1,width=650)
yt_location_entry.pack(anchor="w")
yt_location_entry.insert(ctk.END,f"/{music_path}")
yt_location_entry.configure(state="disabled")

yt_output_dir_button = ctk.CTkButton(yt_location_entry,text="📂",width=15,border_width=1,border_color="#565B5E",fg_color="#343638",hover_color="#1a1a1a",bg_color="#565B5E",command=open_appdata_song_dir)
yt_output_dir_button.place(relx=1,rely=0,x=-26)

export_song_directorys_button = ctk.CTkButton(settmenu,text="Export Data",fg_color="#2B2B2B",hover_color="#212121",border_width=1,command=export_song_directorys)
export_song_directorys_button.pack(anchor="w",pady=5)

#import_song_button = ctk.CTkButton(settmenu,text="Import Song",fg_color="#2B2B2B",hover_color="#212121",border_width=1,command=None)
#import_song_button.pack(anchor="w",pady=5)

close_settings_menu_butt.place(relx=0.95,rely=0.01)
restor_default_settings_butt.place(relx=0.78,rely=0.01)

experimental_title_separator = ctk.CTkFrame(settmenu,width=650,height=2,fg_color="#FF7403") #about the orangest orange can get
experimental_title_separator.pack(padx=10,pady=(25,7))
setting_title = ctk.CTkLabel(settmenu,text="Experimental",font=("aeril",28,"normal"))
setting_title.pack(anchor="w",pady=2)

def openwith_menu_assignment_update():
    if openwith_menu_check.get():
        changelogs.register_open_with(get_exe_path())
    else:
        changelogs.unregister_open_with(get_exe_path())

openwith_menu_check = ctk.CTkCheckBox(settmenu,text="Assign Placeify to 'Open With' Menu",font=("aeril",19,"normal"),command=openwith_menu_assignment_update)
openwith_menu_check.pack(anchor="w",pady=5)
if safe_settings_grab("openwidth_assigned"):
    openwith_menu_check.select()

shortcut_maker_button = ctk.CTkButton(settmenu,text="Create Desktop Shortcut",fg_color="#2B2B2B",hover_color="#212121",border_width=1,command=lambda:changelogs.make_shortcut(get_exe_path(),placeify_ico,"Placeify"))
shortcut_maker_button.pack(anchor="w",pady=5)


###---------------------------------------------------------------------------------
#LIBRARY SIDE MENU------------------------------------------------------------------
library_menu_frame = ctk.CTkFrame(root,fg_color="black",corner_radius=0,width=250)


library_menu_title = ctk.CTkLabel(library_menu_frame,text="Library",font=("Seagoe UI",15,"bold"))
library_menu_title.place(x=5,y=4)

library_menu_info = ctk.CTkLabel(library_menu_frame,text="84 Songs ",font=("Seagoe UI",15,"bold"),anchor="e")
library_menu_info.place(relwidth=1,y=4)
library_menu_title.lift()

def search_library_menu(event):
    query = library_menu_seartch.get()
    if query != "":        
        for widget in library_songs: 
            widget[0].pack_forget()

        for song_data in library_songs:
            if query.lower() in song_data[1].lower():
                song_data[0].pack(fill="x", pady=5)
        library_song_menu._parent_canvas.yview_moveto(0)
    else:
        for song_data in library_songs:
            song_data[0].pack(fill="x", pady=5)



library_menu_seartch = ctk.CTkEntry(library_menu_frame,width=237)
library_menu_seartch.place(x=5,y=30)
library_menu_seartch.bind("<KeyRelease>",search_library_menu)

library_song_menu = ctk.CTkScrollableFrame(library_menu_frame,corner_radius=0,fg_color="#000000")
library_song_menu.place(relwidth=1,relheight=0.8,y=60)

def append_library_song_to_current_dir():
    lw_append_song_to_cdir(current_song_hover)

add_song_to_library_button = ctk.CTkButton(library_song_menu,text="➕",fg_color="#000000",text_color="#ffffff",width=30,corner_radius=15,hover_color="#a2a1a1",bg_color="#252525",command=append_library_song_to_current_dir) #radius is half the diameter- to half the width is the corner radius :DDD
play_song_from_library_button = ctk.CTkButton(library_song_menu,text="▶️",fg_color="#000000",text_color="#ffffff",width=1,corner_radius=15,hover_color="#a2a1a1",bg_color="#252525",command=play_current_selected_library_song)
remove_song_from_library_button = ctk.CTkButton(library_song_menu,text="🗑️",fg_color="#000000",text_color="#ffffff",width=1,corner_radius=15,hover_color="#a2a1a1",bg_color="#252525",command=delete_from_library_menu) #radius is half the diameter- to half the width is the corner radius :DDD
###---------------------------------------------------------------------------------
###GENERAL FOCUS MENUS --------------------------------------------------------
def close_musicmenu():
    animate_close_menu(musicmenu,0.1,1,True)

bg_frame = ctk.CTkFrame(root,fg_color="black")
pywinstyles.set_opacity(bg_frame, value=0.8)

close = ctk.CTkButton(bg_frame,text="❌",fg_color="black",hover_color="grey",width=20,command=close_musicmenu)
close.place(relx=0.95,rely=0.01)

def add_bookmark():
    global bookmarks

    current_songname = CURRENT_TRACKDATA[2]
    song_has_bookmarkdata = find_bookmarks_from_songname(current_songname) # get from name
    if song_has_bookmarkdata != None: #if data is already written for it
        for i in range(len(bookmarks)):
            if bookmarks[i]["song"] == current_songname:
                bookmarks[i]["timestamps"].append(bookmark_track.get())
                bookmarks[i]["names"].append(bookmark_name_entry.get())

                print("appended bookmark")
                
    else:
        bookmarks.append({
            "song":current_songname,
            "timestamps":[bookmark_track.get()],
            "names":[bookmark_name_entry.get()]
            })
        print("created new entry")

    root.after(0,lambda: animate_close_menu(bookmark_menu,0,1,True)) #this function is only acsessed though the add button.     or atleast i hope, i dunno ill probs forget aboutit then itll turn into an issue later
    reload_bookmarks()

###---------------------------------------------------------------------------------
###🔖BOOKMAKRS --------------------------------------------------------
bookmark_menu = ctk.CTkFrame(root,border_width=2,bg_color="#474747")

bookmark_title = ctk.CTkLabel(bookmark_menu,text="Bookmarks",font=("aeril",28,"bold"))
bookmark_title.place(x=15,y=15)

bookmark_target = ctk.CTkLabel(bookmark_menu,text=f"'  -  {"if you're' seeing this, then i fricked something up"}'",font=("aeril",13,"bold"))
bookmark_target.place(x=170,y=20)

track_instuction = ctk.CTkLabel(bookmark_menu,text="Adjust the track for the position of this bookmark",font=("aeril",13,"bold"))
track_instuction.place(relx=0.02,rely=0.3)

bookmark_track_frame = ctk.CTkFrame(bookmark_menu,height=50)
bookmark_track_frame.place(relx=0.02,rely=0.4,relwidth=0.9)

bookmark_track = ctk.CTkSlider(bookmark_track_frame,command=update_preview_tracktime)
bookmark_track.place(relx=0,rely=0.4,relwidth=1)

bookmark_timestamp_preview = ctk.CTkLabel(bookmark_menu,text="345/345",font=("aeril",13,"bold"),fg_color="#202020",corner_radius=5,width=90)
bookmark_timestamp_preview.place(relx=0.8,rely=0.3)

bookmark_name_instuction = ctk.CTkLabel(bookmark_menu,text="Name your bookmark",font=("aeril",13,"bold"))
bookmark_name_instuction.place(relx=0.02,rely=0.57)

bookmark_name_entry = ctk.CTkEntry(bookmark_menu,border_width=2)
bookmark_name_entry.place(relx=0.02,rely=0.65,relwidth=0.9)
bookmark_name_entry.insert(ctk.END,"That good part")

add_bookmark_button = ctk.CTkButton(bookmark_menu,text="Add",border_width=2,fg_color="#2B2B2B",hover_color="#1a1a1a",command=add_bookmark)
add_bookmark_button.place(relx=0.72,rely=0.85)


close_bookmark_menu_butt = ctk.CTkButton(bookmark_menu,text="❌",fg_color="#2B2B2B",hover_color="grey",bg_color="#2B2B2B",width=20,command=close_bookmark_manager)
close_bookmark_menu_butt.place(relx=0.945,rely=0.01)
###---------------------------------------------------------------------------------
### ADD DATA MENU ----------------------------------------------------------
musicmenu = ctk.CTkFrame(root,border_width=2)
def add_music_menu():
    bg_frame.place(relwidth=1,relheight=1)
    
    musicmenu.place(relx=0.1,relwidth=0.8,
                rely=1,relheight=0.8)
    close.place(relx=0.95,rely=0.01)

    bg_frame.lift()
    musicmenu.lift()
    animate_open_menu(musicmenu,-1,0.1,True)

def set_volume_slider(event=None):
    mixer.music.set_volume(volume_slider.get()/2.5)

volume_frame = ctk.CTkFrame(root,corner_radius=5,border_width=2,bg_color="#474747")
volume_frame.place(relx=0,rely=0.565,relwidth=0.04,relheight=0.3)

volume_slider = ctk.CTkSlider(volume_frame,orientation="vertical",command=set_volume_slider)
volume_slider.place(relx=0.2,rely=0.02,relheight=0.95)
volume_slider.set(0.55)
set_volume_slider()

add_music_butt = ctk.CTkButton(bottom_options_bar,fg_color="#2B2B2B",hover_color="#1a1a1a",text="➕",width=25,command=add_music_menu)
add_music_butt.place(relx=0.037,rely=0.05)

library_menu_frame.lift()
# ADD MUSIC MENU THINGS:----------------------------------------------------------------
def profile_import_menu(menu_obj):
    from_yt_button.configure(fg_color="#2B2B2B")
    directory_menu_button.configure(fg_color="#2B2B2B")
    from_spotify_button.configure(fg_color="#2B2B2B")

    spotify_import_frame.place_forget()
    yt_import_frame.place_forget()
    create_directory_frame.place_forget()

    bg_frame.lift()
    musicmenu.lift()

    if menu_obj is yt_import_frame:
        yt_import_frame.place(relx=0,rely=0.12,relwidth=1,relheight=0.88)
        from_yt_button.configure(fg_color="#0A0A0A")
    if menu_obj is create_directory_frame:
        create_directory_frame.place(relx=0,rely=0.12,relwidth=1,relheight=0.88)
        directory_menu_button.configure(fg_color="#0A0A0A")
    if menu_obj is spotify_import_frame:
        spotify_import_frame.place(relx=0,rely=0.12,relwidth=1,relheight=0.88)
        from_spotify_button.configure(fg_color="#0A0A0A")

######  YOUTUBE
    
from_yt_button = ctk.CTkButton(musicmenu,text="YouTube Download",border_width=1.5,fg_color="#2B2B2B",border_color="#666666",hover_color="#1a1a1a",font=("areil",16,"bold"),command=lambda:profile_import_menu(yt_import_frame))
from_yt_button.place(relx=0.02,rely=0.02)

yt_import_frame = ctk.CTkFrame(musicmenu,border_width=2,background_corner_colors=("#474747","#474747","black","black")) # im geniouse
yt_import_frame.place(relx=0,rely=0.12,relwidth=1,relheight=0.88)

yt_url_title = ctk.CTkLabel(yt_import_frame,text="YouTube URL")
yt_url_title.place(relx=0.05,rely=0.05)

yt_url_entry = ctk.CTkEntry(yt_import_frame,border_width=1,placeholder_text="https://youtu.be/A-bCDEFG?si=HIJK")
yt_url_entry.place(relx=0.05,rely=0.15,relwidth=0.88) 

import_status = ctk.CTkLabel(yt_import_frame,text="",text_color="red",wraplength=330)
import_status.place(relx=0.2,rely=0.05)
import_status.lift()

yt_add_to_cdir = ctk.CTkCheckBox(yt_import_frame,text="Add to Current Playlist")
yt_add_to_cdir.place(relx=0.05,rely=0.3)
yt_add_to_cdir.select()

yt_playlist_check = ctk.CTkCheckBox(yt_import_frame,text="Playlist")
yt_playlist_check.place(relx=0.05,rely=0.4)

yt_import_console = ctk.CTkTextbox(yt_import_frame,fg_color="#101010",text_color="white",corner_radius=5)
yt_import_console.place(relx=0.05,rely=0.52,relwidth=0.88,relheight=0.3)
yt_import_console.configure(state="disabled")

def thread_download_yt(safe_url):
    import_youtube_button.configure(text="Downloading...",state="disabled")
    try:
        info, final_path = download_youtube(safe_url)

        if yt_playlist_check.get():
            entries = info.get("entries")
            for entry in entries:
                songname = entry.get("title")
                songfile = songname+".mp3"

                lw_add_song(songfile,yt_add_to_cdir.get())
                print(f"yt playlist import: {songfile}")
        else:
            lw_add_song(final_path,yt_add_to_cdir.get()) 
        close_focus_menus()
        
        import_status.configure(text="Video Imported Successfully!",text_color="green")
    except yt_dlp.utils.DownloadError as e:
        import_status.configure(text=f"Invalid URL - DownloadError",text_color="red")
    finally:
        import_youtube_button.configure(text="Import",state="normal")

    with open(directorys_path, "w") as f:
        f.write(json.dumps(song_directorys))

def import_youtube():
    sus_url = yt_url_entry.get()

    if sus_url.strip() == "":
        import_status.configure(text="URL is empty!",text_color="red")
        return
    if not("https://" in sus_url and "youtu" in sus_url):
        import_status.configure(text="Invalid URL!",text_color="red")
        return
    
    import_status.configure(text="Importing... This could take awhile.",text_color="white")
    root.update() # dosnt update till this ends. which is slowed by the download

    threading.Thread(target=thread_download_yt,args=(sus_url,)).start()
        
import_youtube_button = ctk.CTkButton(yt_import_frame,text="Import",width=80,height=26,border_width=1,fg_color="#2B2B2B",hover_color="#1a1a1a",command=import_youtube,font=("Inter",14,"bold"))
import_youtube_button.place(relx=0.05,rely=0.85,relwidth=0.88)

def dir_exists(name):
    all_dirs = list(song_directorys.keys())
    return True if name in all_dirs else False
 
###### :ADD DIRECTORY
def create_dir():
    dir_status.configure(text="",text_color="white")

    target_name = dirname.get().strip()
    target_path = os.path.join(GLOBAL_MUSIC_DIR,target_name)


    if target_name == "":
        dir_status.configure(text="Cannot create directory with empty name.",text_color="red")
        return 

    if dir_exists(target_path):
        dir_status.configure(text="That directory already exists!",text_color="red")
        return 

    if "/" in target_name:
        dir_status.configure(text="Directorys cannot contain a path defining character. (' / ') ",text_color="red")
        return 

    song_directorys[target_name] = []
    song_directorys[GLOBAL_MUSIC_DIR].append(target_name)

    reload_current_directory_ui()
    close_focus_menus()

    """ #uh yeah no not right now...
    buildpath = GLOBAL_MUSIC_DIR
    subdirs = dirname.get().split("/")
    
    song_directorys[buildpath].append(subdirs[0])
    for i in range(len(subdirs)):
        cdirname = subdirs[i]
        buildpath = os.path.join(buildpath,cdirname)

        if dir_exists(buildpath):
            dir_status.configure(text="That directory already exists!",text_color="red")
            return
        if cdirname.get().strip() == "":
            dir_status.configure(text="Path build cancelled, path cannot be empty.",text_color="red")
            return 

        if i < len(subdirs)-1:
            song_directorys[buildpath] = []
            song_directorys[buildpath].append(subdirs[i+1])
    """
    

create_directory_frame = ctk.CTkFrame(musicmenu,border_width=2,background_corner_colors=("#474747","#474747","black","black"))

dirtitle = ctk.CTkLabel(create_directory_frame,text="Enter Directory Name:",font=("aeril",28,"bold"))
dirtitle.place(relx=0.05,rely=0.1)

dirname = ctk.CTkEntry(create_directory_frame,placeholder_text="Type directory name here",font=("aeril",22,"bold"))
dirname.place(relx=0.05,rely=0.25,relwidth=0.8)

dir_status = ctk.CTkLabel(create_directory_frame,text="",text_color="red",font=("areial",14,"bold"))
dir_status.place(relx=0.02,rely=0.85)

import_dir_button = ctk.CTkButton(create_directory_frame,text="Add Directory",border_width=2,fg_color="#2B2B2B",hover_color="#1a1a1a",command=create_dir)
import_dir_button.place(relx=0.72,rely=0.85)

directory_menu_button = ctk.CTkButton(musicmenu,text="Create Directory",border_width=2,border_color="#666666",fg_color="#2B2B2B",hover_color="#1a1a1a",font=("areil",16,"bold"),command=lambda:profile_import_menu(create_directory_frame))
directory_menu_button.place(relx=0.68,rely=0.02)

###### SPOTIFY:
from_spotify_button = ctk.CTkButton(musicmenu,text="Spotify Download",border_width=1.5,fg_color="#2B2B2B",border_color="#666666",hover_color="#1a1a1a",font=("areil",16,"bold"),command=lambda:profile_import_menu(spotify_import_frame))
from_spotify_button.place(relx=0.35,rely=0.02)

spotify_import_frame = ctk.CTkFrame(musicmenu,border_width=2,background_corner_colors=("#474747","#474747","black","black")) # ok im back to nameing things normally cuz i realize that bad names are bad for 1000 lines of code..
spotify_import_frame.place(relx=0,rely=0.12,relwidth=1,relheight=0.88)

spotify_url_title = ctk.CTkLabel(spotify_import_frame,text="Spotify Album/Playlist/Track URL")
spotify_url_title.place(relx=0.05,rely=0.05)

spotify_url_entry = ctk.CTkEntry(spotify_import_frame,border_width=1,placeholder_text="https://open.spotify.com/playlist/1RO5K4woAzDsGGugGgwd8X")
spotify_url_entry.place(relx=0.05,rely=0.15,relwidth=0.55) 

spotify_import_status = ctk.CTkLabel(spotify_import_frame,text="",text_color="red",wraplength=330)
spotify_import_status.place(relx=0.2,rely=0.05)
spotify_import_status.lift()

spotify_location_title = ctk.CTkLabel(spotify_import_frame,text="Download Location:")
spotify_location_title.place(relx=0.05,rely=0.3)

spotify_location_entry = ctk.CTkEntry(spotify_import_frame,border_width=1)
spotify_location_entry.place(relx=0.05,rely=0.4,relwidth=0.55)
spotify_location_entry.insert(ctk.END,f"/{music_path}")
spotify_location_entry.configure(state="disabled")

spotify_add_to_cdir_check = ctk.CTkCheckBox(spotify_import_frame,text="Add to current playlist")
spotify_add_to_cdir_check.place(relx=0.05,rely=0.54)

spotify_output_dir_button = ctk.CTkButton(spotify_location_entry,text="📂",width=15,border_width=1,border_color="#565B5E",fg_color="#343638",hover_color="#1a1a1a",bg_color="#565B5E",command=open_appdata_song_dir)
spotify_output_dir_button.place(relx=0.92,rely=0)

spotify_import_console = ctk.CTkScrollableFrame(spotify_import_frame,fg_color="#101010",corner_radius=5)
spotify_import_console.place(relx=0.65,rely=0.05,relwidth=0.32,relheight=0.71)


#spotify_dlp_creds_button = ctk.CTkButton(spotify_import_frame,text="API Keys",width=80,height=26,border_width=1,fg_color="#2B2B2B",hover_color="#1a1a1a",font=("Inter",14,"bold"))

#made a whole damn menu just to discover that this shi dont work with spotify....
#it was good looking too...

#spotify_dlp_creds_button.place(relx=0.05,rely=0.85,relwidth=0.3) #spotify-dlp can suck my di-     megpoids.  uh.. yeah..

def download_track_from_search(title, artist, output_dir, ffmpeg_path):
    print(f"downloadin {title}")

    # same sanitizing yt-dlp uses (turns "/" into the lookalike ⧸, etc.)
    safe_name = sanitize_filename(title)
    base_path = os.path.join(output_dir, safe_name)
    final_path = base_path + ".mp3"

    # '%' has special meaning in outtmpl, so escape it
    outtmpl = base_path.replace("%", "%%") + ".%(ext)s"

    ydl_opts = {
        "format": "bestaudio/best",
        "postprocessors": [
            {"key": "FFmpegExtractAudio", "preferredcodec": "mp3"},
            {"key": "FFmpegThumbnailsConvertor", "format": "jpg"},
            {"key": "EmbedThumbnail"},
            {"key": "FFmpegMetadata"},
        ],
        "writethumbnail": True,
        "ffmpeg_location": ffmpeg_path,
        "outtmpl": outtmpl,
        "js_runtimes": {"deno": {"path": deno_path}},
        "remote_components": ["ejs:github"],
        "noplaylist": True,
    }

    # clean up weird whitespace like \xa0
    artist = " ".join(artist.split())          # cleans \xa0 etc.
    first_artist = artist.split(",")[0].strip() 

    queries = [
        f"ytsearch1:{artist} - {title} audio",
        f"ytsearch1:{title} - {artist}audio",
        f"ytsearch1:{first_artist} - {title}",
        f"ytsearch1:{first_artist} {title} official",
        f"ytsearch1:{title} {first_artist}",
    ]

    info = None
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        for q in queries:
            result = ydl.extract_info(q, download=False)   # just check first
            if result.get("entries"):
                info = ydl.extract_info(q, download=True)  # found one, download it
                break

    if info is None:
        raise RuntimeError(f"No search results for '{artist} - {title}'")

    if not os.path.exists(final_path):
        raise FileNotFoundError(f"Expected file not found: {final_path}")

    try:
        tags = EasyID3(final_path)
        tags["title"] = title
        tags["artist"] = artist
        tags.save()
    except:
        print("failed to write data to song")

    return info["entries"][0], final_path

spotify_import_labels = []
def reload_spotify_import_statuses(songs):
    for widget in spotify_import_labels:
        widget.destroy()
    spotify_import_labels.clear()

    for data in songs:
        label = ctk.CTkLabel(spotify_import_console,text=" "+data["title"],fg_color="#222222",anchor="w",width=360)
        label.pack(padx=5,pady=5,fill=ctk.X,expand=True,anchor="n")

        spotify_import_labels.append(label)


is_downloading = False
def toggle_spotify_download():
    global is_downloading

    sus_url = spotify_url_entry.get()
    
    if sus_url.strip() == "":
        spotify_download_status.configure(text=f"Empty URL.",text_color="red")
        return 

    if not "spotify.com" in sus_url:
        spotify_download_status.configure(text=f"Invalid URL",text_color="red")
        return
    is_downloading = False

    if not is_downloading:
        is_downloading = True
        threading.Thread(target=import_spotify_playlist).start()
    else:
        is_downloading = False
        spotify_import_youtube_button.configure(state="disabled",text="Canceling...")

def import_spotify_playlist():
    global is_downloading

    spotify_import_youtube_button.configure(text="Cancel Download")
    playlist_contents = get_spotify_playlist_tracks(spotify_url_entry.get())
    if playlist_contents:

        reload_spotify_import_statuses(playlist_contents)
        for i in range(len(playlist_contents)):
            if is_downloading == True:
                current_song = playlist_contents[i]
                spotify_import_labels[i].configure(fg_color="#DEDEDE",text_color="#000000")

                spotify_download_progress.set((i+1)/len(playlist_contents))
                spotify_download_status.configure(text=f"({i+1} / {len(playlist_contents)}) Downloading - '{current_song['title']}'",text_color="white")
                root.update()
                try:
                    if not current_song["title"]+".mp3" in all_library_songs:
                        _, final_path = download_track_from_search(current_song["title"],current_song["artist"],music_path,ffmpeg_path) #heh.. i havent  heard  that name in   yeearrs son.  let me  tell  you a  bout a good ol   friend of mine,   gdir...
                        lw_add_song(os.path.basename(final_path), spotify_add_to_cdir_check.get()) 
                        
                        spotify_download_status.configure(text="Song Imported Successfully!",text_color="green")
                        spotify_import_labels[i].configure(fg_color="#A2FF97",text_color="#000000")
                    else:
                        spotify_download_status.configure(text="Song Imported Successfully!",text_color="green")
                        spotify_import_labels[i].configure(fg_color="#FCED77",text_color="#000000",text=f" {current_song["title"]} - Already Imported")
                    root.update()
                except Exception as e:
                    spotify_import_labels[i].configure(fg_color="#FF6557",text=f" {current_song["title"]} - Failed")
                    spotify_download_status.configure(text=f"({i+1} / {len(playlist_contents)}) Failed - '{current_song['title']}'",text_color="white")
                    root.update()
                    print(f"spotify import error:\n {e}")
                spotify_import_frame.lift()
            else:
                spotify_import_youtube_button.configure(state="normal",text="Import")
                is_downloading = False
                spotify_download_status.configure(text=f"Import Canceled.",text_color="yellow")
                return
        spotify_download_status.configure(text=f"Playlist Imported!",text_color="green")
    else:
        spotify_download_status.configure(text="ERROR: Could not reach playing. Please make sure that you have a VALID, PUBLIC, url. The url CANNOT reference a albumb or single track.",text_color="red")

    spotify_import_youtube_button.configure(state="normal",text="Import")
    reload_all_lib_songs()
    spotify_import_frame.lift()
    is_downloading = False

    with open(directorys_path, "w") as f:
        f.write(json.dumps(song_directorys))

spotify_import_youtube_button = ctk.CTkButton(spotify_import_frame,text="Import",width=80,height=26,border_width=1,fg_color="#2B2B2B",hover_color="#1a1a1a",command=toggle_spotify_download,font=("Inter",14,"bold"))
spotify_import_youtube_button.place(relx=0.05,rely=0.65,relwidth=0.55)


#SPOTIFY API
def get_spotify_playlist_tracks(playlist_url):
    try:
        playlist_id = playlist_url.split("/playlist/")[1].split("?")[0]
        embed_url = f"https://open.spotify.com/embed/playlist/{playlist_id}"

        resp = requests.get(embed_url, headers={"User-Agent": "Mozilla/5.0"},timeout=5)
        match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.+?)</script>', resp.text) #why's it red?    in vs? huh
        data = json.loads(match.group(1))

        entity = data["props"]["pageProps"]["state"]["data"]["entity"]
        tracks = []
        for item in entity["trackList"]:
            tracks.append({
                "title": item["title"],
                "artist": item["subtitle"],  # usually "Artist1, Artist2"
            })
        return tracks
    except Exception as e:
        return None

spotify_download_status = ctk.CTkLabel(spotify_import_frame,text="Download Status")
spotify_download_status.place(relx=0.05,rely=0.77)

spotify_download_progress = ctk.CTkProgressBar(spotify_import_frame,corner_radius=20,progress_color="#248DDE")#DIHHHHHH
spotify_download_progress.place(relx=0.05,rely=0.87,relwidth=0.88)
spotify_download_progress.set(0)

def apply_playoffset_tween(time=0):
    global playing_xoffset
    if time < 80:
        playing_xoffset = round(cubic_bounce(0,-80,time/80))
        time += 1
        root.after(5,lambda:apply_playoffset_tween(time))

def find_bookmarks_from_songname(name):
    for bookmark in bookmarks:
        if bookmark["song"] == name:
            return bookmark
    return None

def seek_to_bookmark(index):
    selected_bookmark = find_bookmark_index_from_name(CURRENT_TRACKDATA[2])
    timestamp = bookmarks[selected_bookmark]["timestamps"][index]
    timeline_slider.set(timestamp)
    
    hold_pausestate = pause_state.get()

    seek_pos(None)

    if not hold_pausestate:#if not paused
        manage_pause(False) # then play, seek_pos() pauses it by default, so we wanna preserve that state

timestamp_hover_frame = ctk.CTkFrame(root,border_width=15,fg_color="black",border_color="white")  #no clue why you cant see it but worth a shot i guess
timestamp_hover_name = ctk.CTkLabel(timestamp_hover_frame,text="",fg_color="transparent")
timestamp_hover_name.pack()

def timestamp_hover(event,index,location_y=350):
    timestamp_widget = bookmark_frames[index]
    location_x = timestamp_widget.winfo_x()

    timestamp_hover_name.configure(text=f"  {bookmarks[find_bookmark_index_from_name(CURRENT_TRACKDATA[2])]['names'][index]}  ") #sonion... what the fu
    
    timestamp_hover_frame.place(x=location_x,y=location_y) #yeah y pos kinda broke but it dosnt really matter
    timestamp_hover_frame.lift()

def hover_timestamp_leave(event):
    timestamp_hover_frame.place_forget()

def reload_bookmarks():
    #4. bookmarks (oohhhhh scarryyyyy)
    for bookmark in bookmark_frames:
        bookmark.destroy()
    bookmark_frames.clear()  #.clear() is a mutation, no need for global declaration


    bookmark_data = find_bookmarks_from_songname(CURRENT_TRACKDATA[2])
    if bookmark_data: #if any data exists for this song
        timestamps = bookmark_data["timestamps"]

        for i in range(len(timestamps)):
            indicator = ctk.CTkButton(timeline_slider,width=6,height=15,fg_color="white",corner_radius=5,text="",command=lambda index=i:seek_to_bookmark(index),bg_color="#2B2B2B")
            indicator.place(relx=timestamps[i]) # timestamp is recorded in the slider (0-1) on the manager, and so is relx (0-1), so this becomes really easy

            indicator.bind("<Enter>",lambda event,index=i:timestamp_hover(event,index))
            indicator.bind("<Leave>",hover_timestamp_leave)
            bookmark_frames.append(indicator) # so they can be removed later


def select_song(customindex=FOCUS_INDEX, songdir=None):
    global CURRENT_TRACKDATA
    global current_music_lenght
    global seek_offset

    # 1. datagrabbing
    if songdir == None:
        image, song_dir, name, uploader = all_songs[customindex]
    else:
        image, song_dir, name, uploader = safeload_song(songdir,usedir=True)

    if song_dir:   
        if os.path.exists(song_dir): #2. if video sill exists -video? wth are you talking about?
            #3. setmusic player stuff ----------------------------------------
            if not songdir == None: #if its a full dir
                ext, tail = os.path.split(name)
                name = tail

            CURRENT_TRACKDATA = (image,song_dir,name)
            mixer.music.load(song_dir)
            current_music_lenght = MP3(song_dir).info.length * 1000 # seconds -> ms
            seek_offset = 0
            timeline_slider.set(0)
            manage_pause(customstate=False) # starts playback from seek_offset (0) and sets play_start_time

            
            reload_bookmarks() # conveient lil guy, aint he?
            #title update-----------------------------------------------
            song_title_text.configure(text=os.path.basename(name).replace(".mp3",""))
            song_creator_text.configure(text=uploader)

            #discord-----------------------------------------------
            all_gdirnames = GLOBAL_MUSIC_DIR.replace('\\',"/").split("/")
            gdirlen = len(all_gdirnames)

            short_gdirname = f"{all_gdirnames[gdirlen-1]}"

            details = truncate_string(f"{short_gdirname} / {name.replace(".mp3","")} ({uploader})")

            threading.Thread(target=update_presence,args=(details,"vibing to:")).start()
            root.update_idletasks()
            #BG image-----------------------------------------------
            if image:
                width, height = image.size

                scale = max(root_w / width, root_h / height)

                new_width = int(width * scale)
                new_height = int(height * scale)

                image = image.resize((new_width//round(bg_blur_slider.get()*100), new_height//round(bg_blur_slider.get()*100)), Image.Resampling.LANCZOS)

                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                bgimage = ctk.CTkImage(image, size=(new_width, new_height))
                bglabel.configure(image=bgimage,text="")
            else:
                bgimage = ctk.CTkImage(Image.new("RGB",(root_w,root_h),"#000000"), size=(root_w, root_h))
                bglabel.configure(image=bgimage)

            #add to recents
            if name in recent_songs:
                recent_songs.remove(name)

            recent_songs.insert(0,name)
            if len(recent_songs) > 18: #add setting to settigs later maybe
                recent_songs.pop(18)
        else:
            bgimage = ctk.CTkImage(Image.new("RGB",(root_w,root_h),"#000000"), size=(root_w, root_h))
            bglabel.configure(image=bgimage,text="Huh...\nIt looks like the song you are trying to \nplay has a mis-matched filename with the library...\n\nPlease dont change filenames in the file exporer,\n and leave data handeling to the app. \n\nFor now, you can clean up unknown \nsongs in the settings menu.")

    apply_playoffset_tween() #animate the bounce :D

def clear_songframes():
    for i in range(len(song_frames)):
        if len(song_frames[i]) == 3:
            image_label = song_frames[i][1]

            if image_label.cget("image"):
                del image_label._image # found you. 
        song_frames[i][0].destroy() 
    song_frames.clear()


def reload_recents_directory_ui(): #VERY DIFFERENT- USED ONLY FOR RECENT
    clear_songframes()    #destroy UI
    #compile_music_cache() #songs are compiled differnetly for recents.
    create_recents_songframes()   #create new UI - but for the home menu lol
    load_image_thread()   #apply thumbnail images

def reload_current_directory_ui(): #very convient :D  normally global_music_dir is just changed globally externally so we can do whatever we want before hand and it adaps.. like... mahoraga..... yeh... im calling it that now
    clear_songframes()    #destroy UI
    compile_music_cache() #recompile songs list
    create_songframes()   #create new UI
    load_image_thread()   #apply thumbnail images

def bind_songframe_button_thing(selection_index):
    global FOCUS_INDEX
    global PLAYING_INDEX
    global GLOBAL_MUSIC_DIR
    global RENDER_INDEX
    
    if selection_index == "back":
        FOCUS_INDEX = selection_index
        PLAYING_INDEX = None
        FOCUS_INDEX = 0
        GLOBAL_MUSIC_DIR = os.path.dirname(GLOBAL_MUSIC_DIR)# back one
        
        reload_current_directory_ui()
    else:
        _, _, name, _ = all_songs[selection_index]
        print(f"request to play song {name}")
        if selection_index != PLAYING_INDEX:
            if valid_audio_name(name):
                FOCUS_INDEX = selection_index
                PLAYING_INDEX = selection_index

                select_song(selection_index)
            else:#if its a directory
                future_dir = os.path.join(GLOBAL_MUSIC_DIR,name)
                if not future_dir in song_directorys:
                    print("directory missing endpoint, creating one...")
                    song_directorys[future_dir] = []
                GLOBAL_MUSIC_DIR = future_dir
                FOCUS_INDEX = selection_index
                PLAYING_INDEX = None
                RENDER_INDEX = -100
                RENDER_INDEX = 5
                FOCUS_INDEX = 0
                
                reload_current_directory_ui()


def bind_select_cursor(event=None):
    root.configure(cursor="hand2")

song_options_frame = ctk.CTkFrame(root,fg_color="#000000",corner_radius=0,width=100,height=80)
song_options_frame.propagate(False)

def remove_song_from_cdir():
    song_options_frame.place_forget()
    try:
        target_song = list(all_songs[songframe_option_index])
        if not valid_audio_name(target_song[2]): #remove full directory
            try:
                song_directorys.pop(os.path.join(GLOBAL_MUSIC_DIR,target_song[2])) 
            except:
                pass
            try:
                song_directorys[GLOBAL_MUSIC_DIR].pop(song_directorys[GLOBAL_MUSIC_DIR].index(target_song[2]))
            except:
                pass
        else:
            song_index = song_directorys[GLOBAL_MUSIC_DIR].index(target_song[2]) #2: name
            song_directorys[GLOBAL_MUSIC_DIR].pop(song_index)

            del target_song[0] #0: image, fully removed from memory
            all_songs.pop(songframe_option_index)
    except Exception as e:
        print(f"failed to remove song: {e}") #just in case man, you can never be too careful...

    reload_current_directory_ui()

    songframe_option_button.place_forget()
    rebind_all_songframes()

def rename_song_from_entry(): #and now, i present to you.. a function, that... cant.. really.. fail....  (i was feeling nervious so i safegaruded the HELL outta ts)
    global song_directorys, all_library_songs, bookmarks
    original_name = all_songs[songframe_option_index][2]
    newname = new_name_entry.get() 
    song_options_frame.place_forget()

    rename_status.configure(text="")

    should_restart_song = False
    if CURRENT_TRACKDATA: #if a song is loaded
        if CURRENT_TRACKDATA[2] == original_name: #is OUR song is loaded
            manage_pause(customstate=True)
            mixer.music.unload()
            should_restart_song = True

    if valid_audio_name(original_name):
        if os.path.exists(os.path.join(music_path,original_name)): #check for OLD file
            fname, ext = os.path.splitext(newname) # i know that the entry removes .mp3 but like someone might like i dunno od it anyways i dunno man
            if ext != ".mp3":
                newname += ".mp3"

            if fname.strip() == "":
                rename_status.configure(text="Cannot have empty name!")
                return

            if "/" in fname:
                rename_status.configure(text="Cannot contain directory determining characters")
                return

            if os.path.exists(os.path.join(music_path,newname)): #check if NEW name is already taken
                rename_status.configure(text="Name already exists.")
                return

            try:
                os.rename(os.path.join(music_path,original_name),os.path.join(music_path,newname))
            except Exception as e:
                rename_status.configure(text=f"OS Error: {e}")
                print(f"rename cancelled due to os error. (invalid, already taken, ect...)\n{e}")
                return

            #i actually made the following snippet durin school lunch...
            all_directorys = list(song_directorys.keys())

            for cdir in all_directorys: #change all references in song_directorys
                files = song_directorys[cdir]
                if original_name in files:
                    target_file_index = files.index(original_name)
                    song_directorys[cdir][target_file_index] = newname

            for bookmark in bookmarks:
                if bookmark["song"] == original_name:
                    bookmark["song"] = newname #huh, that was... really easy, actually..

            if original_name in recent_songs:
                recent_index = recent_songs.index(original_name)
                recent_songs[recent_index] = newname

            all_library_songs[all_library_songs.index(original_name)] = newname

            load_song_library()

        else:
            print("rename failed due to nonexistsant file. song direcotry will be reserved though.")

        if should_restart_song:
            restart_current_song() #i mean i could save where we were but uh... nah
    else:
        if newname.strip() == "":
            rename_status.configure(text="Cannot have empty name!")
            return

        if "/" in newname:
            rename_status.configure(text="Cannot contain directory determining characters")
            return

        if "." in newname:
            rename_status.configure(text="Cannot contain file extention determining characters.")
            return

        if dir_exists(newname):
            rename_status.configure(text="Directory already exists!")
            return
        
        
        song_directorys[GLOBAL_MUSIC_DIR][song_directorys[GLOBAL_MUSIC_DIR].index(original_name)] = newname #replace direcotry "link"
        song_directorys[os.path.join(GLOBAL_MUSIC_DIR,newname)] = song_directorys.pop(os.path.join(GLOBAL_MUSIC_DIR,original_name)) 

    rebind_all_songframes()
    reload_current_directory_ui() #reload the UI with the new data.
    close_rename_menu()

def close_rename_menu():
    song_options_frame.place_forget()
    animate_close_menu(rename_frame,0.2,1,True)
    close.place(relx=0.95,rely=0.01)

rename_frame = ctk.CTkFrame(root,width=400,height=200,border_width=1,border_color="#666666")
rename_frame.place(relx=0.2,rely=-1)

rename_title = ctk.CTkLabel(rename_frame,text="Rename Song",font=("",18,"bold")) #why dose this spelling look so wrong?
rename_title.place(x=5,y=5)

old_name_rename = ctk.CTkLabel(rename_frame,text="Old Name:",font=("",15,"normal")) 
old_name_rename.place(x=5,y=31)

old_name_entry = ctk.CTkEntry(rename_frame,font=("",10,"normal"),width=380,height=26) 
old_name_entry.place(x=5,y=54)

new_name_rename = ctk.CTkLabel(rename_frame,text="New Name:",font=("",15,"normal")) 
new_name_rename.place(x=5,y=85)

new_name_entry = ctk.CTkEntry(rename_frame,font=("",10,"normal"),width=380,height=26)
new_name_entry.place(x=5,y=110)

rename_status = ctk.CTkLabel(rename_frame,text="",font=("aerial",10,"normal"),height=20,text_color="red")
rename_status.place(x=5,y=140)

cancel_rename_btn = ctk.CTkButton(rename_frame,text="Cancel",border_width=1,border_color="#666666",height=20,fg_color="#333333",hover_color="#320000",command=close_rename_menu)# ive really been likeing this style but i gotta add themes soon so hopefully the idea sticks...
apply_rename_btn = ctk.CTkButton(rename_frame,text="Rename",border_width=1,border_color="#666666",height=20,fg_color="#333333",hover_color="#111111",command=rename_song_from_entry)

cancel_rename_btn.place(rely=0.83,relx=0.02)
apply_rename_btn.place(rely=0.83,relx=0.62)


#delete menu: (ok i kind of took the replace menu CUZ IT DOSNT LOOK THAT BAD--)
delete_frame = ctk.CTkFrame(root,width=400,height=280,border_width=1,border_color="#666666")
delete_frame.place(relx=0.2,rely=-1)

delete_title = ctk.CTkLabel(delete_frame,text="Delete Song",font=("",18,"bold")) #why dose this spelling look so wrong?
delete_title.place(x=5,y=5)

delete_song_title = ctk.CTkLabel(delete_frame,text="song name askdjhksdlf ansdlfkj",font=("",15,"bold"),fg_color="#181818",corner_radius=5) 
delete_song_title.place(relx=0.05,relwidth=0.90,y=45)

delete_song_info = ctk.CTkLabel(delete_frame,text="By deleting a song, you are fully \nremoving it from the library, as well\n as all instances of it in your playlists.\n\n This action is not recoverable unless \nyou download this song again.\n\n\n Are you sure you want to continue?",font=("",13,"normal")) 
delete_song_info.place(relx=0.05,relwidth=0.90,y=83)

cancel_delete_btn = ctk.CTkButton(delete_frame,text="Cancel",border_width=1,border_color="#666666",height=20,fg_color="#333333",hover_color="#111111",command=close_delete_menu)
delete_song_btn = ctk.CTkButton(delete_frame,text="Delete",border_width=1,border_color="#666666",height=20,fg_color="#721212",hover_color="#DE2929") #command is assigned when we know what song we are targeting

cancel_delete_btn.place(rely=0.88,relx=0.02)
delete_song_btn.place(rely=0.88,relx=0.62)

def open_rename_menu():
    old_name_entry.configure(state="normal")
    old_name_entry.delete(0,ctk.END)
    old_name_entry.insert(0,all_songs[songframe_option_index][2].replace(".mp3",""))
    old_name_entry.configure(state="disabled")

    new_name_entry.delete(0,ctk.END)
    new_name_entry.insert(0,all_songs[songframe_option_index][2].replace(".mp3",""))

    bg_frame.place(relwidth=1,relheight=1)
    close.place_forget() #so uh we kinda gotta hide just for this menu cuz its for something else but like why did i call it this? im not gonna change it but this seriously didnt like interfere with anything?
    bg_frame.lift()
    rename_frame.lift()
    animate_open_menu(rename_frame,-0.5,0.2,True)

song_options_rename = ctk.CTkButton(song_options_frame,text="✏️ Rename",width=90,fg_color="#000000",hover_color="#151515",command=open_rename_menu)
song_options_rename.pack(padx=5,pady=(10,5))
song_options_remove = ctk.CTkButton(song_options_frame,text="❌ Remove",width=90,fg_color="#000000",hover_color="#151515",command=remove_song_from_cdir)
song_options_remove.pack(padx=5,pady=(0,10))

def check_leave(event):
    widget = event.widget
    mx, my = event.x_root, event.y_root

    x1 = widget.winfo_rootx()
    y1 = widget.winfo_rooty()
    x2 = x1 + widget.winfo_width()
    y2 = y1 + widget.winfo_height()

    #box bound- hmm... i suppose this actually works pretty well...
    if not (x1 <= mx <= x2 and y1 <= my <= y2):
        song_options_frame.place_forget()

song_options_frame.bind("<Leave>",check_leave)

def song_options_menu_summon():
    target_x = songframe_option_button.winfo_x()-100
    target_y = songframe_option_button.winfo_y()-35

    song_options_frame.place(x=target_x,y=target_y)
    song_options_frame.lift()

songframe_option_index = None #the assigned index
songframe_option_button = ctk.CTkButton(root,text="",image=more_options_image,fg_color="#000000",width=30,hover_color="#0c0c0c",command=song_options_menu_summon)


def enter_songframe(event=None, index=None): #assign the option menu to a index, will be updated with update_songframes
    global songframe_option_index
    songframe_option_index = index

    songframe_option_button.lift()
    bottom_options_bar.lift()
    bottom_timeline_bar.lift()

    song_options_frame.place_forget()

    root.configure(cursor="hand2")
    
def leave_songframe(event=None):
    global songframe_option_index
    root.configure(cursor="arrow")
    songframe_option_index = None
    songframe_option_button.place_forget()
   

def bind_leave_cursor(event=None):
    root.configure(cursor="arrow")

def hover_enter_recent_songframe(event):
    event.configure(fg_color="#464646")
    root.configure(cursor="hand2")

def hover_leave_recent_songframe(event):
    event.configure(fg_color="#2B2B2B")
    root.configure(cursor="arrow")

def create_recents_songframes(spaceing=10):  
    for i in range(len(all_songs)): #use the filtered one
        _,_,songname, _ = all_songs[i]

        songlabel = ctk.CTkLabel(recent_songs_frame, text=(songname.replace(".mp3","")+("" if valid_audio_name(songname) else "   ")), font=("Arial", 20, "bold"), image=None if valid_audio_name(songname) else folder_image,corner_radius=5,fg_color="#2B2B2B",width=625,anchor="w")
        songlabel.pack(padx=10,pady=5,anchor="w")
        
        recent_frames.append(songlabel) 
        

        #UI BUTTON ANIMATIONS
        songlabel.bind("<Button-1>", lambda event, idx=i: bind_songframe_button_thing(idx))

        songlabel.bind("<Enter>", lambda event, widget=songlabel: hover_enter_recent_songframe(widget))
        songlabel.bind("<Leave>",  lambda event, widget=songlabel: hover_leave_recent_songframe(widget))

def create_songframes(spaceing=10):  
    for i in range(len(all_songs)): #use the filtered one
        _,_,songname, _ = all_songs[i]

        song_frame, image_label, title_label = songframe_template(songname)
        song_frames.append((song_frame, image_label, title_label))
        
        image_label.bind("<Button-1>", lambda event, idx=i: bind_songframe_button_thing(idx))
        title_label.bind("<Button-1>", lambda event, idx=i: bind_songframe_button_thing(idx))
        image_label.bind("<Enter>", lambda event, idx=i:enter_songframe(event,idx))
        title_label.bind("<Enter>", lambda event, idx=i:enter_songframe(event,idx))
        image_label.bind("<Leave>", bind_leave_cursor)
        title_label.bind("<Leave>",bind_leave_cursor)

    if GLOBAL_MUSIC_DIR != BASE_DIR: # if its changed   oommgg this is SOOO mUCH BETTER then the last one
        all_gdirnames = GLOBAL_MUSIC_DIR.replace('\\',"/").split("/")
        gdirlen = len(all_gdirnames)

        short_gdirname = f".../{all_gdirnames[gdirlen-2]} / {all_gdirnames[gdirlen-1]}"

        back_frame, back_image_label, back_title_label = songframe_template("<< Back")
        dir_frame, image_label, title_label = songframe_template(short_gdirname+"     ")

        song_frames.append((back_frame, image_label, back_title_label))
        song_frames.append((dir_frame, image_label, title_label))

        back_image_label.bind("<Button-1>", lambda event, idx="back": bind_songframe_button_thing(idx))
        back_title_label.bind("<Button-1>", lambda event, idx="back": bind_songframe_button_thing(idx))
        back_image_label.bind("<Enter>", bind_select_cursor)
        back_title_label.bind("<Enter>", bind_select_cursor)
        back_image_label.bind("<Leave>", bind_leave_cursor)
        back_title_label.bind("<Leave>", bind_leave_cursor)

    bg_frame.lift()

    bottom_options_bar.lift()
    bottom_timeline_bar.lift()

    song_title_text.lift()
    song_creator_text.lift()
    library_menu_button.lift()
    directory_view_frame.lift()

    library_menu_frame.lift()
    external_import_menu.lift()

    

#THE NEW DIRECTORY THINGY FORMAT:
#ok so i think how ima do this is we have a bunch of items, all with the name of the directory. so:


'''example = {
    "music/stuff":["song.mp3","othersong.mp3"],
    "music/stuff/more stuff":["song.mp3","othersong.mp3"], #un-string this if u want teh colors
    "music/things":["song.mp3","othersong.mp3"]
}'''

#the optimization is mid but this isnt that bad, since each of those have a list of all the song names, 
#i spefically chose this over assigning each individual song its own direcoty cuz that would suck.

#'oh but if we wanna reserve the old format how do we know where its be??'

#first of all, who is "we"? secondly-   i uh.. i havent thought that far yet.. actually....       shi,  
# i mean we could start the library thing on startup but i dont wanna, since its SLOW.

#OR WE gets a SECOND list the the UI reads from then its first needed but is locally referred to when songs are needed! 

#AH-HA! I GOT IT! ahh... yup.  mm.. alright, well i gotta go that now... hughhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh

#edit: somehow- os.walk fits this format like... perfectly.... what.
#edit #2 - we cant actually do that second list thing you BAFOON. haveing an entire list containing EACH DIRECTORY??? DO YOU KNOW HOW EXPENSIVE THAT WOULD BE??? NO??   VERY.    VERY EXPENSIVE.
def get_songs_in_directory(directory:str):
    pass


def get_average_color(img: Image.Image):
    small = img.resize((1, 1), Image.Resampling.LANCZOS)
    return small.getpixel((0, 0))

def update_songframes(spaceing=15):
    for i in range(len(song_frames)):
        song_frame, image_label, _ = song_frames[i]
        if i <= len(all_songs)-1: #if in range, ignore back button and dir label
            if image_label.ctkimage is None and all_songs[i][0] is not None:
                image_label.ctkimage = ctk.CTkImage(all_songs[i][0],size=all_songs[i][0].size)
                image_label.configure(image=image_label.ctkimage)

        offset = (i - RENDER_INDEX)
        norm = offset * 0.25  # normalized angle
        curve = math.cos(norm)
        
        relative_y = offset * spaceing / 100
        relative_x = (0.6 + curve * 0.12)

        if relative_y > -0.2 and relative_y < 1.2:
            if PLAYING_INDEX == i:
                song_frame.place(relx=relative_x, relwidth=0.4, rely=relative_y,x=playing_xoffset)
            else:
                song_frame.place(relx=relative_x, relwidth=0.4, rely=relative_y,x=0)
        else:
            song_frame.place_forget()

        if songframe_option_index != None and i == songframe_option_index and PLAYING_INDEX == songframe_option_index:
            songframe_option_button.place(relx=relative_x, rely=relative_y,x=(-0)+playing_xoffset)
        if songframe_option_index != None and i == songframe_option_index and PLAYING_INDEX != songframe_option_index:
            songframe_option_button.place(relx=relative_x, rely=relative_y,x=(0))

        if songframe_option_index == None:
            songframe_option_button.place_forget()
     

def apply_theme(fg_color, border_color, border_width, hover_accent,slider_button,slider_track,slider_bg):
    frames = [bottom_timeline_bar,bottom_options_bar,volume_frame,musicmenu,bookmark_menu,yt_import_frame,spotify_import_frame,]
    for frame in frames:
        frame.configure(fg_color=fg_color,bg_color=border_color,border_color=border_color,border_width=border_width+1)

    
    buttons = [seek_next_song_butt,settings_button,pause_butt,add_bookmark_button,import_youtube_button,restart_song_button,seek_next_song_butt,seek_previous_song_butt,bookmark_manager_button,random_song_butt,add_music_butt]
    for button in buttons:
        button.configure(fg_color=fg_color,hover_color=hover_accent)    

    volume_slider.configure(button_color=slider_button,progress_color=slider_track,fg_color=slider_bg)
    timeline_slider.configure(button_color=slider_button,progress_color=slider_track,fg_color=slider_bg)

#apply_theme("#2B2B2B","#474747",1,"#1A1A1A","#1F6AA5","#AAB0B5","#4A4D50") #default
#apply_theme("#FFFFFF","#FFFFFF",1,"#FFFFFF","#FFFFFF","#FFFFFF","#FFFFFF")

def rgb_to_hex(rgb):
    r, g, b, _ = rgb
    return f"#{r:02x}{g:02x}{b:02x}"

def scroll_wheel(event):
    global FOCUS_INDEX

    delta = event.delta

    if delta > 0:
        FOCUS_INDEX -= 1
    else:
        FOCUS_INDEX += 1

    # clamp to valid range
    FOCUS_INDEX = max(0, min(len(all_songs)-1, FOCUS_INDEX))

    # update button color           - what was this for again?   i forgot.. 
    #huh- like 5 versions later and i remembered.   wait- no i don't.. why am i writing this

def animate_widget_x(widget, start, end, time=0,duration=50):
    if time <= duration:
        widget.place(x=cubic_out(time/duration,start,end))
        
        time += 1
        root.after(16,lambda:animate_widget_x(widget, start, end, time, duration))

def focus_animation(focused):
    if focused:
        animate_widget_x(bottom_options_bar,-300,0)
        animate_widget_x(bottom_timeline_bar,-390,0)
        animate_widget_x(volume_frame,-40,0)

        if current_view_mode == "playlists":
            animate_widget_x(song_title_text,-730,30)
            animate_widget_x(song_creator_text,-730,30)
            animate_widget_x(library_menu_button,-30,0)
        animate_widget_x(directory_view_frame,200,30)
    else:
        animate_widget_x(bottom_options_bar,0,-300)
        animate_widget_x(bottom_timeline_bar,0,-390)
        animate_widget_x(volume_frame,0,-40)

        if current_view_mode == "playlists":
            animate_widget_x(song_title_text,30,-730)
            animate_widget_x(song_creator_text,30,-730)
            animate_widget_x(library_menu_button,0,-30)
        animate_widget_x(directory_view_frame,30,200)

def calulate_seconds_strtime(seconds):
    seconds = int(seconds)
    m = seconds // 60
    s = seconds % 60
    return f"{m}:{s:02d}"

focus_step = "focused"
def interpolate_render_index(): # change the focus index as much as you want, BECAUSE I USED TO USE SCRATCH!!! AH HA HA HA HA
    global FOCUS_INDEX
    global RENDER_INDEX
    global PLAYING_INDEX
    global focus_step

    if not pause_state.get() and current_music_lenght != 0: # if true /= unpaused
        current_s = get_current_track_pos()

        if current_music_lenght > 0 and (current_music_lenght//1000) > current_s:
            slider_value = current_s / (current_music_lenght / 1000)
            timelime_label.configure(text=f"{calulate_seconds_strtime(current_s)} / {calulate_seconds_strtime(current_music_lenght//1000)}")
            timeline_slider.set(slider_value)


        if (current_music_lenght//1000)+1 < current_s and PLAYING_INDEX != None: # when audio is done
            #LOOPING
            if after_song_mode.get() == "Loop":
                currentsongdir = CURRENT_TRACKDATA[1]
                select_song(songdir=currentsongdir)

            #WAITING
            if after_song_mode.get() == "Wait":
                PLAYING_INDEX = None
                currentsongdir = CURRENT_TRACKDATA[1]

                mixer.music.play(start=1)
                manage_pause(True)
                threading.Thread(target=update_presence,args=("  ","choosing a song")).start()

            #SHUFFLE
            if after_song_mode.get() == "Shuffle":
                random_song() # after all of that pain, this just happens

            if after_song_mode.get() == "Next":
                skip_next_song()
    
    if root.state() == "normal" and root.focus_get() != None:
        distance = FOCUS_INDEX - RENDER_INDEX - 4
        RENDER_INDEX += (distance / max(1,scroll_speed_slider.get()*100))
        root.after(0,update_songframes)
        if focus_step == "unfocused":
            focus_step = "focused"
            focus_animation(focused=True)
    else:
        if focus_step == "focused":
            focus_step = "trans"

        if focus_step == "trans":
            focus_step = "unfocused"
            focus_animation(focused=False)

    root.after(16,interpolate_render_index)

def hide_console():
    ctypes.windll.kernel32.FreeConsole()


def keyrelease(event):
    key = event.keysym
    #print(key) #uncomment if you want the keycodes

    if key == "BackSpace" and GLOBAL_MUSIC_DIR != BASE_DIR and not in_menu:
        bind_songframe_button_thing("back")

    if not in_menu:
        if key == "Up":
            skip_backwards_song()
        if key == "Down":
            skip_next_song()  
        if key == "space":
            manage_pause()
        if key == "Tab" and current_view_mode == "playlists":
            toggle_libary_menu()
        if key == "h":
            focus_animation(focused=False) #im not telling anyone about this until im not lazy enought to toggle or add more support for it

    if key == "7":
        show_console()

def safe_save_appdata(path, value):
    try:
        with open(path, "w") as f:
            f.write(value)
        print(f"✅successfully saved {path}")
    except Exception as e:
        print(f"❌ failed to save file: {path} due to the following exception: \n{e}")

#------------------------------
# UI INITS------------------------------
profile_import_menu(yt_import_frame) #make the import menu start on the youtube frame

root.iconbitmap(placeify_ico)
root.bind("<MouseWheel>",scroll_wheel)
root.bind("<KeyRelease>",keyrelease)

def kickstart_song_systems():
    root.after(0,create_songframes)
    root.after(1,interpolate_render_index)
    root.after(0,load_image_thread)

init_passes()

if is_new_user:
    startingtext = ctk.CTkLabel(root,text="Welcome to Placeify! To get started, click  on the '+' button!") #eh ill do this later
    #startingtext.place(relx=0.1,rely=0.5)

    changelogs.show_startscreen(root,ctk.CTkImage(Image.open(resource_path("assets/placeify.png")),size=(60,60)),kickstart_song_systems,placeify_ico,get_exe_path())
else:
    kickstart_song_systems()

reload_all_lib_songs()
compile_music_cache()

root.mainloop()

print(" SHUTDOWN -------------------------------------------------")

try:
    rpc_loop.call_soon_threadsafe(rpc_loop.stop)
except:
    pass

mixer.music.stop()
mixer.music.unload()

mutinstance.running = False

save_settings()
safe_save_appdata(bookmarks_path, json.dumps(bookmarks))
safe_save_appdata(directorys_path, json.dumps(song_directorys))
safe_save_appdata(recents_path, json.dumps(recent_songs))
