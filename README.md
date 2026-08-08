Placeify is an **lightweight**, open‑source music player that lets you import songs straight from YouTube using yt‑dlp, then listen offline with **zero ads**, **clean UI**, **thumbnails**, **playlists**, and more.

Features:

    - ⬇️ Import music from YouTube links
    - 📵 Offline playback (no ads, no buffering)
    - 📂 Custom directories (playlists/albums)
    - 🔀 Shuffle + loop
    - ➡️ Next/previous track
    - 🖼️ Thumbnail support
    - 🫧 Clean, modern UI with VERY cool animations
    - 🔧 Fully open‑source
    - 🪟 Windows EXE build available (no linux, sorry)

-------------------------------------------------------------------------------
**HOW TO USE**
-------------------------------------------------------------------------------

**NON-DEVELOPERS**

  If you’re not a developer, don’t worry — just download the EXE version from the Releases page.
  
  1. Open `placeify.exe`
  2. Click the + button
  3. Paste a YouTube link
  4. Hit Import
  5. Enjoy your music offline
  
  You can also create folders (playlists) using the folder icon.
  Folders can even contain other folders — go crazy with that one.

-------------------------------------------------------------------------------

🧑‍💻**DEVELOPERS** (if you want to edit it)

Placeify is written entirely in Python.
If you want to run main.py, you’ll need these dependencies installed:

    - customtkinter
    - pillow
    - pygame
    - yt-dlp
    - pypresence
    - pywinstyles
    - asyncio
    - mutagen
    - io (BytesIO)
    - ffmpeg (external)
    - ffprobe (external)
    

Once installed simply, run:

`main.py`

**⚠️⚠️IMPORTANT⚠️⚠️**

You **NEEEEEED** **FFMPEG** AND **FFPROBE** IN YOUR LOCAL DIRECTORY.

You can find it here: 

https://github.com/GyanD/codexffmpeg/releases

Look for the latest build

-------------------------------------------------------------------------------
📜**LICENSE**

Placeify uses the **MIT License**, partially so that you can use it, and so that I don't get sued if something doesn't work.
You can find that in the `LICENSE` file or in the "License" section on the repository page.

-------------------------------------------------------------------------------
🪳**BUGS AND ERRORS**

Placeify is still pretty new, as I only started it about like a week ago. Although most bugs have been sorted out, there are still many chances that there are more to find. If you found any, please let me know!

I also apologize in advance, I know that the engine is just 700 lines of spaghetti, and I don't know how to structure it and I WILL reformat it later I swear
