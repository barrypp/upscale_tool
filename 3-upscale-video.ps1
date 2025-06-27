$env:Path = 'C:\Program Files\7-Zip;C:\ProgramFiles\mpv;' + $env:Path
Import-Module ./5-plot.psm1

#ffmpeg -hide_banner -h encoder=av1_nvenc -filters -encoders -hwaccels
#ffprobe -v error -select_streams v:0 -show_entries stream/frame/stream -i 1.mkv
#ffmpeg -hide_banner -i 1.mkv -vf vfrdet -an  -f null -

#ls 2/*.mkv | % { vspipe -p -c y4m --arg "in=$_" --arg is_img=False upscale_and_rife_2.vpy . }
#ls 2/*.mkv | % { vspipe -p -c y4m --arg "in=$_" --arg is_img=False upscale_and_rife_2.vpy --info }
#ls 2/*.mkv | % { vspipe -p -c y4m --arg "in=$_" --arg is_img=False upscale_and_rife_2.vpy --graph full > 1.dot }
#ffprobe -v error -select_streams v:0 -show_entries frame=pts_time,pkt_size,pict_type -of csv=s=,:p=0 -i .\p7_cq00.mkv
#ls *.mkv | % {$bit_rate = ffprobe -v error -select_streams v:0 -show_entries format=bit_rate -of csv=s=x:p=0 -i $_; "{0,5:F}Mbps {1}" -f ($bit_rate/1Mb),($_.Name) } | sort -Desc
#ffmpeg -v warning -stats -y -hwaccel d3d11va -ss "00:58:31" -t "00:00:02" -i $a -c:a flac -fps_mode passthrough -c:v hevc_nvenc -preset p7 -tune lossless -pix_fmt p010le -profile:v main10 2/test.mkv

#ls 1/*.mkv | % { $a = Split-Path $_ -LeafBase; ffmpeg -hide_banner -y -i "$_" -c:a copy -c:s copy -c:v av1_nvenc -preset p7 -b:v 0K -cq 28 "3/$a.mkv" }
#ls 1/*.mkv | % { $a = Split-Path $_ -LeafBase; ffmpeg -hide_banner -y -i "$_" -c:a copy -c:s copy -c:v hevc_nvenc -preset p7 -pix_fmt p010le -profile:v main10 -b:v 0K -cq 26 "3/$a.mkv" }
#ls -Filter '1/*' | % { $a = split-path $_ -LeafBase; cmd /c "vspipe -c y4m --arg ""in=$_"" --arg is_img=False --arg model=RealESRGAN_x2plus.onnx src/upscale_and_rife_2.vpy - | ffmpeg -hide_banner -y -i - -i ""$_"" -map 0:v -map 1:a? -map 1:s? -c:a copy -c:s copy -c:v hevc_nvenc -preset p7 -pix_fmt p010le -profile:v main10 -b:v 0K -cq 28 ""3/$a.mkv""" }

mkdir -Force tmp2,tmp3
$a = (ls ../1/*)[0]
[float]$duration = ffprobe -v error -select_streams v:0 -show_entries format=duration -of csv=s=x:p=0 -i $a
[float]$height = ffprobe -v error -select_streams v:0 -show_entries stream=height -of csv=s=x:p=0 -i $a
ffmpeg -v warning -stats -y -hwaccel d3d11va -ss (Get-Random -Maximum ($duration-60)) -t "00:00:01" -i $a -ss (Get-Random -Maximum ($duration-60)) -t "00:00:01" -i $a -ss (Get-Random -Maximum ($duration-60)) -t "00:00:01" -i $a -ss (Get-Random -Maximum ($duration-60)) -t "00:00:01" -i $a -ss (Get-Random -Maximum ($duration-60)) -t "00:00:01" -i $a -ss (Get-Random -Maximum ($duration-60)) -t "00:00:01" -i $a -filter_complex '[0:v][0:a][1:v][1:a][2:v][2:a][3:v][3:a][4:v][4:a][5:v][5:a]concat=n=6:v=1:a=1[v][a]' -map '[v]' -map '[a]' -c:a flac -fps_mode passthrough -c:v hevc_nvenc -preset p7 -tune lossless -pix_fmt p010le -profile:v main10 tmp2/test.mkv
cmd /c "vspipe -c y4m --arg in=tmp2/test.mkv --arg is_img=False --arg model=RealESRGAN_x2plus.onnx upscale_and_rife_2.vpy - | ffmpeg -v warning -stats -y -i - -map 0:v -c:v hevc_nvenc -preset p7 -tune lossless -pix_fmt p010le -profile:v main10 tmp2/test2.mkv"
#mv tmp2/test.mkv tmp2/test2.mkv

ffmpeg -v warning -stats -y -i tmp2/test2.mkv -map 0:v -c:v av1_nvenc -preset p7 -b:v 0K -cq 28 tmp3/p7_cq28.mkv
#ffmpeg -v warning -stats -y -i tmp2/test2.mkv -map 0:v -c:v av1_nvenc -preset p7 -b:v 0K -cq 32 tmp3/p7_cq32.mkv
#ffmpeg -v warning -stats -y -i tmp2/test2.mkv -map 0:v -c:v libsvtav1 -crf 18 -preset -2 tmp3/m2_crf18.mkv

if ($true){
    $vmaf = @{}
    ls tmp3/*.mkv | sort | ForEach-Object {
        $bit_rate = ffprobe -v error -select_streams v:0 -show_entries format=bit_rate -of csv=s=x:p=0 -i $_
        [int]$height = ffprobe -v error -select_streams v:0 -show_entries stream=height -of csv=s=x:p=0 -i $_
        $model = if ($height -gt 1620) {":model=path='../model/vmaf_4k_v0.6.1.json'"} else {""}
        ffmpeg -v warning -stats -i $_ -i tmp2/test2.mkv -lavfi "[0:v]setpts=PTS-STARTPTS[dis];[1:v]setpts=PTS-STARTPTS[ref];[dis][ref]libvmaf=n_threads=12'$($model):log_fmt=csv:log_path=tmp3/$($_.name).vmaf.csv" -f null -
        #ffmpeg -v warning -stats -hwaccel cuda -hwaccel_output_format cuda -i $_ -hwaccel cuda -hwaccel_output_format cuda -i tmp2/test2.mkv -filter_complex "[0:v]scale_cuda=format=yuv420p[ref];[1:v]scale_cuda=format=yuv420p[dist];[dist][ref]libvmaf_cuda" -f null -
        $b = Import-Csv tmp3/$($_.name).vmaf.csv
        $vmaf[$_.Name] = $b
        "$($_.Name) {0:F}Mbps {1} $model" -f ($bit_rate/1Mb),(($b.vmaf | Sort-Object)[[int](($b.vmaf.count -1) /2)])
    }
    plot_vmaf($vmaf)
}

#Read-Host -Prompt "Press any key to continue"