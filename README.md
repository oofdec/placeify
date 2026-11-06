Placeify is a free, open-source music player that lets you import songs directly from YouTube and Spotify, then listen to them offline without ads, buffering, subscriptions, or other nonsense.


Features:
---
- ⬇️ Import music from YouTube or Spotify Links
- 📵 Offline playback (no ads, no buffering)
- 📂 Custom directories (playlists/albums)
- 🔀 Shuffle + loop
- ➡️ Next/previous track
- 🖼️ Thumbnail support
- 🫧 Clean, modern UI with VERY cool animations
- 🔧 Fully open‑source
- 🪟 Windows EXE build available (no linux, sorry)
- AND MORE!!!!!!
-------------------------------------------------------------------------------
**HOW TO USE**
-------------------------------------------------------------------------------

**NON-DEVELOPERS**

  If you’re not a developer, don’t worry - just download the EXE version from the Releases page.
  
  1. Open `placeify.exe`
  2. Click the + button
  3. Paste a YouTube, or Spotify playlist/URL (it MUST BE PUBLIC!!!) 
  4. Hit Import
  5. Enjoy!!!
  
  You can also create folders (playlists) using the folder icon.
  Since Placeify uses a subdirectory system, playlists can be inside playlists, inside playlists, inside playlists, inside playlists, inside playlists, inside playli

  I recommend placing the EXE into the appdata folder that Placeify makes, but thats just me ig...

-------------------------------------------------------------------------------

🧑‍💻**Running the source code** 

Placeify is written entirely in Python.
If you want to run main.py, you’ll need these dependencies installed:


| Library Name | Purpose |
|--|--|
| `customtkinter` | Graphics Library |
| `pillow` | Image Management / Editing |
| `pygame` | Music Player |
| `yt-dlp` | Audio Downloading |
| `pypresence` | Discord Rich Presence (optional, dont worry.) |
| `pywinstyles` | Extra UI effects (Opacity support for `ctk`) |
| `mutagen` | ID3 Tag Management (Title, Author, Image) |


📦**External Dependancies**
| Binary Name | Purpose |
|--|--|
| `ffmpeg` | Used for thumbnail embedding and formatting |
| `Deno` | Used for YouTube JS resolving |

Once installed, simply drop these into:
```directory or seomthing
assets/downloading
```

Then, you can finally run `main.py`

-------------------------------------------------------------------------------
📜**LICENSE**

Placeify is released under the **MIT License**, meaning you can use it, modify it, and distribute it!

It also means I'm not the one responsible if it explodes and bricks your pc


You can find that in the `LICENSE` file or in the "License" section on the repository page.

-------------------------------------------------------------------------------
🪳**BUGS AND ERRORS**

Even though most bugs and errors have been sorted out, there are still always things that can go wrong! If you notice anything, then do the following:


1.  Press **7** to open the debug console.
2.  Try to reproduce the issue.
3.  Open an issue on GitHub.
4.  Include any useful logs.

also, please don't report that the codebase is ugly, trust me,
**i know.**

![Project Logo](./assets/placeify.png)
