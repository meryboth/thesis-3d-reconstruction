# ============================================================
# AUDITORIA COLMAP - DATASET HIBRIDO DJI + INSTA360
# ============================================================

$HybridDataset = "C:\nerfstudio_work\panteon-chacarita\panteon-asociacion-catalana\dataset-clean"

$SearchRoots = @(
    "C:\nerfstudio_work\panteon-chacarita\panteon-asociacion-catalana",
    "C:\nerfstudio_work\thesis"
)

$OutDir = "C:\nerfstudio_work\thesis\00-auditoria\colmap-dji-insta360"

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$InventoryFile = Join-Path $OutDir "01_candidate-files.csv"
$FailureFile   = Join-Path $OutDir "02_failure-events.csv"
$RawReport     = Join-Path $OutDir "03_failure-context.txt"
$SummaryFile   = Join-Path $OutDir "04_colmap-failure-summary.txt"
$JsonFile      = Join-Path $OutDir "05_colmap-failure-metrics.json"
$MetricsCsv    = Join-Path $OutDir "06_extracted-colmap-metrics.csv"
$HybridOnlyCsv = Join-Path $OutDir "07_hybrid-dataset-only.csv"
$HybridSummary = Join-Path $OutDir "08_hybrid-experiment-summary.txt"


function Read-TextFileSafe {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    try {
        Get-Content -LiteralPath $Path -Raw -ErrorAction Stop
    }
    catch {
        $null
    }
}


Write-Host ""
Write-Host "============================================================"
Write-Host "AUDITORIA COLMAP - DATASET HIBRIDO DJI + INSTA360"
Write-Host "============================================================"
Write-Host ""
Write-Host "Dataset:"
Write-Host $HybridDataset
Write-Host ""


# ============================================================
# 1. BUSCAR ARCHIVOS CANDIDATOS
# ============================================================

$allFiles = @()

foreach ($root in $SearchRoots) {

    if (-not (Test-Path $root)) {
        Write-Host "[WARN] No existe: $root"
        continue
    }

    $found = Get-ChildItem `
        -LiteralPath $root `
        -Recurse `
        -File `
        -ErrorAction SilentlyContinue |
    Where-Object {

        $ext = $_.Extension.ToLower()
        $path = $_.FullName.ToLower()

        $validExtension = $ext -in @(
            ".log",
            ".txt",
            ".out",
            ".err"
        )

        $validTopic = (
            $path -match "colmap" -or
            $path -match "sfm" -or
            $path -match "mapper" -or
            $path -match "nerfstudio" -or
            $path -match "reconstruction"
        )

        $validExtension -and $validTopic
    }

    $allFiles += $found
}

$allFiles = $allFiles | Sort-Object FullName -Unique

Write-Host "Archivos base encontrados: $($allFiles.Count)"


# ============================================================
# 2. RELEVANCIA DEL DATASET HIBRIDO
# ============================================================

$candidates = @()
$hybridLower = $HybridDataset.ToLower()

foreach ($file in $allFiles) {

    $score = 0
    $signals = @()

    $pathLower = $file.FullName.ToLower()

    if ($pathLower -match "dataset-clean") {
        $score += 10
        $signals += "PATH_HYBRID_DATASET"
    }

    if ($pathLower -match "dji") {
        $score += 2
        $signals += "PATH_DJI"
    }

    if (
        $pathLower -match "insta360" -or
        $pathLower -match "insta"
    ) {
        $score += 2
        $signals += "PATH_INSTA360"
    }

    if (
        $pathLower -match "combined" -or
        $pathLower -match "mixed" -or
        $pathLower -match "merged" -or
        $pathLower -match "hybrid" -or
        $pathLower -match "fusion"
    ) {
        $score += 4
        $signals += "PATH_COMBINED"
    }

    $content = Read-TextFileSafe -Path $file.FullName

    if ($null -ne $content) {

        $lower = $content.ToLower()

        $hasHybrid = (
            $lower.Contains($hybridLower) -or
            $lower -match "dataset-clean"
        )

        $hasDji = $lower -match "dji"

        $hasInsta = (
            $lower -match "insta360" -or
            $lower -match "insta 360" -or
            $lower -match "insta"
        )

        if ($hasHybrid) {
            $score += 20
            $signals += "CONTENT_HYBRID_DATASET"
        }

        if ($hasDji) {
            $score += 2
            $signals += "CONTENT_DJI"
        }

        if ($hasInsta) {
            $score += 2
            $signals += "CONTENT_INSTA360"
        }

        if ($hasDji -and $hasInsta) {
            $score += 5
            $signals += "CONTENT_DJI+INSTA360"
        }
    }

    if ($score -gt 0) {

        $hybridConfirmed = (
            $signals -contains "CONTENT_HYBRID_DATASET" -or
            $signals -contains "PATH_HYBRID_DATASET"
        )

        $candidates += [PSCustomObject]@{
            FullName               = $file.FullName
            SizeMB                 = [math]::Round($file.Length / 1MB, 3)
            LastWriteTime          = $file.LastWriteTime
            RelevanceScore         = $score
            Signals                = ($signals -join ";")
            HybridDatasetConfirmed = $hybridConfirmed
        }
    }
}

$candidates = $candidates |
    Sort-Object `
        @{Expression = "RelevanceScore"; Descending = $true}, `
        @{Expression = "LastWriteTime"; Descending = $true}

$candidates |
    Export-Csv `
        -LiteralPath $InventoryFile `
        -NoTypeInformation `
        -Encoding UTF8

$hybridCandidates = @(
    $candidates |
    Where-Object {
        $_.HybridDatasetConfirmed -eq $true
    }
)

$hybridCandidates |
    Export-Csv `
        -LiteralPath $HybridOnlyCsv `
        -NoTypeInformation `
        -Encoding UTF8

Write-Host "Candidatos relevantes: $($candidates.Count)"
Write-Host "Logs confirmados dataset-clean: $($hybridCandidates.Count)"


# ============================================================
# 3. PATRONES DE FALLO
# ============================================================

$patterns = [ordered]@{
    OOM_KILLED               = "(out of memory|oomkilled|oom killed|cuda out of memory|killed)"
    NO_INITIAL_PAIR          = "(no good initial image pair|failed to find initial image pair|no initial pair)"
    NOT_ENOUGH_INLIERS       = "(not enough inliers|insufficient inliers|too few inliers)"
    REGISTRATION_FAILED      = "(failed to register|registration failed|could not register|register.*failed)"
    MAPPER_FAILED            = "(mapper.*failed|incremental mapper.*failed|reconstruction failed)"
    TRIANGULATION_FAILED     = "(triangulation.*failed|failed.*triangulat)"
    BUNDLE_ADJUSTMENT_FAILED = "(bundle adjustment.*failed|global bundle adjustment.*failed|solver failure)"
    MATCHING_FAILED          = "(feature matching.*failed|matching.*failed|two.view.geometry.*failed)"
    FEATURE_EXTRACTION_FAILED = "(feature extraction.*failed|extractor.*failed)"
    DATABASE_ERROR           = "(database.*error|sqlite.*error)"
    CUDA_ERROR               = "(cuda error|cuda.*failed|cublas|cusolver)"
    NO_IMAGES_REGISTERED     = "(0 registered images|registered images:\s*0)"
    LOW_REGISTERED_IMAGES    = "(registered images:\s*[1-9]\b)"
    DISCONNECTED_COMPONENT   = "(multiple components|disconnected component|new reconstruction|new model)"
    GENERIC_FATAL            = "(fatal|exception|traceback)"
    MANUAL_INTERRUPT         = "(keyboardinterrupt|interrupted)"
}


# ============================================================
# 4. EXTRAER EVENTOS DE FALLO
# ============================================================

$failureEvents = @()
$contextBuilder = New-Object System.Text.StringBuilder

foreach ($candidate in $hybridCandidates) {

    try {
        $lines = Get-Content `
            -LiteralPath $candidate.FullName `
            -ErrorAction Stop
    }
    catch {
        continue
    }

    for ($i = 0; $i -lt $lines.Count; $i++) {

        $line = $lines[$i]

        foreach ($entry in $patterns.GetEnumerator()) {

            if ($line -match $entry.Value) {

                $start = [math]::Max(0, $i - 6)
                $end = [math]::Min($lines.Count - 1, $i + 10)

                $context = $lines[$start..$end] -join "`n"

                $failureEvents += [PSCustomObject]@{
                    File           = $candidate.FullName
                    FailureType    = $entry.Key
                    LineNumber     = $i + 1
                    MatchedLine    = $line.Trim()
                    RelevanceScore = $candidate.RelevanceScore
                }

                [void]$contextBuilder.AppendLine(
                    "============================================================"
                )

                [void]$contextBuilder.AppendLine(
                    "FILE: $($candidate.FullName)"
                )

                [void]$contextBuilder.AppendLine(
                    "FAILURE TYPE: $($entry.Key)"
                )

                [void]$contextBuilder.AppendLine(
                    "LINE: $($i + 1)"
                )

                [void]$contextBuilder.AppendLine(
                    "============================================================"
                )

                [void]$contextBuilder.AppendLine($context)
                [void]$contextBuilder.AppendLine("")
            }
        }
    }
}

$failureEvents |
    Export-Csv `
        -LiteralPath $FailureFile `
        -NoTypeInformation `
        -Encoding UTF8

$contextBuilder.ToString() |
    Set-Content `
        -LiteralPath $RawReport `
        -Encoding UTF8


# ============================================================
# 5. EXTRAER METRICAS COLMAP
# ============================================================

$metricPatterns = [ordered]@{
    DatasetImages            = "(?:starting with|found|processing)\s+([0-9]+)\s+images"
    Cameras                  = "cameras:\s*([0-9]+)"
    Images                   = "(?<!registered )images:\s*([0-9]+)"
    RegisteredImages         = "registered images:\s*([0-9]+)"
    UnregisteredImages       = "unregistered images:\s*([0-9]+)"
    Points                   = "points:\s*([0-9]+)"
    Observations             = "observations:\s*([0-9]+)"
    MeanTrackLength          = "mean track length:\s*([0-9.]+)"
    MeanObservationsPerImage = "mean observations per image:\s*([0-9.]+)"
    MeanReprojectionError    = "mean reprojection error:\s*([0-9.]+)"
    Matches                  = "matches:\s*([0-9]+)"
    Keypoints                = "keypoints:\s*([0-9]+)"
    Descriptors              = "descriptors:\s*([0-9]+)"
    TwoViewGeometries        = "two.view.geometries:\s*([0-9]+)"
    Inliers                  = "inliers[^0-9]*([0-9]+)"
}

$extractedMetrics = @()

foreach ($candidate in $hybridCandidates) {

    $content = Read-TextFileSafe -Path $candidate.FullName

    if ($null -eq $content) {
        continue
    }

    foreach ($entry in $metricPatterns.GetEnumerator()) {

        $options = (
            [System.Text.RegularExpressions.RegexOptions]::IgnoreCase `
            -bor `
            [System.Text.RegularExpressions.RegexOptions]::Multiline
        )

        $matches = [regex]::Matches(
            $content,
            $entry.Value,
            $options
        )

        foreach ($match in $matches) {

            $extractedMetrics += [PSCustomObject]@{
                File           = $candidate.FullName
                Metric         = $entry.Key
                Value          = $match.Groups[1].Value
                RelevanceScore = $candidate.RelevanceScore
            }
        }
    }
}

$extractedMetrics |
    Export-Csv `
        -LiteralPath $MetricsCsv `
        -NoTypeInformation `
        -Encoding UTF8


# ============================================================
# 6. CALCULAR TASAS DE REGISTRO
# ============================================================

$derivedMetrics = @()

foreach (
    $fileGroup in (
        $extractedMetrics |
        Group-Object File
    )
) {

    $datasetImagesValue = (
        $fileGroup.Group |
        Where-Object {
            $_.Metric -eq "DatasetImages"
        } |
        Select-Object -Last 1
    )

    $imagesValue = (
        $fileGroup.Group |
        Where-Object {
            $_.Metric -eq "Images"
        } |
        Select-Object -Last 1
    )

    $registeredValue = (
        $fileGroup.Group |
        Where-Object {
            $_.Metric -eq "RegisteredImages"
        } |
        Select-Object -Last 1
    )

    $totalImages = $null

    if ($null -ne $datasetImagesValue) {
        $totalImages = [double]$datasetImagesValue.Value
    }

    if (
        $null -eq $totalImages -and
        $null -ne $imagesValue
    ) {
        $totalImages = [double]$imagesValue.Value
    }

    if (
        $null -ne $registeredValue -and
        $null -ne $totalImages -and
        $totalImages -gt 0
    ) {

        $registered = [double]$registeredValue.Value

        $rate = (
            $registered /
            $totalImages
        ) * 100

        $derivedMetrics += [PSCustomObject]@{
            File                    = $fileGroup.Name
            TotalImages             = [int]$totalImages
            RegisteredImages        = [int]$registered
            UnregisteredCalculated  = [int]($totalImages - $registered)
            RegistrationRatePercent = [math]::Round($rate, 4)
        }
    }
}


# ============================================================
# 7. RESUMEN
# ============================================================

$failureGroups = @(
    $failureEvents |
    Group-Object FailureType |
    Sort-Object Count -Descending
)

$summary = @()

$summary += "COLMAP DJI + INSTA360 FAILURE AUDIT"
$summary += ("=" * 72)
$summary += ""
$summary += "Dataset híbrido:"
$summary += $HybridDataset
$summary += ""
$summary += "Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
$summary += ""

$summary += "COUNTS"
$summary += "------"
$summary += "Base log files found: $($allFiles.Count)"
$summary += "Relevant candidate logs: $($candidates.Count)"
$summary += "Confirmed dataset-clean logs: $($hybridCandidates.Count)"
$summary += "Failure events detected: $($failureEvents.Count)"
$summary += "Extracted numeric metrics: $($extractedMetrics.Count)"
$summary += ""

$summary += "FAILURE TYPES"
$summary += "-------------"

if ($failureGroups.Count -eq 0) {
    $summary += "No explicit failure patterns detected."
}

foreach ($group in $failureGroups) {
    $summary += "$($group.Name): $($group.Count)"
}

$summary += ""
$summary += "DERIVED REGISTRATION METRICS"
$summary += "----------------------------"

if ($derivedMetrics.Count -eq 0) {
    $summary += "No registration rates could be derived."
}

foreach ($row in $derivedMetrics) {

    $summary += ""
    $summary += "File: $($row.File)"
    $summary += "Total images: $($row.TotalImages)"
    $summary += "Registered images: $($row.RegisteredImages)"
    $summary += "Unregistered calculated: $($row.UnregisteredCalculated)"
    $summary += "Registration rate: $($row.RegistrationRatePercent)%"
}

$summary += ""
$summary += "CONFIRMED HYBRID LOGS"
$summary += "---------------------"

foreach ($candidate in $hybridCandidates) {

    $summary += (
        "[Score {0}] [{1}] {2}" -f `
        $candidate.RelevanceScore, `
        $candidate.Signals, `
        $candidate.FullName
    )
}

$summary += ""
$summary += "IMPORTANT NOTE"
$summary += "--------------"
$summary += "Only logs linked to dataset-clean are treated as confirmed hybrid DJI + Insta360 evidence."
$summary += "Failure counts represent log occurrences, not necessarily independent experimental runs."
$summary += "Use 03_failure-context.txt to inspect the exact mechanism behind each detected failure."
$summary += "This audit does not modify, delete, move or rerun any reconstruction."

$summary |
    Set-Content `
        -LiteralPath $SummaryFile `
        -Encoding UTF8


# ============================================================
# 8. RESUMEN ESPECIFICO DEL EXPERIMENTO HIBRIDO
# ============================================================

$hybridText = @()

$hybridText += "HYBRID DJI + INSTA360 COLMAP EXPERIMENT"
$hybridText += ("=" * 72)
$hybridText += ""
$hybridText += "Dataset:"
$hybridText += $HybridDataset
$hybridText += ""
$hybridText += "Confirmed log files: $($hybridCandidates.Count)"
$hybridText += "Detected failure events: $($failureEvents.Count)"
$hybridText += ""

$hybridText += "FAILURE DISTRIBUTION"
$hybridText += "--------------------"

if ($failureGroups.Count -eq 0) {
    $hybridText += "No explicit failure patterns detected."
}

foreach ($group in $failureGroups) {
    $hybridText += "$($group.Name): $($group.Count)"
}

$hybridText += ""
$hybridText += "REGISTRATION RESULTS"
$hybridText += "--------------------"

if ($derivedMetrics.Count -eq 0) {
    $hybridText += "No registration metrics could be reconstructed."
}

foreach ($row in $derivedMetrics) {

    $hybridText += ""
    $hybridText += "Log: $($row.File)"
    $hybridText += "Images total: $($row.TotalImages)"
    $hybridText += "Images registered: $($row.RegisteredImages)"
    $hybridText += "Images not registered: $($row.UnregisteredCalculated)"
    $hybridText += "Registration rate: $($row.RegistrationRatePercent)%"
}

$hybridText += ""
$hybridText += "METHODOLOGICAL NOTE"
$hybridText += "-------------------"
$hybridText += "This document was reconstructed automatically from historical experiment logs."
$hybridText += "Metrics should be checked against 03_failure-context.txt before being cited as final thesis evidence."

$hybridText |
    Set-Content `
        -LiteralPath $HybridSummary `
        -Encoding UTF8


# ============================================================
# 9. JSON
# ============================================================

$failureTypeObject = [ordered]@{}

foreach ($group in $failureGroups) {
    $failureTypeObject[$group.Name] = $group.Count
}

$jsonObject = [ordered]@{
    generated_at   = Get-Date -Format "yyyy-MM-ddTHH:mm:ss"
    hybrid_dataset = $HybridDataset

    counts = [ordered]@{
        base_log_files          = $allFiles.Count
        relevant_candidate_logs = $candidates.Count
        confirmed_hybrid_logs   = $hybridCandidates.Count
        failure_events          = $failureEvents.Count
        extracted_metrics       = $extractedMetrics.Count
    }

    failure_types = $failureTypeObject

    hybrid_logs = @(
        $hybridCandidates |
        ForEach-Object {
            [ordered]@{
                file            = $_.FullName
                relevance_score = $_.RelevanceScore
                signals         = $_.Signals
                size_mb         = $_.SizeMB
                last_write_time = $_.LastWriteTime
            }
        }
    )

    failure_events = @(
        $failureEvents |
        ForEach-Object {
            [ordered]@{
                file         = $_.File
                failure_type = $_.FailureType
                line_number  = $_.LineNumber
                matched_line = $_.MatchedLine
            }
        }
    )

    extracted_metrics = @(
        $extractedMetrics |
        ForEach-Object {
            [ordered]@{
                file   = $_.File
                metric = $_.Metric
                value  = $_.Value
            }
        }
    )

    derived_registration_metrics = @(
        $derivedMetrics |
        ForEach-Object {
            [ordered]@{
                file                      = $_.File
                total_images              = $_.TotalImages
                registered_images         = $_.RegisteredImages
                unregistered_images       = $_.UnregisteredCalculated
                registration_rate_percent = $_.RegistrationRatePercent
            }
        }
    )
}

$jsonObject |
    ConvertTo-Json -Depth 12 |
    Set-Content `
        -LiteralPath $JsonFile `
        -Encoding UTF8


# ============================================================
# 10. RESULTADO
# ============================================================

Write-Host ""
Write-Host "============================================================"
Write-Host "AUDITORIA COMPLETADA"
Write-Host "============================================================"
Write-Host ""
Write-Host "Logs confirmados: $($hybridCandidates.Count)"
Write-Host "Eventos de fallo: $($failureEvents.Count)"
Write-Host "Metricas extraidas: $($extractedMetrics.Count)"
Write-Host ""
Write-Host "RESULTADOS:"
Write-Host $OutDir
Write-Host ""
Write-Host "01_candidate-files.csv"
Write-Host "02_failure-events.csv"
Write-Host "03_failure-context.txt"
Write-Host "04_colmap-failure-summary.txt"
Write-Host "05_colmap-failure-metrics.json"
Write-Host "06_extracted-colmap-metrics.csv"
Write-Host "07_hybrid-dataset-only.csv"
Write-Host "08_hybrid-experiment-summary.txt"
Write-Host ""