Set objShell = WScript.CreateObject("WScript.Shell")
strDesktop = objShell.SpecialFolders("Desktop")
Set objShortcut = objShell.CreateShortcut(strDesktop & "\Ambulance App.lnk")
objShortcut.TargetPath = WScript.Arguments(0)
objShortcut.IconLocation = WScript.Arguments(1)
objShortcut.Save
