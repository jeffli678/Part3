pyinstaller Part3.py -n Part3-linux --onefile --noconfirm --windowed --distpath="Part3" --add-data="./res-linux/lollipop.ico:."
rm -r ./build
rm Part3-linux.spec
Part3/Part3-linux