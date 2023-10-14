$env:Path = 'C:\Program Files\7-Zip;C:\ProgramFiles\mpv;' + $env:Path


ls -Filter '1/*.cbz' | ForEach-Object {
    7z x $_.FullName -o"2/tmp"
    mkdir -Force 3/tmp

    #
    ls -Filter './2/tmp/*.gif' | ForEach-Object {
        $a = split-path $_ -LeafBase
        ffmpeg -hide_banner -y -i "$_" -c:v hevc_nvenc -preset p7 -pix_fmt p010le -profile:v main10 -b:v 0K "./2/tmp/$a.mkv"
        cmd /c "vspipe -c y4m --arg in=./2/tmp/$a.mkv --arg is_img=False upscale_and_rife_2.vpy - | ffmpeg -hide_banner -y -i - -c:v hevc_nvenc -preset p7 -pix_fmt p010le -profile:v main10 -b:v 0K ./3/tmp/$a.mkv"
        rm $_
        rm ./2/tmp/$a.mkv*
    }

    #
    identify ./2/tmp/* | ConvertFrom-Csv -Delimiter " " -Header a,b,c | foreach {
        $_.a | Out-File -FilePath tmp.$($_.c).txt -Append
    }

    #
    ls -Filter 'tmp.*.txt' | ForEach-Object {
        vspipe -p --arg "in=$($_.Name)" --arg is_img=True upscale_and_rife_2.vpy .
        $b = 0
        Get-Content $_.Name | % {
            $c = split-path $_ -LeafBase
            mv 3/tmp/tmp_$b.bmp 3/tmp/$c.bmp
            $b = $b + 1
        }
    }
    
    7z a -mx0 -tzip "3/$($_.Name)" ./3/tmp/*

    rm -R -Force 2/tmp
    rm -R -Force 3/tmp
    rm -Force tmp.*.txt
}

Read-Host -Prompt "Press any key to continue"