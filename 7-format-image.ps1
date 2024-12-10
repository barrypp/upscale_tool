$env:Path = 'C:\Program Files\7-Zip;C:\ProgramFiles\mpv;' + $env:Path

mkdir -Force 2/tmp00

# format
ls '1/*/*' | foreach-Object {
    #
    do {
        Start-Sleep -Seconds 0.1
        $FreePhysicalMemory = (Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory
        $FreeCPU = 100 - ((Get-CimInstance Win32_PerfFormattedData_PerfOS_Processor).PercentProcessorTime | Measure-Object -Average).Average
    } while ($FreePhysicalMemory -lt 4*1024*1024 -or $FreeCPU -lt 10)
    #
    get-job | Receive-Job
    #
    Start-ThreadJob -ScriptBlock {
        $i = $using:_
        if ($true){
            magick mogrify -path ./2/tmp00 -quality 90 -format jxl -define jxl:effort=7 $i
        }else{
            magick mogrify -path ./2/tmp00 -format png $i
        }
        "$($i.name)"
    } -ThrottleLimit 24 | out-null
}
get-job | Wait-Job | Receive-Job
get-job | remove-job

Read-Host -Prompt "Press any key to continue"