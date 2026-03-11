@echo off
:: CommandDeck Windows Services Uninstaller
:: Run as Administrator
title CommandDeck Service Uninstaller
echo Stopping and removing CommandDeck services...
nssm stop  CommandDeckRelay
nssm remove CommandDeckRelay confirm
nssm stop  CommandDeckAgent
nssm remove CommandDeckAgent confirm
echo Done.
pause
