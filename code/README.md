### build init

pyinstaller -c --uac-admin --onedir --icon=16.ico --add-data "16.ico;." --upx-dir="D:\\upx-5.1.0-win64" --contents-directory "init\_data" --clean init.py

### build run

pyinstaller --onedir --windowed --icon=16.ico --add-data "16.ico;." --upx-dir="D:\\upx-5.1.0-win64" --contents-directory "run\_data" --clean run.py

### build UI\_Server

pyinstaller --onedir --windowed --icon=16.ico --add-data "16.ico;." --upx-dir="D:\\upx-5.1.0-win64" --contents-directory "UI\_Server\_data" --clean UI\_Server.py

### build-tree

│  DownloadApp.exe
│
├─DownloadApp
│  │  downloadIPC.exe
│  │  OrbitSDK.dll
│  │
│  └─UI_Server
│      │  UI_Server.exe
│      │
│      └─UI_Server_data
│
└─idv-login
    │  dwrg.ico
    │  LoginApp.exe
    │
    ├─init
    │  │  init.exe
    │  │
    │  └─init_data
    │
    └─run
        │  run.exe
        │
        └─run_data
