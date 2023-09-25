$env:Path = 'C:\Program Files\7-Zip;C:\ProgramFiles\mpv;' + $env:Path


ls -Filter '1/*.cbz' | ForEach-Object {
    7z x $_.FullName -o"2/tmp"
    mkdir -Force 3/tmp

    #
    wsl parallel -j 8 -m identify ::: ./2/tmp/*.jpg | ConvertFrom-Csv -Delimiter " " -Header a,b,c | foreach {
        $_.a | Out-File -FilePath tmp.$($_.c).txt -Append
    }

    #
    ls -Filter 'tmp.*.txt' | ForEach-Object {
        #cmd /c "vspipe -c y4m --arg ""in=$($_.Name)"" upscale_and_rife_2.vpy - | ffmpeg -hide_banner -y -i - -c:v libwebp -quality 99 3/tmp/tmp_%d.webp"
        vspipe -p --arg "in=$($_.Name)" upscale_and_rife_2.vpy .
        $b = 0
        Get-Content $_.Name | % {
            $c = split-path $_ -LeafBase
            mv 3/tmp/tmp_$b.webp 3/tmp/$c.webp
            $b = $b + 1
        }
    }
    
    7z a -mx0 -tzip "3/$($_.Name)" ./3/tmp/*

    rm -R -Force 2/tmp
    rm -R -Force 3/tmp
    rm -Force tmp.*.txt
}

Read-Host -Prompt "Press any key to continue"