$root = "C:\nerfstudio_work\thesis"

$cases = @(
    @{
        Name = "Paraguas Vicente Lopez"
        Path = "$root\01-paraguas-vicentelopez\02-resultados-finales\colmap-fotogrametria-densa"
    },
    @{
        Name = "Templete Central"
        Path = "$root\02-templete-central\02-resultados-finales\dji\colmap-fotogrametria"
    },
    @{
        Name = "Panteon Asociacion Catalana"
        Path = "$root\03-panteon-asociacion-espanola\02-resultados-finales\dji\colmap-fotogrametria"
    }
)

foreach ($case in $cases) {

    Write-Host ""
    Write-Host "============================================================"
    Write-Host $case.Name
    Write-Host "============================================================"

    $log = Join-Path $case.Path "dense-cloud-metrics.log"
    $json = Join-Path $case.Path "dense-cloud-metadata.json"

    if (Test-Path $log) {
        Write-Host "[OK] metrics.log"
        Get-Item $log |
            Select-Object FullName, Length, LastWriteTime
    }

    if (-not (Test-Path $log)) {
        Write-Host "[MISSING] dense-cloud-metrics.log"
    }

    if (Test-Path $json) {
        Write-Host "[OK] metadata.json"
        Get-Item $json |
            Select-Object FullName, Length, LastWriteTime
    }

    if (-not (Test-Path $json)) {
        Write-Host "[MISSING] dense-cloud-metadata.json"
    }
}