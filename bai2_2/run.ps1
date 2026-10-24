param(
    [string]$Mssv,
    [ValidateRange(1, 2147483647)][int]$IntervalSeconds = 5,
    [string]$Broker = 'tcp://broker.hivemq.com:1883',
    [switch]$BuildOnly,
    [switch]$Help
)

$ErrorActionPreference = 'Stop'

if ($Help) {
    Write-Host '.\run.ps1 -Mssv YOUR_MSSV [-IntervalSeconds 5] [-Broker tcp://broker.hivemq.com:1883]'
    Write-Host '.\run.ps1 -BuildOnly'
    return
}
if (-not $BuildOnly -and $Mssv -notmatch '^[A-Za-z0-9_-]+$') {
    throw 'Supply your actual student ID: .\run.ps1 -Mssv YOUR_MSSV'
}
foreach ($tool in @('javac', 'java')) {
    if (-not (Get-Command $tool -ErrorAction SilentlyContinue)) {
        throw "Cannot find $tool. Install JDK 17 or newer and add its bin directory to PATH."
    }
}

$libraryDirectory = Join-Path $PSScriptRoot 'lib'
$outputDirectory = Join-Path $PSScriptRoot 'out'
New-Item -ItemType Directory -Path $libraryDirectory, $outputDirectory -Force | Out-Null

# Use a cached Maven dependency if present; otherwise download the two official artifacts.
$dependencies = @(
    @{ Path = 'org/eclipse/paho/org.eclipse.paho.client.mqttv3/1.2.5/org.eclipse.paho.client.mqttv3-1.2.5.jar' },
    @{ Path = 'org/json/json/20240303/json-20240303.jar' }
)
foreach ($dependency in $dependencies) {
    $destination = Join-Path $libraryDirectory (Split-Path $dependency.Path -Leaf)
    if (Test-Path -LiteralPath $destination) {
        continue
    }
    $cachedJar = Join-Path $env:USERPROFILE ('.m2/repository/' + $dependency.Path)
    if (Test-Path -LiteralPath $cachedJar) {
        Copy-Item -LiteralPath $cachedJar -Destination $destination
        continue
    }
    $download = $destination + '.download'
    $uri = 'https://repo.maven.apache.org/maven2/' + $dependency.Path
    Write-Host "Downloading $(Split-Path $destination -Leaf)..."
    try {
        Invoke-WebRequest -Uri $uri -OutFile $download -UseBasicParsing -TimeoutSec 30
        Move-Item -LiteralPath $download -Destination $destination
    } catch {
        if (Test-Path -LiteralPath $download) {
            Remove-Item -LiteralPath $download
        }
        throw "Dependency download failed. Download $uri into '$libraryDirectory', then retry. Details: $($_.Exception.Message)"
    }
}

$sourceDirectory = Join-Path $PSScriptRoot 'src/main/java'
$sources = @(Get-ChildItem -LiteralPath $sourceDirectory -Filter '*.java' -Recurse | ForEach-Object { $_.FullName })
$libraryClasspath = Join-Path $libraryDirectory '*'
& javac --release 17 -encoding UTF-8 -cp $libraryClasspath -d $outputDirectory @sources
if ($LASTEXITCODE -ne 0) {
    throw 'Java compilation failed.'
}
Write-Host 'Java compilation complete.'
if ($BuildOnly) {
    return
}

$classpath = $outputDirectory + [IO.Path]::PathSeparator + $libraryClasspath
& java -cp $classpath vn.edu.iot.MqttAssignment --mssv $Mssv --interval $IntervalSeconds --broker $Broker
if ($LASTEXITCODE -ne 0) {
    throw "Java program exited with code $LASTEXITCODE."
}
