$ErrorActionPreference = 'Stop'
$reportWord = $null
$reportDoc = $null
try {
    $reportWord = New-Object -ComObject Word.Application
    $reportWord.Visible = $false
    $reportWord.DisplayAlerts = 0
    $reportDoc = $reportWord.Documents.Open('D:\IOT-asm\bai2\output\bao-cao.docx', $false, $true, $false)
    $reportDoc.Repaginate()
    $reportDoc.ExportAsFixedFormat('D:\IOT-asm\tmp\docs\bai2_render\bao-cao.pdf', 17)
    Write-Output ('Pages: ' + $reportDoc.ComputeStatistics(2))
} finally {
    if ($null -ne $reportDoc) { $reportDoc.Close(0) }
    if ($null -ne $reportWord) { $reportWord.Quit() }
}
