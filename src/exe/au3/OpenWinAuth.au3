#Region ;**** Directives created by AutoIt3Wrapper_GUI ****
#AutoIt3Wrapper_Compile_Both=y
#AutoIt3Wrapper_UseX64=y
#AutoIt3Wrapper_Change2CUI=y
#AutoIt3Wrapper_Add_Constants=n
#AutoIt3Wrapper_Run_Tidy=y
#EndRegion ;**** Directives created by AutoIt3Wrapper_GUI ****
#Region ;**** Directives created by AutoIt3Wrapper_GUI ****

#include <FileConstants.au3>
#include <MsgBoxConstants.au3>
#include <File.au3>
#Include <Array.au3>

Opt("TrayAutoPause",0)
launch_winauth()

Func PrintList($List)
    If IsArray($List) Then
        Local $txt = ""
        For $i = 0 to UBound($List) -1
            $txt = $txt & "," & $List[$i]
        Next
        Local $out = StringMid($txt,2)
        Global $Result = "[" & $out & "]"
        ConsoleWrite($Result & @CRLF)
        Return $Result
    Else
        ConsoleWrite("List Error: " & "variable is not an array or a list" & @CRLF)
    EndIf
EndFunc   ;==>PrintList

Func CleanCodeFile()

	$FullPath = _PathFull("..\tmp", @ScriptDir)
	$sFileName = $FullPath & "\winauth_code.txt"

	$aTextBefore = FileRead($sFileName, 3)
	PrintList("Before: " & $aTextBefore & @CRLF)

	FileDelete($sFileName)
	FileOpen($sFileName, 0)
	FileClose($sFileName)

	$aTextAfter = FileRead($sFileName, 3)
	PrintList("After: " & $aTextAfter & @CRLF)
EndFunc

Func launch_winauth()

	CleanCodeFile()

	Local $WinAuthPath = "WinAuth.exe"
    Local $iPID = Run($WinAuthPath, "", @SW_SHOWMAXIMIZED)
    WinWait("[CLASS:WinAuth]", "", 8)
	; I hope 7 seconds is enough
	Sleep(1000 * 7 )
	Local $Res = get_code_from_clipboard()
	save_the_code($Res)
	Sleep( 1000 )
	WinSetState("WinAuth", "", @SW_MINIMIZE)

    ProcessClose($iPID)
EndFunc   ;==>Example

Func save_the_code($Code)

   $FullPath = _PathFull("..\tmp", @ScriptDir)
   $sFileName = $FullPath & "\winauth_code.txt"

   ; Open file - deleting any existing content
   $hFilehandle = FileOpen($sFileName, $FO_OVERWRITE)

   ; Write a line
   ConsoleWrite("Writing code: " & $Code & @CRLF)
   FileWrite($hFilehandle, $Code)
   FileClose($hFilehandle)

EndFunc

Func get_code_from_clipboard()
    ; Retrieve the data stored in the clipboard.
	Sleep(1000)
    Local $sData = ClipGet()
	Sleep(1000)
    ; Retrieve the data stored in the clipboard.
	ConsoleWrite("Clipboard: " & $sData & @CRLF)
	return $sData

EndFunc   ;==>Example