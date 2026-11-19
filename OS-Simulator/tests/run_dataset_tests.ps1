param(
    [ValidateSet("small", "large", "all")]
    [string]$Dataset = "all",
    [string]$Module
)

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$simulatorRoot = Split-Path -Parent $scriptRoot
Push-Location $simulatorRoot
try {
    $arguments = @(".\tests\run_dataset_tests.py", "--dataset", $Dataset)
    if ($Module) {
        $arguments += @("--module", $Module)
    }
    python @arguments
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}
