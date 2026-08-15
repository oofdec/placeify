import math
import time
import customtkinter as ctk
from mutagen.id3 import ID3
from mutagen.mp3 import MP3
from pygame import mixer
from PIL import Image
import io
import os, sys
import threading
from yt_dlp import YoutubeDL
from pypresence import Presence
import pywinstyles
import random
import asyncio
import json
import ctypes



default_settings = {"scroll_speed":0.08,
                    "blur_amount":0.25,
                    "use_disc":True}

def safe_mkdir(dirname):
    if not os.path.exists(dirname):
        os.mkdir(dirname)
        print(f"✅path {dirname} created")
    else:
        print(f"ℹ️path {dirname} already exists")

def find_best_music_dir(): # this is so stable trust bro trust
    appdata_path = os.getenv('APPDATA')

    placeify_path = os.path.join(appdata_path,"placeify")
    music_path = os.path.join(appdata_path,"placeify","music")
    setting_path = os.path.join(appdata_path,"placeify","settings.json")
    
    # step 1.         create all directorys
    safe_mkdir(placeify_path)
    safe_mkdir(music_path)

    if not os.path.exists(setting_path):
        with open(setting_path,"w") as f:
            f.write(json.dumps(default_settings))
        print("✅settings.json created")
    else:
        print("ℹ️settings.json already exists")
    
    return music_path



def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def get_ffmpeg_path():
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, "ffmpeg", "ffmpeg.exe")
    else:
        return os.path.join("ffmpeg", "ffmpeg.exe")


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
    if safe_settings_grab("use_disc"):
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


#-----------------------------------------------------------------------------------------------------------
#-----------music file stuff--------------------------------------------------------------------------------
def valid_audio_name(name):
    if ".mp3" in name or ".ogg" in name or ".wav" in name:
        return True
    else:
        return False


def safeload_song(name, usedir=False):
    image_data = None
    music_dir = GLOBAL_MUSIC_DIR+"/"+name

    if usedir:
        songpath = name
    else:
        songpath = music_dir

    uploader = ""
    try:
        audio = ID3(songpath)
        for tag in audio.values():
            if tag.FrameID == "APIC":
                image_data = tag.data
                break
    except Exception:
        pass

    try:
        uploader = audio.get("TPE1").text[0]
    except Exception:
        pass

    if image_data != None:
        image = Image.open(io.BytesIO(image_data))
    else:
        image = Image.new("RGBA",size=(1,1))

    return image, songpath, name, uploader


def critical_error_report(title,msg):
    print("\n--err report------------------------------------------------------------")
    print(f"""❌CRITICAL ERROR: {title} 
        What happened? :
            {msg}

            Please update your installation of placeify, and if this keeps happening, pleasee let me know under the comments of the github page.""")
    print("--------------------------------------------------------------\n")


def safe_settings_grab(name):
    if name in saved_settings:
        print(f"✅recall setting name {name}")
        return saved_settings[name]
    else:
        if name in default_settings:
            print(f"⚠️outdated save for '{name}', returning current default '{default_settings[name]}'")
            return default_settings[name]
        else:
            critical_error_report(
                title=f"no save was found for the name '{name}' under the dircetory or defaults.",

                msg=f"""there was no found attribute for a setting called '{name}' anywhere. 

                    This could happen from a outdated version that dose not support a default for this setting yet, or
                    a setting that name has been changed. This could also be an issue on our part. """
                    )


all_songs = []
def compile_music_cache():
    music_dir = os.listdir(GLOBAL_MUSIC_DIR)

    all_songs.clear()

    for songname in music_dir: # filter mp3
        _, ext = os.path.splitext(songname)
        if valid_audio_name(ext):
            all_songs.append(safeload_song(songname))
        if ext == "":
            all_songs.append((Image.new("RGBA",size=(1,1)),None,songname,""))

# BASE INITS---MUSIC DIRS------------------
GLOBAL_MUSIC_DIR = find_best_music_dir()
BASE_DIR = GLOBAL_MUSIC_DIR
compile_music_cache()

mixer.init()

#SETTINGS RECALL------------------------------
appdata_path = os.getenv('APPDATA')
placeify_path = os.path.join(appdata_path,"placeify")
settings_path = os.path.join(placeify_path,"settings.json")
with open(settings_path,"r") as f:
    try:
        saved_settings = json.loads(f.read())
    except:
        print("⚠️ settings courrupted - could not read setting json. restoring defaults")
        saved_settings = default_settings #fallback if courrupted settings

        with open(settings_path, "w") as f:
            f.write(json.dumps(saved_settings))
        print("   └ ℹ️default settings restored.")
print("GLOBAL DIR: "+GLOBAL_MUSIC_DIR)

#DISCORD------------------
CLIENT_ID = "1532524855130587216"
rpc = Presence(CLIENT_ID)
failed_presense = False
threading.Thread(target=connect_presence, daemon=True).start()




def cubic_bounce(start, end, t):
    # clamp t to [0, 1]
    if t < 0: t = 0
    if t > 1: t = 1

    # cubic ease-out base
    base = 1 - (1 - t)**3

    # bounce amount (you can tweak 0.25)
    bounce = math.sin(t * math.pi) * (1 - t) * 0.25

    # final value
    return start + (end - start) * (base + bounce)



ffmpeg_path = get_ffmpeg_path()
def download_youtube(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'ffmpeg_location': ffmpeg_path,   # FINALLYYYYYYY 
        'outtmpl': f'{GLOBAL_MUSIC_DIR+"/"}%(title)s.%(ext)s',   # auto name file as the video title
        'writethumbnail': True,
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            },
            {
                'key': 'FFmpegMetadata',   # <-- mm yes ffmpeg
            },
            {
                'key': 'EmbedThumbnail',   # embeds thumbnail into mp3 somehow
            }
        ]
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)

    #is all of this stored in the mp3?    dunno, probs wont accsess it anyway
    print("Title:", info.get("title"))
    print("Uploader:", info.get("uploader"))
    print("Tags:", info.get("tags"))
    print("Description:", info.get("description"))
    print("Channel:", info.get("channel"))
    print("Upload date:", info.get("upload_date"))


#-----------------------------------------------------------------------------------------------------------
#-----------UI Stuff--------------------------------------------------------------------------------
root = ctk.CTk("#050505")
root.geometry("700x400")
root.title("placeify")
root.resizable(width=False,height=False)

pause_state = ctk.BooleanVar(value=False) # unpaused
FOCUS_INDEX = 0 # internal index
RENDER_INDEX = 0 # UI index- for offset
PLAYING_INDEX = None # for ui state holding
CURRENT_TRACKDATA = ()
song_frames = [] # a list containing all of the ui elemets for showing the songs

current_music_lenght = 0
playing_xoffset = 0 #an offset applyed to the current played song
global_x_offset = 0 # applys to all widgets for switching diretorys

seek_offset = 0      # position (seconds) within the track where playback last started/resumed
play_start_time = 0  # time.time() when playback last started/resumed

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
            apply_playoffset_tween()


def skip_backwards_song():
    global PLAYING_INDEX
    global FOCUS_INDEX

    if PLAYING_INDEX != None:
        sus_index = (PLAYING_INDEX-1)%(len(all_songs))

        PLAYING_INDEX = (PLAYING_INDEX-1)%(len(all_songs))
        FOCUS_INDEX = PLAYING_INDEX

        if valid_audio_name(all_songs[sus_index][2]):
            select_song(PLAYING_INDEX)
            apply_playoffset_tween()



def find_random_valid_song_in_dir():
    song_exists_number = 0 
    for i in range(len(all_songs)):
        if "mp3" in all_songs[i][2]:
            song_exists_number += 1

    if song_exists_number > 1:
        random_song = random.randint(0,len(all_songs)-1)

        found_song = False
        current_song = "" if PLAYING_INDEX == None else all_songs[PLAYING_INDEX][2]
        while not found_song:
            if valid_audio_name(all_songs[random_song][2]) and current_song != all_songs[random_song][2]:
                found_song = True
            else:
                random_song = random.randint(0,len(all_songs)-1)
                           
        return random_song
    return None


def restart_current_song():
    if CURRENT_TRACKDATA != ():
        select_song(songdir=CURRENT_TRACKDATA[1])


def random_song():
    global PLAYING_INDEX
    global FOCUS_INDEX

    random_song = find_random_valid_song_in_dir()

    if random_song != None:
        print(random_song)
        PLAYING_INDEX = random_song
        FOCUS_INDEX = random_song

        select_song(random_song)
        apply_playoffset_tween()



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
def show_settings_menu():
    settmenu.place(relwidth=1,relheight=1)
    bg_frame.place(relwidth=1,relheight=1)
    close_settings_menu_butt.place(relx=0.935,rely=0.01)

    bg_frame.lift()
    settmenu.lift()
    close_settings_menu_butt.lift()

def close_focus_menus():
    bg_frame.place_forget()

    musicmenu.place_forget()
    dirmenu.place_forget()

    settmenu.place_forget()
    close_settings_menu_butt.place_forget()

def save_settings():
    settings_save = {
        "scroll_speed":scroll_speed_slider.get(),
        "blur_amount": bg_blur_slider.get(),
        "use_disc":use_disc_check.get()
        }

    try:
        with open(settings_path, "w") as f:
            f.write(json.dumps(settings_save))
        print("✅settings saved successfully!")
    except Exception as e:
        print("❌uh oh, couldnt save settings bc "+str(e))

def close_settings_menu():
    save_settings()
    close_focus_menus()

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

song_title_text = ctk.CTkLabel(root,font=("ariel",35,"bold"),text="",corner_radius=5)
song_title_text.place(relx=0.01,rely=0.01)

song_creator_text = ctk.CTkLabel(root,font=("ariel",19,"bold"),text="",corner_radius=5)
song_creator_text.place(relx=0.01,rely=0.11)

###---------------------------------------------------------------------------------
###BOTTOM OPTIONS BAR:  ------------------------------------------------------------------------

seek_previous_song_image = ctk.CTkImage(Image.open(resource_path("assets/previous_focus.png")), size=(14,14))
seek_previous_song_butt = ctk.CTkButton(bottom_options_bar,text="",image=seek_previous_song_image,fg_color="#2B2B2B",hover_color="#1a1a1a",width=5,command=skip_backwards_song)
seek_previous_song_butt.place(relx=0.17,rely=0.05)

seek_next_song_image = ctk.CTkImage(Image.open(resource_path("assets/next_focus.png")), size=(14,14))
seek_next_song_butt = ctk.CTkButton(bottom_options_bar,text="",image=seek_next_song_image,fg_color="#2B2B2B",hover_color="#1a1a1a",width=5,command=skip_next_song)
seek_next_song_butt.place(relx=0.26,rely=0.05)

random_song_butt_image = ctk.CTkImage(Image.open(resource_path("assets/shuffle v2.png")), size=(14,14))
random_song_butt = ctk.CTkButton(bottom_options_bar,text="",fg_color="#2B2B2B",hover_color="#1a1a1a",width=5,command=random_song,image=random_song_butt_image)
random_song_butt.place(relx=0.35,rely=0.05)

restart_song_image = ctk.CTkImage(Image.open(resource_path("assets/restart.png")), size=(14,14))
restart_song_button = ctk.CTkButton(bottom_options_bar,fg_color="#2B2B2B",text="",hover_color="#1a1a1a",image=restart_song_image,width=5,command=restart_current_song)
restart_song_button.place(relx=0.45,rely=0.05)

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

###---------------------------------------------------------------------------------
###SETTINGS MENU---------------------------------------------------------------------------------
def update_scrollspeed_text(event=None):
    scroll_speed_title.configure(text=f"Scroll Interpolation: {round(scroll_speed_slider.get()*100)}")
def update_bluramount_text(event=None):
    bg_blur_title.configure(text=f"BG Blur Amount: {round(bg_blur_slider.get()*100)}")

settmenu = ctk.CTkScrollableFrame(root,border_width=2,bg_color="#474747")

setting_title = ctk.CTkLabel(settmenu,text="Settings",font=("aeril",28,"bold"))
setting_title.pack(anchor="w")

setting_title = ctk.CTkLabel(settmenu,text="Visibility and UI",font=("aeril",28,"normal"))
setting_title.pack(anchor="w",pady=(25,9))

scroll_speed_title = ctk.CTkLabel(settmenu,text=f"Scroll Interpolation: {8}",font=("aeril",19,"normal"))
scroll_speed_title.pack(anchor="w")

scroll_speed_slider = ctk.CTkSlider(settmenu,width=600,command=update_scrollspeed_text,from_=0, to=0.20)
scroll_speed_slider.pack(anchor="w")
scroll_speed_slider.set(safe_settings_grab("scroll_speed"))

bg_blur_title = ctk.CTkLabel(settmenu,text=f"BG Blur Amount: {25}",font=("aeril",19,"normal"))
bg_blur_title.pack(anchor="w")

bg_blur_slider = ctk.CTkSlider(settmenu,width=600,command=update_bluramount_text,from_=0.01, to=0.35)
bg_blur_slider.pack(anchor="w")
bg_blur_slider.set(safe_settings_grab("blur_amount"))


setting_title = ctk.CTkLabel(settmenu,text="Privacy",font=("aeril",28,"normal"))
setting_title.pack(anchor="w",pady=(25,9))

use_disc_check = ctk.CTkCheckBox(settmenu,text=f"Use Discord Rich Presence",font=("aeril",19,"normal"))
use_disc_check.pack(anchor="w")
if safe_settings_grab("use_disc"):
    use_disc_check.select()



update_bluramount_text()
update_scrollspeed_text()

close_settings_menu_butt = ctk.CTkButton(root,text="❌",fg_color="#2B2B2B",hover_color="grey",bg_color="#2B2B2B",width=20,command=close_settings_menu)

###---------------------------------------------------------------------------------
###GENERAL FOCUS MENUS --------------------------------------------------------
bg_frame = ctk.CTkFrame(root,fg_color="black")
pywinstyles.set_opacity(bg_frame, value=0.8)

close = ctk.CTkButton(bg_frame,text="❌",fg_color="black",hover_color="grey",width=20,command=close_focus_menus)
close.place(relx=0.95,rely=0.01)

###---------------------------------------------------------------------------------
### ADD DATA MENU ----------------------------------------------------------
musicmenu = ctk.CTkFrame(root,border_width=2)

yt_menu = ctk.CTkFrame(musicmenu,border_width=2,bg_color="#474747")
yt_menu.place(relx=0,rely=0.18,relwidth=1,relheight=0.82)

yt_url_title = ctk.CTkLabel(yt_menu,text="YouTube URL")
yt_url_title.place(relx=0.05,rely=0.05)

yt_url_entry = ctk.CTkEntry(yt_menu)
yt_url_entry.place(relx=0.05,rely=0.15,relwidth=0.88) 

yt_instructions = ctk.CTkLabel(yt_menu,text=f"""Paste your video link here.\n\n\nThis will be added to:""",
    justify="left",
    font=("ariel",16,"bold"))
yt_instructions.place(relx=0.05,rely=0.27)

location_entry = ctk.CTkEntry(yt_menu)
location_entry.place(relx=0.05,rely=0.58,relwidth=0.9)
location_entry.insert(ctk.END,f"/{GLOBAL_MUSIC_DIR}")
location_entry.configure(state="disabled")

def open_appdata_song_dir():
    os.startfile(GLOBAL_MUSIC_DIR)

song_output_portal = ctk.CTkButton(location_entry,text="📂",width=15,border_width=2,border_color="#565B5E",fg_color="#343638",hover_color="#1a1a1a",bg_color="#565B5E",command=open_appdata_song_dir)
song_output_portal.place(relx=0.95,rely=0)

import_status = ctk.CTkLabel(yt_menu,text="",text_color="red")
import_status.place(relx=0.1,rely=0.85)
import_status.lift()

def safe_import_yturl():
    sus_url = yt_url_entry.get()
    if sus_url.replace(" ","") == "":
        import_status.configure(text="URL is empty!",text_color="red")
    else:
        import_status.configure(text="Importing... This could take awhile.",text_color="white")
        root.update() # dosntupdate till this ends. which is slowed by the download
        try:
            download_youtube(sus_url)
            import_status.configure(text="Video Imported Successfully!",text_color="green")
            compile_music_cache()
                
            for i in range(len(song_frames)):
                song_frames[i].destroy()
            song_frames.clear()

            root.after(0,create_songframes)
            close_focus_menus()
        except:
            import_status.configure(text="Somthing went wrong. Please check that the URL is correct.",text_color="red")
        

import_button = ctk.CTkButton(yt_menu,text="Import",border_width=2,fg_color="#2B2B2B",hover_color="#1a1a1a",command=safe_import_yturl)
import_button.place(relx=0.72,rely=0.85)

def add_yt_menu():
    bg_frame.place(relwidth=1,relheight=1)
    yt_menu.place(relx=0,rely=0.18,relwidth=1,relheight=0.82)
    dirmenu.place_forget()

    bg_frame.lift()
    musicmenu.lift()


from_yt_button = ctk.CTkButton(musicmenu,text="YouTube Download",border_width=2,fg_color="#2B2B2B",hover_color="#1a1a1a",font=("areil",18,"bold"),command=add_yt_menu)
from_yt_button.place(relx=0.02,rely=0.05)

def add_music_menu():
    location_entry.configure(state="normal")
    location_entry.delete(0,ctk.END)
    location_entry.insert(ctk.END,f"/{GLOBAL_MUSIC_DIR}")
    location_entry.configure(state="disabled")

    bg_frame.place(relwidth=1,relheight=1)
    musicmenu.place(relx=0.1,relwidth=0.8,
                rely=0.1,relheight=0.8)

    bg_frame.lift()
    musicmenu.lift()

def set_volume_slider(event=None):
    mixer.music.set_volume(volume_slider.get()/2)

volume_frame = ctk.CTkFrame(root,corner_radius=5,border_width=2,bg_color="#474747")
volume_frame.place(relx=0,rely=0.565,relwidth=0.04,relheight=0.3)

volume_slider = ctk.CTkSlider(volume_frame,orientation="vertical",command=set_volume_slider)
volume_slider.place(relx=0.2,rely=0.02,relheight=0.95)
volume_slider.set(0.2)
set_volume_slider()

add_music_butt = ctk.CTkButton(bottom_options_bar,fg_color="#2B2B2B",hover_color="#1a1a1a",text="➕",width=25,command=add_music_menu)
add_music_butt.place(relx=0.037,rely=0.05)

#ADD DIRECTORY

dirmenu = ctk.CTkFrame(musicmenu,border_width=2)

dirtitle = ctk.CTkLabel(dirmenu,text="Enter Directory Name:",font=("aeril",28,"bold"))
dirtitle.place(relx=0.05,rely=0.1)

dirname = ctk.CTkEntry(dirmenu,placeholder_text="You can use '/' to create subdirectorys",font=("aeril",22,"bold"))
dirname.place(relx=0.05,rely=0.25,relwidth=0.8)

dir_status = ctk.CTkLabel(dirmenu,text="",text_color="red")
dir_status.place(relx=0.1,rely=0.85)



def create_dir():
    try:
        dir_status.configure(text="")
        os.mkdir(GLOBAL_MUSIC_DIR+"/"+dirname.get())

        compile_music_cache()
                
        for i in range(len(song_frames)):
            song_frames[i].destroy()
        song_frames.clear()
        FOCUS_INDEX = 0

        root.after(0,create_songframes)

        close_focus_menus()
    except:
        dir_status.configure(text="An error occured. Please make sure that the \n name is avalable")


def add_directory_menu():
    bg_frame.place(relwidth=1,relheight=1)
    dirmenu.place(relx=0,rely=0.18,relwidth=1,relheight=0.82)
    yt_menu.place_forget()

    bg_frame.lift()
    musicmenu.lift()

#add_dir_image = ctk.CTkImage(Image.open(resource_path("assets/real folder.png")))

import_dir_button = ctk.CTkButton(dirmenu,text="Add Directory",border_width=2,fg_color="#2B2B2B",hover_color="#1a1a1a",command=create_dir)
import_dir_button.place(relx=0.72,rely=0.85)

dir_menu_butt = ctk.CTkButton(musicmenu,text="Create Directory",border_width=2,fg_color="#2B2B2B",hover_color="#1a1a1a",font=("areil",18,"bold"),command=add_directory_menu)
dir_menu_butt.place(relx=0.68,rely=0.05)

def apply_playoffset_tween(time=0):
    global playing_xoffset
    if time < 80:
        playing_xoffset = round(cubic_bounce(0,-80,time/80))
        time += 1
        root.after(5,lambda:apply_playoffset_tween(time))


def select_song(customindex=FOCUS_INDEX, songdir=None):
    global CURRENT_TRACKDATA
    global current_music_lenght
    global seek_offset

    if songdir == None:
        image, song_dir, name, uploader = all_songs[customindex]
    else:
        image, song_dir, name, uploader = safeload_song(songdir,usedir=True)

    CURRENT_TRACKDATA = (image,song_dir,name)

    mixer.music.load(song_dir)

    current_music_lenght = MP3(song_dir).info.length * 1000 # seconds -> ms

    seek_offset = 0
    timeline_slider.set(0)

    manage_pause(customstate=False) # starts playback from seek_offset (0) and sets play_start_time

    song_title_text.configure(text=os.path.basename(name).replace(".mp3",""))
    song_creator_text.configure(text=uploader)

    all_gdirnames = GLOBAL_MUSIC_DIR.replace('\\',"/").split("/")
    gdirlen = len(all_gdirnames)

    short_gdirname = f"{all_gdirnames[gdirlen-1]}"

    details = truncate_string(f"{short_gdirname} / {name.replace(".mp3","")} ({uploader})")

    threading.Thread(target=update_presence,args=(details,"vibing to:")).start()

    width, height = image.size

    root.update_idletasks()
    root_w = root.winfo_width()
    root_h = root.winfo_height()

    scale = max(root_w / width, root_h / height)

    new_width = int(width * scale)
    new_height = int(height * scale)

    image = image.resize((new_width//round(bg_blur_slider.get()*100), new_height//round(bg_blur_slider.get()*100)), Image.Resampling.LANCZOS)

    image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    bgimage = ctk.CTkImage(image, size=(new_width, new_height))
    bglabel.configure(image=bgimage)

def bind_songframe_button_thing(selection_index):
    global FOCUS_INDEX
    global PLAYING_INDEX
    global GLOBAL_MUSIC_DIR
    global RENDER_INDEX
    

    if selection_index == "back":
        FOCUS_INDEX = selection_index
        PLAYING_INDEX = None
        
        GLOBAL_MUSIC_DIR = os.path.dirname(GLOBAL_MUSIC_DIR)# back one
        compile_music_cache()

        for i in range(len(song_frames)):
            song_frames[i].destroy()
        song_frames.clear()
        FOCUS_INDEX = 0
        
        root.after(0,create_songframes)
    else:
        _, _, name, _ = all_songs[selection_index]
        if selection_index != PLAYING_INDEX:
            if ".mp3" in name:
                FOCUS_INDEX = selection_index
                PLAYING_INDEX = selection_index

                root.after(0,apply_playoffset_tween)
                select_song(selection_index)
            else:#if its a directory
                print(f"""-----------------------------------
                sus {selection_index}
                name {name}
                g dir {GLOBAL_MUSIC_DIR + "/" +name}""")
                FOCUS_INDEX = selection_index
                PLAYING_INDEX = None
                
                RENDER_INDEX = -100
                GLOBAL_MUSIC_DIR = GLOBAL_MUSIC_DIR + "/" +name
                compile_music_cache()

                
                
                for i in range(len(song_frames)):
                    song_frames[i].destroy()
                song_frames.clear()
                RENDER_INDEX = 5
                FOCUS_INDEX = 0

                root.after(0,create_songframes)

def create_songframes(spaceing=10):  
    for i in range(len(all_songs)): #use the filtered one
        image,_,songname, _ = all_songs[i]
        songframe = ctk.CTkFrame(root,width=300,height=40,border_width=2,corner_radius=0)

        
        btn = ctk.CTkFrame(songframe, width=300, height=40, fg_color="transparent")
        btn.pack()

        ctkimage = ctk.CTkImage(image,size=image.size)
        bg = ctk.CTkLabel(btn, image=ctkimage, text="")
        bg.place(relwidth=1, relheight=1)

        songlabel = ctk.CTkLabel(btn, text=songname.replace(".mp3",""), font=("Arial", 20, "bold"))
        songlabel.place(relx=0.5, rely=0.5, anchor="center")

        song_frames.append(songframe)
        
        #UI BUTTON ANIMATIONS
        songlabel.bind("<Button-1>", lambda event, idx=i: bind_songframe_button_thing(idx))
        bg.bind("<Button-1>", lambda event, idx=i: bind_songframe_button_thing(idx))
    if GLOBAL_MUSIC_DIR != BASE_DIR: # if its changed   oommgg this is SOOO mUCH BETTER then the last one

        all_gdirnames = GLOBAL_MUSIC_DIR.replace('\\',"/").split("/")
        gdirlen = len(all_gdirnames)

        short_gdirname = f".../{all_gdirnames[gdirlen-2]} / {all_gdirnames[gdirlen-1]}"
        #since this will only appear if they are in a upper direcotry we dont gotta worry about indexes

        dirname_label = ctk.CTkLabel(root,text=short_gdirname+"     ",width=300,height=40,corner_radius=0) # I CANNOT JUSTIFY THIS FOR THE LIFE OF ME SOMEONE PLEASE HELP WHAT IS GOING ON

        back_frame = ctk.CTkFrame(root,width=300,height=40,border_width=2,corner_radius=0)
        back_frame.pack_propagate(False)

        bg = ctk.CTkLabel(back_frame, text="")
        bg.place(relwidth=1, relheight=1)

        songlabel = ctk.CTkLabel(back_frame, text=" << Back", font=("Arial", 20, "bold"))
        songlabel.place(relx=0.5, rely=0.5, anchor="center")

        song_frames.append(back_frame)
        song_frames.append(dirname_label)
        
        #UI BUTTON ANIMATIONS
        songlabel.bind("<Button-1>", lambda event, idx="back": bind_songframe_button_thing(idx))
        bg.bind("<Button-1>", lambda event, idx="back": bind_songframe_button_thing(idx))

   

def get_average_color(img: Image.Image):
    small = img.resize((1, 1), Image.Resampling.LANCZOS)
    return small.getpixel((0, 0))

def update_songframes(spaceing=15):
    for i in range(len(song_frames)):
        songframe = song_frames[i]

        offset = (i - RENDER_INDEX)
        norm = offset * 0.25  # normalized angle
        curve = math.cos(norm)
        
        relative_y = offset * spaceing / 100
        relative_x = 0.6 + curve * 0.12

        if relative_y > -0.2 and relative_y < 1.2:
            if PLAYING_INDEX == i:
                songframe.place(relx=relative_x, relwidth=0.4, rely=relative_y,x=playing_xoffset)
            else:
                songframe.place(relx=relative_x, relwidth=0.4, rely=relative_y,x=0)
        else:
            songframe.place_forget()
    
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

    # update button color

def calulate_seconds_strtime(seconds):
    s = round(seconds)%60
    m = round(seconds//60)

    return f"{m}:{s:02d}"
   

def interpolate_render_index(): # change the focus index as much as you want, BECAUSE I USED TO USE SCRATCH!!! AH HA HA HA HA
    global FOCUS_INDEX
    global RENDER_INDEX
    global PLAYING_INDEX

    if not pause_state.get() and current_music_lenght != 0: # if true /= unpaused
        current_s = get_current_track_pos()

        if current_music_lenght > 0 and (current_music_lenght//1000) > current_s:
            slider_value = current_s / (current_music_lenght / 1000)
            #slider_value = max(0, min(1, slider_value+0.1)) # clamp so it can't run past the end of the track
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

    distance = FOCUS_INDEX - RENDER_INDEX - 4
    RENDER_INDEX += (distance / max(1,scroll_speed_slider.get()*100))
    
    if root.state() == "normal" and root.focus_get() != None:
        root.after(0,update_songframes)
    root.after(16,interpolate_render_index)

def show_console():
    ctypes.windll.kernel32.AllocConsole()
    sys.stdout = open("CONOUT$", "w")
    sys.stderr = open("CONOUT$", "w")

def keyrelease(event):
    print(event.keysym)
    key = event.keysym

    if key == "BackSpace" and GLOBAL_MUSIC_DIR != BASE_DIR:
        bind_songframe_button_thing("back")
    
    if key == "Up":
        skip_backwards_song()
    if key == "Down":
        skip_next_song()
    if key == "7":
        show_console()



#------------------------------
# UI INITS------------------------------
root.iconbitmap(resource_path("assets/placeify.ico"))
root.bind("<MouseWheel>",scroll_wheel)
root.bind("<KeyRelease>",keyrelease)

root.after(0,create_songframes)
root.after(1,interpolate_render_index)

root.mainloop()

#SHUTDOWN----------------------------
try:
    rpc_loop.call_soon_threadsafe(rpc_loop.stop)
except:
    pass
mixer.music.stop()
save_settings()
