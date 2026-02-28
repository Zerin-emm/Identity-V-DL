### build init
pyinstaller -c --uac-admin --onedir --icon=16.ico --add-data "16.ico;." --upx-dir="D:\upx-5.1.0-win64" --contents-directory "init_data" --clean init.py

### build run
pyinstaller --onedir --windowed --icon=16.ico --add-data "16.ico;." --upx-dir="D:\upx-5.1.0-win64" --contents-directory "run_data" --clean run.py

###build UI_Server
pyinstaller --onedir --windowed --icon=16.ico --add-data "16.ico;." --upx-dir="D:\upx-5.1.0-win64" --contents-directory "run_data" --clean UI_Server.py

### build-tree
│  DownloadApp.exe
│  downloadIPC.exe
│  OrbitSDK.dll
│
├─idv-login             #Folder
│  │  LoginApp.exe
│  │
│  ├─init                   #Folder
│  │  │  init.exe
│  │  │
│  │  └─init_data     #Folder
│  │
│  └─run                   #Folder
│      │  run.exe
│      │
│      └─run_data     #Folder
│
└─UI_Server             #Folder
    │  UI_Server.exe
    │
    └─run_data         #Folder