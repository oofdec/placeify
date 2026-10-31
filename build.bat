pyinstaller --onefile --noconsole^
  --clean ^
  --name=placeify^
  --add-data "assets;assets" ^
  --icon="assets/placeify.ico" ^
  main.py

echo build complete!
pause
