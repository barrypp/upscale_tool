$env:Path = 'C:\Program Files\7-Zip;C:\ProgramFiles\mpv;' + $env:Path

param (
    [Parameter(Mandatory = $true)]
    $format
)

$div = $format -eq "jxl" ? 3 : 24
mkdir -Force ../2/tmp00
$img = Get-ChildItem '../1/*/*'
$counter = [pscustomobject] @{ Value = 0 }
$img_g = $img | Group-Object -Property { $counter.Value++ % $div }

# format
$img_g | foreach-Object -Parallel {
    $to_jxl = $using:to_jxl
    if ($format -eq "jxl"){
        magick mogrify -monitor -path ../2/tmp00 -quality 90 -format jxl -define jxl:effort=7 ($_.Group | ForEach-Object {$_.fullName}) 2>&1 | Select-String "100% complete" | Write-Host
    }else{
        magick mogrify -monitor -path ../2/tmp00 -format png ($_.Group | ForEach-Object {$_.fullName}) 2>&1 | Select-String "100% complete" | Write-Host
    }
} -ThrottleLimit 24

#Read-Host -Prompt "Press any key to continue"  