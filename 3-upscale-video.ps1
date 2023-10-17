$env:Path = 'C:\Program Files\7-Zip;C:\ProgramFiles\mpv;' + $env:Path
Import-Module ./5-plot.psm1

#ffmpeg -hide_banner -h encoder=hevc_nvenc
#ffmpeg -hide_banner -filters -encoders -hwaccels
#ffprobe -v error -select_streams v:0 -show_entries stream -i 1.mkv
#ls *.mkv | % {$bit_rate = ffprobe -v error -select_streams v:0 -show_entries format=bit_rate -of csv=s=x:p=0 -i $_; "{0,5:F}Mbps {1}" -f ($bit_rate/1Mb),($_.Name) } | sort -Desc
#ls 1/*.mkv | % { $a = split-path $_ -Leaf; vspipe -p -c y4m --arg "in=1/$a" --arg is_img=False upscale_and_rife_2.vpy --info } 
#ls 1/*.mkv | % { $a = split-path $_ -Leaf; vspipe -p -c y4m --arg "in=1/$a" --arg is_img=False upscale_and_rife_2.vpy --graph full > 1.dot } 
#ls 1/*.mkv | % { $a = Split-Path $_ -LeafBase; ffmpeg -hide_banner -y -i "$_" -c:a copy -c:s copy -c:v hevc_nvenc -preset p7 -pix_fmt p010le -profile:v main10 -b:v 0K -cq 26 "3/$a.mkv" }
#ls -Filter '1/*' | % { $a = split-path $_ -LeafBase; cmd /c "vspipe -c y4m --arg ""in=$_"" --arg is_img=False upscale_and_rife_2.vpy - | ffmpeg -hide_banner -y -i - -i ""$_"" -map 0:v -map 1 -map -1:v -c:a copy -c:s copy -c:v hevc_nvenc -preset p7 -pix_fmt p010le -profile:v main10 -b:v 0K -cq 26 ""./3/$a.mkv""" }

$a = (ls 1/*)[0]
[float]$duration = ffprobe -v error -select_streams v:0 -show_entries format=duration -of csv=s=x:p=0 -i $a
[float]$height = ffprobe -v error -select_streams v:0 -show_entries stream=height -of csv=s=x:p=0 -i $a
ffmpeg -v warning -stats -y -hwaccel d3d11va -ss "00:00:00" -t "00:00:10" -i $a -ss ($duration/6) -t "00:00:10" -i $a -ss ($duration*2/6) -t "00:00:10" -i $a -ss ($duration*3/6) -t "00:00:10" -i $a -ss ($duration*4/6) -t "00:00:10" -i $a -ss ($duration*5/6) -t "00:00:10" -i $a -filter_complex '[0:v][1:v][2:v][3:v][4:v][5:v]concat=n=6:v=1:a=0[v]' -map '[v]' -c:v hevc_nvenc -preset p7 -tune lossless -pix_fmt p010le -profile:v main10 2/test.mkv
if (2160 -gt $height){
    cmd /c "vspipe -c y4m --arg in=2/test.mkv --arg is_img=False upscale_and_rife_2.vpy - | ffmpeg -v warning -stats -y -i - -map 0:v -c:v hevc_nvenc -preset p7 -tune lossless -pix_fmt p010le -profile:v main10 2/test2.mkv"
}
else{
    mv 2/test.mkv 2/test2.mkv
}
ffmpeg -v warning -stats -y -i 2/test2.mkv -c:v hevc_nvenc -preset p7 -pix_fmt p010le -profile:v main10 -b:v 0K -cq 26 3/p7_cq26.mkv
ffmpeg -v warning -stats -y -i 2/test2.mkv -c:v hevc_nvenc -preset p7 -pix_fmt p010le -profile:v main10 -b:v 0K -cq 28 3/p7_cq28.mkv
ffmpeg -v warning -stats -y -i 2/test2.mkv -c:v libx265 -crf 18 -preset slow 3/slow_crf18.mkv

$vmaf = @{}
ls 3/*.mkv | sort | ForEach-Object {
    $bit_rate = ffprobe -v error -select_streams v:0 -show_entries format=bit_rate -of csv=s=x:p=0 -i $_
    [int]$height = ffprobe -v error -select_streams v:0 -show_entries stream=height -of csv=s=x:p=0 -i $_
    $model = if ($height -gt 1620) {":model=path='model/vmaf_4k_v0.6.1.json'"} else {""}
    ffmpeg -v warning -stats -i $_ -i 2/test2.mkv -lavfi "[0:v]setpts=PTS-STARTPTS[dis];[1:v]setpts=PTS-STARTPTS[ref];[dis][ref]libvmaf=n_threads=8'$($model):log_fmt=csv:log_path=3/$($_.name).vmaf.csv" -f null -
    $b = Import-Csv 3/$($_.name).vmaf.csv
    $vmaf[$_.Name] = $b
    "$($_.Name) {0:F}Mbps {1} $model" -f ($bit_rate/1Mb),(($b.vmaf | Sort-Object)[[int](($b.vmaf.count -1) /2)])
}

plot_vmaf($vmaf)
#Read-Host -Prompt "Press any key to continue"