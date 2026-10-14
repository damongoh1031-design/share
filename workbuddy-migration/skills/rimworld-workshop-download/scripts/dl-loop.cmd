@echo off
cd /d C:/SteamCMDData
echo START %DATE% %TIME% > dl-cmd-result.txt
for /f "usebackq delims=" %%i in ("C:/SteamCMDData/ids-final.txt") do (
  echo force_install_dir "C:/SteamCMDData/steam" > dl-one.txt
  echo login anonymous >> dl-one.txt
  echo workshop_download_item 294100 %%i >> dl-one.txt
  echo quit >> dl-one.txt
  "C:/SteamCMDData/sc2/steamcmd.exe" +runscript "C:/SteamCMDData/dl-one.txt" > nul 2>&1
  echo %%i OK >> dl-cmd-result.txt
)
echo ALLDONE %DATE% %TIME% >> dl-cmd-result.txt
