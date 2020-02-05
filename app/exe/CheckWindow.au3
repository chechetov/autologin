#Region ;**** Directives created by AutoIt3Wrapper_GUI ****
#AutoIt3Wrapper_Compile_Both=y
#AutoIt3Wrapper_UseX64=y
#AutoIt3Wrapper_Change2CUI=y
#AutoIt3Wrapper_Add_Constants=n
#AutoIt3Wrapper_Run_Tidy=y
#EndRegion ;**** Directives created by AutoIt3Wrapper_GUI ****
#include <FileConstants.au3>
#include <MsgBoxConstants.au3>
#include <File.au3>
#include <Array.au3>
#include <WinAPI.au3>

Opt("TrayAutoPause", 0)

$StandardSleep = 500

If $CmdLine[0] = 0 Then
	ConsoleWrite(@CRLF & "No title in arguments!" & @CRLF)
	Exit
EndIf

If $CmdLine[1] Then

	ConsoleWrite(@CRLF & "Args: " & $CmdLine[1])

	$MainWindowTitle = $CmdLine[1]
	$MainWindowHandle = FindAWindow($MainWindowTitle, 1)
	Sleep($StandardSleep)

	If $MainWindowHandle Then
		ConsoleWrite(@CRLF & "Window found: " & $MainWindowHandle & @CRLF)
		Exit 0
	Else
		ConsoleWrite(@CRLF & "Window not found: " & $MainWindowHandle & @CRLF)
		Exit 1
	EndIf
EndIf


Func FindAWindow($WindowTitle, $MessageNeeded, $CallingAttempt = 1)

	; Retrieve a list of window handles.
	Local $aList = WinList()
	Local $aWindowHandle = 555
	Local $MaxAttempts = 3
	Local $WindowFound = 0

	ConsoleWrite(@CRLF & "FindAWindow start, attempt " & $CallingAttempt & " of " & $MaxAttempts & @CRLF)
	ConsoleWrite("Target: " & $WindowTitle & @CRLF)
	Sleep(500)

	If $CallingAttempt <= $MaxAttempts Then
		; Loop through the array displaying only visible windows with a title.
		For $i = 1 To $aList[0][0]
			If $aList[$i][0] <> "" And BitAND(WinGetState($aList[$i][1]), 2) And $aList[$i][0] == $WindowTitle Then
				If $MessageNeeded == 1 Then
					ConsoleWrite("Title: " & $aList[$i][0] & @CRLF & "Handle: " & $aList[$i][1] & @CRLF)
				EndIf
				$aWindowHandle = $aList[$i][1]
				ConsoleWrite("Found a window: " & $aWindowHandle & @CRLF)
				$WindowFound = 1
				ExitLoop
			EndIf
			Sleep(10)
		Next
	EndIf

	If ($WindowFound == 0 And $CallingAttempt < $MaxAttempts) Then

		ConsoleWrite("Could not find a window: " & $WindowTitle & @CRLF)
		ConsoleWrite("Current handle: " & $aWindowHandle & @CRLF)
		ConsoleWrite("Retrying ..." & @CRLF)
		Sleep(3000)
		FindAWindow($WindowTitle, 1, $CallingAttempt + 1)

	EndIf

	If ($WindowFound == 0 And $CallingAttempt == $MaxAttempts) Then
		ConsoleWrite("FindAWindow(): reached MaxAttemps: " & $MaxAttempts & " not found " & @CRLF)
		Return $aWindowHandle
	EndIf

	If $WindowFound == 1 Then
		ConsoleWrite("FindAWindow(): found " & @CRLF)
		ConsoleWrite("Current handle: " & $aWindowHandle & @CRLF)
		Return $aWindowHandle
	EndIf

EndFunc   ;==>FindAWindow
