; Instalador do BIOS IA (Windows, por usuário, sem precisar de administrador)
Unicode true
!include "MUI2.nsh"

!define APP      "BIOS IA"
!define EXE      "BIOS IA.exe"
!define VERSAO   "1.0.0"
!define CHAVE    "Software\Microsoft\Windows\CurrentVersion\Uninstall\BIOS-IA"

Name "${APP}"
OutFile "..\dist\BIOS-IA-Instalador-${VERSAO}.exe"
InstallDir "$LOCALAPPDATA\Programs\BIOS IA"
InstallDirRegKey HKCU "Software\BIOS IA" "Pasta"
RequestExecutionLevel user
SetCompressor /SOLID lzma
BrandingText "BIOS · tecnologia aplicada ao crescimento do seu negócio"

!define MUI_ICON   "icon.ico"
!define MUI_UNICON "icon.ico"
!define MUI_ABORTWARNING
!define MUI_FINISHPAGE_RUN "$INSTDIR\${EXE}"
!define MUI_FINISHPAGE_RUN_TEXT "Abrir o BIOS IA agora"

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_LANGUAGE "PortugueseBR"

Section "BIOS IA"
  SetOutPath "$INSTDIR"
  File /r "..\dist\win-unpacked\*.*"
  File "icon.ico"
  WriteUninstaller "$INSTDIR\Desinstalar BIOS IA.exe"
  CreateShortCut "$DESKTOP\${APP}.lnk" "$INSTDIR\${EXE}" "" "$INSTDIR\icon.ico"
  CreateDirectory "$SMPROGRAMS\${APP}"
  CreateShortCut "$SMPROGRAMS\${APP}\${APP}.lnk" "$INSTDIR\${EXE}" "" "$INSTDIR\icon.ico"
  CreateShortCut "$SMPROGRAMS\${APP}\Desinstalar ${APP}.lnk" "$INSTDIR\Desinstalar BIOS IA.exe"
  WriteRegStr HKCU "Software\BIOS IA" "Pasta" "$INSTDIR"
  WriteRegStr HKCU "${CHAVE}" "DisplayName" "${APP}"
  WriteRegStr HKCU "${CHAVE}" "DisplayVersion" "${VERSAO}"
  WriteRegStr HKCU "${CHAVE}" "Publisher" "BIOS"
  WriteRegStr HKCU "${CHAVE}" "DisplayIcon" "$INSTDIR\icon.ico"
  WriteRegStr HKCU "${CHAVE}" "UninstallString" '"$INSTDIR\Desinstalar BIOS IA.exe"'
  WriteRegDWORD HKCU "${CHAVE}" "NoModify" 1
  WriteRegDWORD HKCU "${CHAVE}" "NoRepair" 1
SectionEnd

Section "Uninstall"
  ; os dados (tarefas e a chave do Claude) ficam em %APPDATA%\bios-ia e não são apagados
  Delete "$DESKTOP\${APP}.lnk"
  RMDir /r "$SMPROGRAMS\${APP}"
  RMDir /r "$INSTDIR"
  DeleteRegKey HKCU "${CHAVE}"
  DeleteRegKey HKCU "Software\BIOS IA"
SectionEnd
