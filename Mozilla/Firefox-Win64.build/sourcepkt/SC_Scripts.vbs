' VBScript source code
Option Explicit

const kErrorSuccess     = 0
const kErrorFailure     = 1

Sub AddComboTable
'On Error Resume Next
	Const msiViewModifyInsertTemporary = 7

	Dim dbView
	Dim recComBox
	Dim fsoMenuPrg, oFolder, oSubfolder, colFolders, strFolder
	Dim strMenuPrg, intCount
	
	strMenuPrg = Session.Property("ProgramMenuFolder") : CheckError
	Set dbView = Session.Database.OpenView("SELECT `Property`, `Order`, `Value`, `Text` FROM `ComboBox`") : CheckError
	dbView.Execute
	
	Set recComBox = Session.Installer.CreateRecord(4) : CheckError
	recComBox.StringData(1) = "MENU_FOLDERID"

	Set fsoMenuPrg = CreateObject("Scripting.FileSystemObject") : CheckError
	Set ofolder = fsoMenuPrg.GetFolder(strMenuPrg) : CheckError

	Set colFolders = oFolder.SubFolders : CheckError
	intCount = 1
	For Each oSubfolder in colFolders
		strFolder = oSubfolder.name 
		recComBox.IntegerData(2) = intCount
		recComBox.StringData(3) = strFolder
		recComBox.StringData(4) = ""
'		msgbox recComBox.StringData(1) & recComBox.StringData(2) & recComBox.StringData(3)
		dbView.Modify msiViewModifyInsertTemporary, recComBox : CheckError
		intCount = intCount + 1
	Next

	dbView.Close
	Set recComBox = Nothing
	Set dbView = Nothing
	Set fsoMenuPrg = Nothing
	Set ofolder = Nothing
End Sub

Sub CheckError
	Dim message, errRec
	If Err = 0 Then Exit Sub
	message = Err.Source & " " & Hex(Err) & ": " & Err.Description
	If Not installer Is Nothing Then
		Set errRec = installer.LastErrorRecord
		If Not errRec Is Nothing Then message = message & vbNewLine & errRec.FormatText
	End If
	writelog(message)
End Sub

function writelog(strlogmsg)
    On Error Resume Next
    const msiMessageTypeInfo = &H04000000
    dim oLogRec
'    MsgBox strlogmsg

    Set oLogRec = Installer.CreateRecord(1)

    oLogRec.stringdata(1) = strlogmsg
    oLogRec.stringdata(0) = "[1]"
    oLogRec.formattext
    message msiMessageTypeInfo, oLogRec
end function
