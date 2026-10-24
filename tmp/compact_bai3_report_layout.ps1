$ErrorActionPreference = 'Stop'
$source = 'D:\IOT-asm\bai3\bai3_1\Bao_cao_Bai3_Phan1_Nhom16.docx'
$temp = Join-Path (Split-Path -Parent $source) ([Guid]::NewGuid().ToString() + '.docx')
Copy-Item -LiteralPath $source -Destination $temp
Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem
$archive = [System.IO.Compression.ZipFile]::Open($temp, [System.IO.Compression.ZipArchiveMode]::Update)
try {
    $entry = $archive.GetEntry('word/document.xml')
    $reader = [IO.StreamReader]::new($entry.Open())
    try {
        $xml = [Xml.XmlDocument]::new()
        $xml.PreserveWhitespace = $true
        $xml.LoadXml($reader.ReadToEnd())
    } finally { $reader.Dispose() }

    $ns = [Xml.XmlNamespaceManager]::new($xml.NameTable)
    $ns.AddNamespace('w', 'http://schemas.openxmlformats.org/wordprocessingml/2006/main')
    $paragraphs = $xml.SelectNodes('//w:body//w:p', $ns)
    $diagram = $null
    $tree = $null
    $photoIntro = $null
    $photoHeading = $null
    foreach ($p in $paragraphs) {
        $text = ($p.SelectNodes('.//w:t', $ns) | ForEach-Object InnerText) -join ''
        if ($text.StartsWith('Producer --> default exchange')) { $diagram = $p }
        if ($text.StartsWith('bai3_1/')) { $tree = $p }
        if ($text.StartsWith('5 ')) { $photoHeading = $p }
    }
    if ($null -ne $photoHeading) { $photoIntro = $photoHeading.SelectSingleNode('following::w:p[1]', $ns) }
    if ($null -eq $diagram -or $null -eq $tree -or $null -eq $photoIntro) { throw 'Could not locate a cover-page code block or the outdated photo note.' }

    function Set-ParagraphLines($paragraph, [string[]]$lines, $namespaceManager, $document) {
        $w = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
        $pPr = $paragraph.SelectSingleNode('w:pPr', $namespaceManager)
        $run = $paragraph.SelectSingleNode('w:r', $namespaceManager)
        if ($null -eq $run) { $run = $document.CreateElement('w', 'r', $w) }
        foreach ($child in @($paragraph.ChildNodes)) {
            if ($child -ne $pPr -and $child -ne $run) { [void]$paragraph.RemoveChild($child) }
        }
        if ($null -eq $run.ParentNode) { [void]$paragraph.AppendChild($run) }
        foreach ($child in @($run.ChildNodes)) { [void]$run.RemoveChild($child) }
        for ($i = 0; $i -lt $lines.Count; $i++) {
            if ($i -gt 0) { [void]$run.AppendChild($document.CreateElement('w', 'br', $w)) }
            $t = $document.CreateElement('w', 't', $w)
            $t.InnerText = $lines[$i]
            $space = $document.CreateAttribute('xml', 'space', 'http://www.w3.org/XML/1998/namespace')
            $space.Value = 'preserve'
            [void]$t.Attributes.Append($space)
            [void]$run.AppendChild($t)
        }
    }

    Set-ParagraphLines $diagram @(
        'Producer --> default exchange --> it4735.nhom16.telemetry --> Consumer',
        '                 routing key = queue name                 <-- ACK'
    ) $ns $xml
    Set-ParagraphLines $tree @(
        'bai3_1/',
        '  common.py                 # cau hinh RabbitMQ va queue',
        '  producer.py, consumer.py  # gui va nhan thong diep',
        '  compose.yaml, Dockerfile  # RabbitMQ va cac container',
        '  requirements.txt          # thu vien pika',
        '  .env.example, .dockerignore # cau hinh mau va loai file'
    ) $ns $xml
    Set-ParagraphLines $photoIntro @(
        'Các ảnh dưới đây ghi lại log chương trình và trạng thái queue trong quá trình thử nghiệm.'
    ) $ns $xml

    $entry.Delete()
    $newEntry = $archive.CreateEntry('word/document.xml', [System.IO.Compression.CompressionLevel]::Optimal)
    $stream = $newEntry.Open()
    try { $xml.Save($stream) } finally { $stream.Dispose() }
} finally { $archive.Dispose() }

# Confirm both paragraphs were written before replacing the original file.
$verify = [System.IO.Compression.ZipFile]::OpenRead($temp)
try {
    $entry = $verify.GetEntry('word/document.xml')
    $reader = [IO.StreamReader]::new($entry.Open())
    try {
        $check = [Xml.XmlDocument]::new()
        $check.LoadXml($reader.ReadToEnd())
    } finally { $reader.Dispose() }
    $checkNs = [Xml.XmlNamespaceManager]::new($check.NameTable)
    $checkNs.AddNamespace('w', 'http://schemas.openxmlformats.org/wordprocessingml/2006/main')
    $texts = @($check.SelectNodes('//w:body//w:p', $checkNs) | ForEach-Object { ($_.SelectNodes('.//w:t', $checkNs) | ForEach-Object InnerText) -join '' })
    if (-not ($texts -contains '202400057')) {
        $tableText = ($check.SelectNodes('//w:tbl//w:t', $checkNs) | ForEach-Object InnerText) -join ' '
        if ($tableText -notmatch '202400057') { throw 'Roster verification failed.' }
    }
    if (-not ($texts | Where-Object { $_ -like 'Producer --> default exchange*' })) { throw 'Diagram verification failed.' }
    if (-not ($texts | Where-Object { $_ -like 'bai3_1/*' })) { throw 'File tree verification failed.' }
} finally { $verify.Dispose() }
Move-Item -LiteralPath $temp -Destination $source -Force
Write-Output 'Compacted cover-page diagram and file tree; preserved the roster and embedded images.'




