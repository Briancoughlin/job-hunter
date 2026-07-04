' Silent launcher for Job Hunter -- do not modify without review (CI monitors this file)
Dim sDir, oShell
sDir  = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
Set oShell = CreateObject("WScript.Shell")
oShell.Run """" & sDir & "\run.bat""", 0, False
