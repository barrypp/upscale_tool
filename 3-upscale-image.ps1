$env:Path = 'C:\Program Files\7-Zip;C:\ProgramFiles\mpv;' + $env:Path
Import-Module ./5-plot.psm1
#7z l *.cbz > 1.txt
#ls *.cbz | % { $a = -split $(7z l $_.FullName | select -last 1); "{0,5:F}MB/f {1}" -f ($a[2]/$a[4]/1Mb),($_.Name) } | sort -Desc
#ls 1/*.cbz | ForEach-Object { 7z x $_.FullName -o"2/tmp"; 7z a -mx0 -tzip "3/$($_.Name)" "$((ls ./2/tmp/*)[0])/*";  rm -R -Force ./2/tmp }
$no_odd_height = $false

$data = @{}
ls -Filter '1/*.cbz' | ForEach-Object {
    7z x $_.FullName -o"2/tmp1"
    mkdir -Force 2/tmp2,2/tmp3,2/tmp4

    #
    mv 2/tmp1/*.mkv 2/tmp4
    mv 2/tmp1/*.png,2/tmp1/*.jpg,2/tmp1/*.bmp,2/tmp1/*.webp,2/tmp1/*.jxl 2/tmp2
    
    # gif
    ls -Filter '2/tmp1/*.gif' | ForEach-Object {
        $a = split-path $_ -LeafBase
        ffmpeg -v warning -stats -y -i "$_" -c:v hevc_nvenc -preset p7 -tune lossless -pix_fmt p010le -profile:v main10 -b:v 0K "./2/tmp1/$a.mkv"
        cmd /c "vspipe -c y4m --arg in=./2/tmp1/$a.mkv --arg is_img=False --arg model=301 upscale_and_rife_2.vpy - | ffmpeg -v warning -stats -y -i - -c:v hevc_nvenc -preset p7 -pix_fmt p010le -profile:v main10 -b:v 0K -cq 26 ./2/tmp4/$a.mkv"
    }

    #
    magick identify 2/tmp2/* | ConvertFrom-Csv -Delimiter " " -Header a,b,c,d,e,f | foreach {
        $a = $_.c -split "x"
        $b = [int]$a[1]
        if ($b -ge 2160){
            mv $_.a 2/tmp3
        }
        else{
            if (($b % 2) -ge 1 -and $no_odd_height){
                magick $_.a -chop 0x1 $_.a
            }
            $_.a | Out-File -FilePath 2/tmp.$($_.c)_$($_.f).txt -Append
        }
    }

    # upscale
    ls -Filter '2/tmp.*.txt' | ForEach-Object {
        vspipe -p --arg "in=2/$($_.Name)" --arg is_img=True --arg model=301 upscale_and_rife_2.vpy .
        $b = 0
        Get-Content 2/$($_.Name) | % {
            $c = split-path $_ -LeafBase
            mv 2/tmp3/tmp_$b.bmp 2/tmp3/$c.bmp
            $b = $b + 1
        }
    }

    # format
    $data[$_.Name] = @{frame=[System.Collections.ArrayList]::new();vmaf=[System.Collections.ArrayList]::new()}
    $frame_sync = [System.Collections.ArrayList]::Synchronized($data[$_.Name].frame)
    $vmaf_sync = [System.Collections.ArrayList]::Synchronized($data[$_.Name].vmaf)
    ls -Filter '2/tmp3/*' | foreach-Object {
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
            $frame_sync = $using:frame_sync
            $vmaf_sync = $using:vmaf_sync
            $i = $using:_
            magick mogrify -path ./2/tmp4 -quality 90 -format jxl -define jxl:effort=7 $i
            $a = Split-Path $i -LeafBase
            ffmpeg -v warning -i "./2/tmp4/$a.jxl" -i $i -lavfi "[0:v]setpts=PTS-STARTPTS[dis];[1:v]setpts=PTS-STARTPTS[ref];[dis][ref]libvmaf=n_threads=8:model=path='model/vmaf_4k_v0.6.1.json':log_fmt=csv:log_path=2/tmp.$a.vmaf.csv" -f null -
            $c = Import-Csv "2/tmp.$a.vmaf.csv"
            "$($i.name) to jxl {0:F}kB {1:F}kB $($c.vmaf)" -f ($i.length/1kB),((ls "./2/tmp4/$a.jxl").length/1kB)
            $frame_sync.add($c.Frame) | out-null # thread safe ?
            $vmaf_sync.add($c.vmaf) | out-null
        } -ThrottleLimit 24 | out-null
    }
    get-job | Wait-Job | Receive-Job
    get-job | remove-job
    
    "2/tmp3 {0:F}MB" -f ((ls 2/tmp3 | measure length -sum).Sum/1MB)
    "2/tmp4 {0:F}MB" -f ((ls 2/tmp4 | measure length -sum).Sum/1MB)    
    
   7z a -mx0 -tzip "3/$($_.Name)" ./2/tmp4/*
   rm -R -Force 2/tmp*
}

plot_vmaf($data)
#Read-Host -Prompt "Press any key to continue"