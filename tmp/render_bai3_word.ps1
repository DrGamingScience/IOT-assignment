$ErrorActionPreference = 'Stop'
$outdir = 'D:\IOT-asm\tmp\bai3_report\render'
New-Item -ItemType Directory -Path $outdir -Force | Out-Null
$bai3Word = $null
$bai3Doc = $null
try {
    $bai3Word = New-Object -ComObject Word.Application
    $bai3Word.Visible = $false
    $bai3Word.DisplayAlerts = 0
    $bai3Doc = $bai3Word.Documents.Open('D:\IOT-asm\bai3\bai3_1\Bao_cao_Bai3_Phan1_Nhom16.docx', $false, $true, $false)
    $bai3Doc.Repaginate()
    $bai3Doc.ExportAsFixedFormat("$outdir\report.pdf", 17)
    Write-Output ('Pages: ' + $bai3Doc.ComputeStatistics(2))
} finally {
    if ($null -ne $bai3Doc) { $bai3Doc.Close(0) }
    if ($null -ne $bai3Word) { $bai3Word.Quit() }
}
