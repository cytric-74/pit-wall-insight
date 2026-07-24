@echo off
set "PATH=%PATH:%%SystemRoot%%=C:\Windows%"
set "PATH=%PATH%;C:\Windows\System32;C:\Windows;C:\Windows\System32\wbem;C:\Windows\System32\WindowsPowerShell\v1.0;C:\Program Files\nodejs;C:\Users\rohan\AppData\Roaming\npm"
C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe %*
