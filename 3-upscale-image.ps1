$env:Path = 'C:\Program Files\7-Zip;C:\ProgramFiles\mpv;' + $env:Path
#7z l *.cbz > 1.txt
#Get-ChildItem *.cbz | % { $a = -split $(7z l $_.FullName | select -last 1); "{0,5:F}MB/f {1}" -f ($a[2]/$a[4]/1Mb),($_.Name) } | sort -Desc
#Get-ChildItem 1/*.cbz | ForEach-Object { 7z x $_.FullName -o"tmp"; 7z a -mx0 -tzip "3/$($_.Name)" "$((Get-ChildItem ./tmp/*)[0])/*";  rm -R -Force ./tmp }
$no_odd_height = $false

Get-ChildItem '../1/*.cbz' | ForEach-Object {
    7z x $_.FullName -o"tmp1"
    mkdir -Force tmp2,tmp3,tmp4

    #
    Move-Item tmp1/*.mkv tmp4
    Move-Item tmp1/*.png,tmp1/*.jpg,tmp1/*.bmp,tmp1/*.webp,tmp1/*.jxl tmp2
    
    # gif
    Get-ChildItem 'tmp1/*.gif' | ForEach-Object {
        $a = split-path $_ -LeafBase
        ffmpeg -v warning -stats -y -i "$_" -c:v hevc_nvenc -preset p7 -tune lossless -pix_fmt p010le -profile:v main10 -b:v 0K "./tmp1/$a.mkv"
        cmd /c "vspipe -c y4m --arg in=./tmp1/$a.mkv --arg is_img=False --arg model=301 upscale_and_rife_2.vpy - | ffmpeg -v warning -stats -y -i - -c:v hevc_nvenc -preset p7 -pix_fmt p010le -profile:v main10 -b:v 0K -cq 26 ./tmp4/$a.mkv"
    }

    #
    magick identify tmp2/* | ConvertFrom-Csv -Delimiter " " -Header a,b,c,d,e,f | ForEach-Object {
        $a = $_.c -split "x"
        $b = [int]$a[1]
        if ($b -ge 2160){
            Move-Item $_.a tmp3
        }
        else{
            if (($b % 2) -ge 1 -and $no_odd_height){
                magick $_.a -chop 0x1 $_.a
            }
            $_.a | Out-File -FilePath tmp.$($_.c)_$($_.f).txt -Append
        }
    }

    # upscale
    Get-ChildItem 'tmp.*.txt' | ForEach-Object {
        vspipe -p --arg "in=./$($_.Name)" --arg is_img=True --arg model=301 upscale_and_rife_2.vpy .
        $b = 0
        Get-Content ./$($_.Name) | % {
            $c = split-path $_ -LeafBase
            Move-Item tmp3/tmp_$b.bmp tmp3/$c.bmp
            $b = $b + 1
        }
    }

    # format
    $img = Get-ChildItem 'tmp3/*'
    $counter = [pscustomobject] @{ Value = 0 }
    $img_g = $img | Group-Object -Property { $counter.Value++ % 3 }
    #
    $img_g | foreach-Object -Parallel {
        magick mogrify -monitor -path tmp4 -quality 90 -format jxl -define jxl:effort=7 ($_.Group | ForEach-Object {$_.fullName}) 2>&1 | Select-String "100% complete" | Write-Host
    } -ThrottleLimit 24
    
    "tmp3 {0:F}MB" -f ((Get-ChildItem tmp3 | Measure-Object length -sum).Sum/1MB)
    "tmp4 {0:F}MB" -f ((Get-ChildItem tmp4 | Measure-Object length -sum).Sum/1MB)    
    
   7z a -mx0 -tzip "../3/$($_.Name)" tmp4/*
   Remove-Item -R -Force tmp*
}

#Read-Host -Prompt "Press any key to continue"