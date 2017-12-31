pyinstaller Part3.py --onefile --runtime-tmpdir="./" --distpath="Part3" --add-binary="res-win/ffmpeg.exe;." --add-binary="res-win/ffprobe.exe;." --add-data="res-win/lollipop.ico;." --icon="res-win/lollipop.ico"
rmdir /S /Q build
Part3\Part3.exe