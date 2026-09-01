# ============================================================
# COLMAP - DATASETS HIBRIDOS DJI + INSTA360
# TEMPLETE CENTRAL + PANTEON ASOCIACION CATALANA
# ============================================================
#
# Ejecuta:
# 1. Feature extraction
# 2. Exhaustive matching
# 3. Mapper
# 4. Model analyzer para TODOS los componentes sparse
#
# Cada ejecución se guarda en una carpeta run-YYYYMMDD-HHMMSS.
#
# NO sobrescribe experimentos anteriores.
# ============================================================

$ErrorActionPreference = "Stop"

$DockerImage = "ghcr.io/nerfstudio-project/nerfstudio:latest"

$RunTimestamp = Get-Date -Format "yyyyMMdd-HHmmss"


$Experiments = @(
    @{
        CaseName = "02-templete-central"

        Dataset = "C:\nerfstudio_work\panteon-chacarita\templete-central\dataset-clean"

        BaseOutput = "C:\nerfstudio_work\thesis\02-templete-central\01-experimentos\hybrid-dji-insta360-colmap"
    },

    @{
        CaseName = "03-panteon-asociacion-espanola"

        Dataset = "C:\nerfstudio_work\panteon-chacarita\panteon-asociacion-catalana\dataset-clean"

        BaseOutput = "C:\nerfstudio_work\thesis\03-panteon-asociacion-espanola\01-experimentos\hybrid-dji-insta360-colmap"
    }
)


function Run-HybridColmapExperiment {

    param(
        [string]$CaseName,
        [string]$Dataset,
        [string]$BaseOutput
    )


    # ========================================================
    # PATHS
    # ========================================================

    $Output = Join-Path $BaseOutput "run-$RunTimestamp"

    $ColmapDir = Join-Path $Output "colmap"
    $SparseDir = Join-Path $ColmapDir "sparse"

    $LogsDir = Join-Path $Output "logs"
    $MetricsDir = Join-Path $Output "metrics"

    $DatabasePath = Join-Path $ColmapDir "database.db"


    Write-Host ""
    Write-Host "============================================================"
    Write-Host "CASO: $CaseName"
    Write-Host "============================================================"
    Write-Host ""
    Write-Host "Dataset:"
    Write-Host "  $Dataset"
    Write-Host ""
    Write-Host "Output:"
    Write-Host "  $Output"
    Write-Host ""


    # ========================================================
    # VALIDAR DATASET
    # ========================================================

    if (-not (Test-Path $Dataset)) {

        Write-Host "[ERROR] Dataset inexistente:"
        Write-Host $Dataset

        return
    }


    # ========================================================
    # CREAR CARPETAS
    # ========================================================

    New-Item -ItemType Directory -Force -Path $Output | Out-Null
    New-Item -ItemType Directory -Force -Path $ColmapDir | Out-Null
    New-Item -ItemType Directory -Force -Path $SparseDir | Out-Null
    New-Item -ItemType Directory -Force -Path $LogsDir | Out-Null
    New-Item -ItemType Directory -Force -Path $MetricsDir | Out-Null


    # ========================================================
    # INVENTARIO DEL DATASET
    # ========================================================

    $images = @(
        Get-ChildItem `
            -LiteralPath $Dataset `
            -File `
            -ErrorAction SilentlyContinue |
        Where-Object {
            $_.Extension.ToLower() -in @(
                ".jpg",
                ".jpeg",
                ".png",
                ".tif",
                ".tiff"
            )
        }
    )


    $ImageCount = $images.Count


    $inventory = foreach ($image in $images) {

        [PSCustomObject]@{
            FileName      = $image.Name
            Extension     = $image.Extension
            SizeBytes     = $image.Length
            SizeMB        = [math]::Round($image.Length / 1MB, 4)
            LastWriteTime = $image.LastWriteTime
            FullPath      = $image.FullName
        }
    }


    $inventory |
        Export-Csv `
            -LiteralPath (Join-Path $Output "dataset-inventory.csv") `
            -NoTypeInformation `
            -Encoding UTF8


    Write-Host "Imagenes detectadas: $ImageCount"


    # ========================================================
    # RUN INFO
    # ========================================================

    $RunInfo = @(
        "HYBRID DJI + INSTA360 COLMAP EXPERIMENT"
        ("=" * 72)
        ""
        "Case: $CaseName"
        "Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
        ""
        "Dataset:"
        $Dataset
        ""
        "Dataset images: $ImageCount"
        ""
        "Output:"
        $Output
        ""
        "Docker image:"
        $DockerImage
        ""
        "Resources:"
        "CPU limit: 2"
        "RAM limit: 6 GB"
        "GPU: NVIDIA"
        ""
        "Pipeline:"
        "1. COLMAP feature_extractor"
        "2. COLMAP exhaustive_matcher"
        "3. COLMAP mapper"
        "4. COLMAP model_analyzer per sparse component"
        ""
        "Camera configuration:"
        "ImageReader.single_camera = 0"
        ""
        "Reason:"
        "The dataset contains captures produced by different physical cameras."
        ""
        "Experimental objective:"
        "Determine whether the hybrid DJI + Insta360 dataset produces a single connected SfM reconstruction or multiple disconnected sparse components."
    )


    $RunInfo |
        Set-Content `
            -LiteralPath (Join-Path $Output "run-info.txt") `
            -Encoding UTF8


    # ========================================================
    # 1. FEATURE EXTRACTION
    # ========================================================

    Write-Host ""
    Write-Host "------------------------------------------------------------"
    Write-Host "1/4 FEATURE EXTRACTION"
    Write-Host "------------------------------------------------------------"
    Write-Host ""


    $FeatureLog = Join-Path $LogsDir "01_feature_extractor.log"


    & docker run `
        --rm `
        --gpus all `
        --cpus=2 `
        --memory=6g `
        -v "${Dataset}:/dataset:ro" `
        -v "${Output}:/experiment" `
        $DockerImage `
        colmap feature_extractor `
        --database_path /experiment/colmap/database.db `
        --image_path /dataset `
        --ImageReader.single_camera 0 `
        --SiftExtraction.use_gpu 1 `
        2>&1 |
        Tee-Object -FilePath $FeatureLog


    $FeatureExit = $LASTEXITCODE


    Write-Host ""
    Write-Host "Feature extractor exit code: $FeatureExit"


    if ($FeatureExit -ne 0) {

        Write-Host ""
        Write-Host "[ERROR] Feature extraction no termino correctamente."
        Write-Host "Log:"
        Write-Host $FeatureLog

        return
    }


    # ========================================================
    # 2. EXHAUSTIVE MATCHING
    # ========================================================

    Write-Host ""
    Write-Host "------------------------------------------------------------"
    Write-Host "2/4 EXHAUSTIVE MATCHING"
    Write-Host "------------------------------------------------------------"
    Write-Host ""


    $MatcherLog = Join-Path $LogsDir "02_exhaustive_matcher.log"


    & docker run `
        --rm `
        --gpus all `
        --cpus=2 `
        --memory=6g `
        -v "${Output}:/experiment" `
        $DockerImage `
        colmap exhaustive_matcher `
        --database_path /experiment/colmap/database.db `
        --SiftMatching.use_gpu 1 `
        2>&1 |
        Tee-Object -FilePath $MatcherLog


    $MatcherExit = $LASTEXITCODE


    Write-Host ""
    Write-Host "Exhaustive matcher exit code: $MatcherExit"


    if ($MatcherExit -ne 0) {

        Write-Host ""
        Write-Host "[ERROR] Exhaustive matching no termino correctamente."
        Write-Host ""
        Write-Host "Database preservada:"
        Write-Host $DatabasePath
        Write-Host ""
        Write-Host "Log:"
        Write-Host $MatcherLog

        return
    }


    # ========================================================
    # 3. MAPPER
    # ========================================================

    Write-Host ""
    Write-Host "------------------------------------------------------------"
    Write-Host "3/4 COLMAP MAPPER"
    Write-Host "------------------------------------------------------------"
    Write-Host ""


    $MapperLog = Join-Path $LogsDir "03_mapper.log"


    & docker run `
        --rm `
        --cpus=2 `
        --memory=6g `
        -v "${Dataset}:/dataset:ro" `
        -v "${Output}:/experiment" `
        $DockerImage `
        colmap mapper `
        --database_path /experiment/colmap/database.db `
        --image_path /dataset `
        --output_path /experiment/colmap/sparse `
        2>&1 |
        Tee-Object -FilePath $MapperLog


    $MapperExit = $LASTEXITCODE


    Write-Host ""
    Write-Host "Mapper exit code: $MapperExit"


    # ========================================================
    # 4. DETECTAR TODOS LOS COMPONENTES
    # ========================================================

    $models = @(
        Get-ChildItem `
            -LiteralPath $SparseDir `
            -Directory `
            -ErrorAction SilentlyContinue |
        Where-Object {
            $_.Name -match '^\d+$'
        } |
        Sort-Object {
            [int]$_.Name
        }
    )


    Write-Host ""
    Write-Host "------------------------------------------------------------"
    Write-Host "COMPONENTES SPARSE GENERADOS"
    Write-Host "------------------------------------------------------------"
    Write-Host ""

    Write-Host "Cantidad:"
    Write-Host "  $($models.Count)"
    Write-Host ""


    foreach ($model in $models) {
        Write-Host "  sparse\$($model.Name)"
    }


    # ========================================================
    # INVENTARIO FISICO
    # ========================================================

    $componentInventory = foreach ($model in $models) {

        $cameraBin = Join-Path $model.FullName "cameras.bin"
        $imagesBin = Join-Path $model.FullName "images.bin"
        $pointsBin = Join-Path $model.FullName "points3D.bin"


        [PSCustomObject]@{
            Component         = $model.Name
            FullPath          = $model.FullName
            CamerasBinExists  = Test-Path $cameraBin
            ImagesBinExists   = Test-Path $imagesBin
            Points3DBinExists = Test-Path $pointsBin
            CamerasBinBytes   = $(if (Test-Path $cameraBin) { (Get-Item $cameraBin).Length })
            ImagesBinBytes    = $(if (Test-Path $imagesBin) { (Get-Item $imagesBin).Length })
            Points3DBinBytes  = $(if (Test-Path $pointsBin) { (Get-Item $pointsBin).Length })
        }
    }


    $componentInventory |
        Export-Csv `
            -LiteralPath (Join-Path $MetricsDir "01_sparse-component-inventory.csv") `
            -NoTypeInformation `
            -Encoding UTF8


    # ========================================================
    # MODEL ANALYZER PARA CADA COMPONENTE
    # ========================================================

    Write-Host ""
    Write-Host "------------------------------------------------------------"
    Write-Host "4/4 MODEL ANALYZER"
    Write-Host "------------------------------------------------------------"
    Write-Host ""


    $analysisRows = @()


    foreach ($model in $models) {

        Write-Host "Analizando componente $($model.Name)..."


        $AnalyzerLog = Join-Path `
            $LogsDir `
            "04_model_analyzer_component_$($model.Name).log"


        $analyzerOutput = & docker run `
            --rm `
            --cpus=2 `
            --memory=6g `
            -v "${Output}:/experiment" `
            $DockerImage `
            colmap model_analyzer `
            --path "/experiment/colmap/sparse/$($model.Name)" `
            2>&1


        $analyzerOutput |
            Tee-Object -FilePath $AnalyzerLog


        $text = $analyzerOutput -join "`n"


        function Get-ColmapMetric {

            param(
                [string]$Text,
                [string]$Pattern
            )


            $match = [regex]::Match(
                $Text,
                $Pattern,
                [System.Text.RegularExpressions.RegexOptions]::IgnoreCase
            )


            if ($match.Success) {
                return $match.Groups[1].Value
            }


            return $null
        }


        $Cameras = Get-ColmapMetric `
            -Text $text `
            -Pattern "Cameras:\s*([0-9]+)"


        $Images = Get-ColmapMetric `
            -Text $text `
            -Pattern "(?:Registered images|Images):\s*([0-9]+)"


        $Points = Get-ColmapMetric `
            -Text $text `
            -Pattern "Points:\s*([0-9]+)"


        $Observations = Get-ColmapMetric `
            -Text $text `
            -Pattern "Observations:\s*([0-9]+)"


        $TrackLength = Get-ColmapMetric `
            -Text $text `
            -Pattern "Mean track length:\s*([0-9.]+)"


        $ObsPerImage = Get-ColmapMetric `
            -Text $text `
            -Pattern "Mean observations per image:\s*([0-9.]+)"


        $Reprojection = Get-ColmapMetric `
            -Text $text `
            -Pattern "Mean reprojection error:\s*([0-9.]+)"


        $analysisRows += [PSCustomObject]@{
            Component                    = $model.Name
            Cameras                      = $Cameras
            RegisteredImages             = $Images
            Points3D                     = $Points
            Observations                 = $Observations
            MeanTrackLength              = $TrackLength
            MeanObservationsPerImage     = $ObsPerImage
            MeanReprojectionErrorPixels  = $Reprojection
            ModelPath                    = $model.FullName
        }
    }


    $analysisRows |
        Export-Csv `
            -LiteralPath (Join-Path $MetricsDir "02_component-model-analyzer.csv") `
            -NoTypeInformation `
            -Encoding UTF8


    # ========================================================
    # METRICAS DERIVADAS DE FRAGMENTACION
    # ========================================================

    $registeredCounts = @(
        $analysisRows |
        ForEach-Object {

            if (
                $null -ne $_.RegisteredImages -and
                $_.RegisteredImages -ne ""
            ) {
                [int]$_.RegisteredImages
            }
        }
    )


    $TotalRegistered = 0

    if ($registeredCounts.Count -gt 0) {

        $TotalRegistered = (
            $registeredCounts |
            Measure-Object -Sum
        ).Sum
    }


    $LargestComponent = 0

    if ($registeredCounts.Count -gt 0) {

        $LargestComponent = (
            $registeredCounts |
            Measure-Object -Maximum
        ).Maximum
    }


    $OutsideLargest = $TotalRegistered - $LargestComponent


    $LargestShare = 0

    if ($TotalRegistered -gt 0) {

        $LargestShare = (
            $LargestComponent /
            $TotalRegistered
        ) * 100
    }


    $LargestDatasetCoverage = 0

    if ($ImageCount -gt 0) {

        $LargestDatasetCoverage = (
            $LargestComponent /
            $ImageCount
        ) * 100
    }


    # ========================================================
    # RESUMEN FINAL
    # ========================================================

    $SummaryPath = Join-Path `
        $MetricsDir `
        "00_experiment-summary.txt"


    $summary = @(
        "HYBRID DJI + INSTA360 COLMAP EXPERIMENT"
        ("=" * 72)
        ""
        "Case: $CaseName"
        ""
        "Dataset:"
        $Dataset
        ""
        "Dataset images: $ImageCount"
        ""
        "Feature extractor exit code: $FeatureExit"
        "Exhaustive matcher exit code: $MatcherExit"
        "Mapper exit code: $MapperExit"
        ""
        "Sparse components generated: $($models.Count)"
        ""
        "Registered images across components: $TotalRegistered"
        "Largest component images: $LargestComponent"
        "Images outside largest component: $OutsideLargest"
        "Largest component share of registered reconstruction: $([math]::Round($LargestShare, 4))%"
        "Largest component coverage of complete dataset: $([math]::Round($LargestDatasetCoverage, 4))%"
        ""
        "Fragmented reconstruction: $($models.Count -gt 1)"
        ""
        "COMPONENTS"
        "----------"
    )


    foreach ($row in $analysisRows) {

        $summary += ""
        $summary += "Component: $($row.Component)"
        $summary += "Registered images: $($row.RegisteredImages)"
        $summary += "Cameras: $($row.Cameras)"
        $summary += "Points 3D: $($row.Points3D)"
        $summary += "Observations: $($row.Observations)"
        $summary += "Mean track length: $($row.MeanTrackLength)"
        $summary += "Mean observations/image: $($row.MeanObservationsPerImage)"
        $summary += "Mean reprojection error: $($row.MeanReprojectionErrorPixels) px"
    }


    $summary += ""
    $summary += "METHODOLOGICAL INTERPRETATION"
    $summary += "-----------------------------"
    $summary += "Multiple sparse components indicate a fragmented SfM reconstruction."
    $summary += "This is not equivalent to a software crash: COLMAP may complete successfully while producing disconnected models."
    $summary += "All sparse components are preserved for subsequent experimental analysis."


    $summary |
        Set-Content `
            -LiteralPath $SummaryPath `
            -Encoding UTF8


    Write-Host ""
    Write-Host "============================================================"
    Write-Host "CASO COMPLETADO"
    Write-Host "============================================================"
    Write-Host ""
    Write-Host "Componentes: $($models.Count)"
    Write-Host "Total registrado: $TotalRegistered"
    Write-Host "Componente principal: $LargestComponent"
    Write-Host "Fuera del componente principal: $OutsideLargest"
    Write-Host ""
    Write-Host "Guardado permanentemente en:"
    Write-Host $Output
    Write-Host ""
}


# ============================================================
# EJECUTAR SECUENCIALMENTE
# ============================================================

foreach ($experiment in $Experiments) {

    Run-HybridColmapExperiment `
        -CaseName $experiment.CaseName `
        -Dataset $experiment.Dataset `
        -BaseOutput $experiment.BaseOutput
}


Write-Host ""
Write-Host "============================================================"
Write-Host "SCRIPT FINALIZADO"
Write-Host "============================================================"
Write-Host ""