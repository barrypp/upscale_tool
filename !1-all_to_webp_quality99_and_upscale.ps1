$env:Path = 'C:\Program Files\7-Zip;C:\ProgramFiles\mpv;' + $env:Path


ls -Filter '1/*.cbz' | ForEach-Object {
    7z x $_.FullName -o"2/tmp"
    mkdir -Force 3/tmp

    ls -Filter '2/tmp/*.jpg' | ForEach-Object -Parallel {
        $d = $_.Name
        $e = Split-Path $d -LeafBase
        cmd.exe /c "vspipe -c y4m --arg ""in=2/tmp/$d"" upscale_and_rife_2.vpy - | ffmpeg -loglevel warning -y -i - -quality 99 -compression_level 6 ""3/tmp/$e.webp"""
    } -ThrottleLimit 6
    
    7z a -mx0 -tzip "3/"+$_.Name ./3/tmp/*

    rm -R -Force 2/tmp
    rm -R -Force 3/tmp
}

Read-Host -Prompt "Press any key to continue"