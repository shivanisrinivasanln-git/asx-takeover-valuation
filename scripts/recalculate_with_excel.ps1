# Open a workbook in desktop Excel, recalculate every formula and save it as .xlsx, so the file
# holds Excel's own calculated values. Usage: recalculate_with_excel.ps1 <input.xlsx> <output.xlsx>
param(
    [Parameter(Mandatory = $true)][string]$InputPath,
    [Parameter(Mandatory = $true)][string]$OutputPath
)

$ErrorActionPreference = 'Stop'
$xlOpenXmlWorkbook = 51
$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false
try {
    $workbook = $excel.Workbooks.Open((Resolve-Path $InputPath).Path)
    $excel.CalculateFull()
    # Remove the author and last-saved-by names that Excel adds from the signed-in account
    $workbook.RemoveDocumentInformation(99)
    $workbook.SaveAs([System.IO.Path]::GetFullPath($OutputPath), $xlOpenXmlWorkbook)
    $workbook.Close($false)
}
finally {
    $excel.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($excel) | Out-Null
}
