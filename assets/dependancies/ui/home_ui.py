import customtkinter as ctk

def place_homeframe(homeframe):
    homeframe.place(relwidth=1,relheight=0.83,rely=0.17)

def main(root):
    homeframe = ctk.CTkScrollableFrame(root,fg_color="#0D0D0D",corner_radius=0)

    recent_playlists_title = ctk.CTkLabel(homeframe,text="Top Playlists",font=("@Microsoft YaHei UI",26,"bold")) #dosnt look bad actually
    recent_playlists_separator = ctk.CTkFrame(homeframe,height=3,width=680)

    recent_playlists_title.pack(anchor="w",padx=5,pady=15)
    recent_playlists_separator.pack(anchor="w",padx=20,pady=5)

    recent_playlists_frame = ctk.CTkFrame(homeframe,fg_color="#0D0D0D",width=800,height=155,corner_radius=0)#invisible bar, but i can use .place on it and the scrollbar will still work :D
    recent_playlists_frame.pack(anchor="w",pady=5)

    recent_songs_title = ctk.CTkLabel(homeframe,text="Recents",font=("@Microsoft YaHei UI",26,"bold")) #dosnt look bad actually
    recent_songs_separator = ctk.CTkFrame(homeframe,height=3,width=680)

    recent_songs_title.pack(anchor="w",padx=5,pady=(10,5))
    recent_songs_separator.pack(anchor="w",padx=20,pady=5)

    recent_songs_frame = ctk.CTkFrame(homeframe,fg_color="#090909",width=680,height=700)
    recent_songs_frame.pack(anchor="w",padx=20,pady=5)
    recent_songs_frame.pack_propagate(False)

    return homeframe, recent_songs_frame, recent_playlists_frame
