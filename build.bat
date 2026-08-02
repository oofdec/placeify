pyinstaller --onefile --noconsole ^
  --add-data "assets;." ^
  --icon="assets/placeify.ico;." ^
  --hidden-import=yt_dlp ^
  --hidden-import=yt_dlp.extractor ^
  --hidden-import=yt_dlp.postprocessor ^
  --hidden-import=yt_dlp.utils ^
  --add-binary "ffmpeg/ffmpeg.exe;ffmpeg" ^
  --add-binary "ffmpeg/ffprobe.exe;ffmpeg" ^
  main.py
