$env:Path = 'C:\Program Files\7-Zip;C:\ProgramFiles\mpv;' + $env:Path

$test_run = $false
$s = If ($test_run) {"2"} Else {"1"}

ls -Filter '1/*' | ForEach-Object {
    $a = split-path $_ -LeafBase
    if ($test_run){
        ffmpeg -hide_banner -loglevel warning -y -hwaccel d3d11va -ss "00:11:05" -t "00:00:10" -i "$_" -c copy "2/$a.mkv"
    }
    cmd /c "vspipe -c y4m --arg ""in=$s/$a.mkv"" --arg is_img=False upscale_and_rife_2.vpy - | ffmpeg -hide_banner -y -i - -i ""$s/$a.mkv"" -map 0:v -map 1 -map -1:v -c:a copy -c:s copy -c:v hevc_nvenc -preset p7 -pix_fmt p010le -profile:v main10 -b:v 0K -cq 26 ""./3/$a.mkv"""
}

Read-Host -Prompt "Press any key to continue"