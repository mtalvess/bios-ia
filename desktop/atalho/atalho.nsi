; Atalho do BIOS IA (versão gratuita no claude.ai) abrindo como app, em janela própria
Unicode true
!include "MUI2.nsh"

!define APP  "BIOS IA"
!define LINK "https://claude.ai/artifact/BCy8bwKmWfscNjWPtFYifH"
!define CHAVE "Software\Microsoft\Windows\CurrentVersion\Uninstall\BIOS-IA-Atalho"

Name "${APP}"
OutFile "BIOS-IA-Atalho.exe"
InstallDir "$LOCALAPPDATA\BIOS IA Atalho"
RequestExecutionLevel user
SetCompressor /SOLID lzma
BrandingText "BIOS · tecnologia aplicada ao crescimento do seu negócio"

!define MUI_ICON   "icon.ico"
!define MUI_UNICON "icon.ico"
!define MUI_WELCOMEPAGE_TITLE "Atalho do BIOS IA"
!define MUI_WELCOMEPAGE_TEXT "Cria o atalho do escritório BIOS IA na área de trabalho e no menu Iniciar. Ele abre em janela própria, como um programa.$\r$\n$\r$\nDepois é só clicar com o botão direito no atalho e escolher Fixar na barra de tarefas."
!define MUI_FINISHPAGE_RUN
!define MUI_FINISHPAGE_RUN_TEXT "Abrir o BIOS IA agora"
!define MUI_FINISHPAGE_RUN_FUNCTION Abrir

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_LANGUAGE "PortugueseBR"

Var NAV

Function AcharNavegador
  StrCpy $NAV "$PROGRAMFILES32\Microsoft\Edge\Application\msedge.exe"
  IfFileExists $NAV fim
  StrCpy $NAV "$PROGRAMFILES64\Microsoft\Edge\Application\msedge.exe"
  IfFileExists $NAV fim
  StrCpy $NAV "$PROGRAMFILES64\Google\Chrome\Application\chrome.exe"
  IfFileExists $NAV fim
  StrCpy $NAV "$PROGRAMFILES32\Google\Chrome\Application\chrome.exe"
  IfFileExists $NAV fim
  StrCpy $NAV "$LOCALAPPDATA\Google\Chrome\Application\chrome.exe"
  IfFileExists $NAV fim
  StrCpy $NAV ""
  fim:
FunctionEnd

Function Abrir
  ExecShell "open" "$DESKTOP\${APP}.lnk"
FunctionEnd

Section "Atalho"
  SetOutPath "$INSTDIR"
  File "icon.ico"
  WriteUninstaller "$INSTDIR\Remover atalho BIOS IA.exe"
  Call AcharNavegador
  StrCmp $NAV "" semNavegador
    CreateShortCut "$DESKTOP\${APP}.lnk" "$NAV" "--app=${LINK}" "$INSTDIR\icon.ico" 0 SW_SHOWNORMAL "" "Escritório BIOS IA"
    CreateShortCut "$SMPROGRAMS\${APP}.lnk" "$NAV" "--app=${LINK}" "$INSTDIR\icon.ico" 0 SW_SHOWNORMAL "" "Escritório BIOS IA"
    Goto pronto
  semNavegador:
    ; sem Edge/Chrome: abre no navegador padrão
    WriteINIStr "$INSTDIR\${APP}.url" "InternetShortcut" "URL" "${LINK}"
    CreateShortCut "$DESKTOP\${APP}.lnk" "$INSTDIR\${APP}.url" "" "$INSTDIR\icon.ico"
    CreateShortCut "$SMPROGRAMS\${APP}.lnk" "$INSTDIR\${APP}.url" "" "$INSTDIR\icon.ico"
  pronto:
  WriteRegStr HKCU "${CHAVE}" "DisplayName" "${APP} (atalho)"
  WriteRegStr HKCU "${CHAVE}" "Publisher" "BIOS"
  WriteRegStr HKCU "${CHAVE}" "DisplayIcon" "$INSTDIR\icon.ico"
  WriteRegStr HKCU "${CHAVE}" "UninstallString" '"$INSTDIR\Remover atalho BIOS IA.exe"'
  WriteRegDWORD HKCU "${CHAVE}" "NoModify" 1
  WriteRegDWORD HKCU "${CHAVE}" "NoRepair" 1
SectionEnd

Section "Uninstall"
  Delete "$DESKTOP\${APP}.lnk"
  Delete "$SMPROGRAMS\${APP}.lnk"
  RMDir /r "$INSTDIR"
  DeleteRegKey HKCU "${CHAVE}"
SectionEnd
