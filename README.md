# ActivityMonitorApp_Update
A Windows desktop app built with Python and Tkinter that monitors active window titles, logs keyboard and mouse events, and displays real-time system stats (CPU, memory, disk, network). Features include pause/resume monitoring, theme switching (dark/light), and log saving. Uses pynput, psutil, and pywin32.

Summary of required installations:

| Library | Used for                                       | Install command       |
| ------- | ---------------------------------------------- | --------------------- |
| pynput  | Keyboard and mouse event listening             | `pip install pynput`  |
| psutil  | System statistics (CPU, memory, disk, network) | `pip install psutil`  |
| pywin32 | Windows API access (`win32gui`)                | `pip install pywin32` |
