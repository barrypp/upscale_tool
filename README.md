# upscale_tool

## procedure for upscale_and_rife_2
|name|fps(output)|size|
|-|-|-|
|animejanaiV2L3,RIFEModel.v4_6|11 fps|720p to 2160p|
|animejanaiV2L3,RIFEModel.v4_6|20 fps|1080p to 2160p|
|animejanaiV2L3,jpg to webp|1.6 fps|720p to 2160p|
```
path=%path%;C:\ProgramFiles\mpv

for %i in (*.mp4,*.mkv) do ffprobe -hide_banner "%i" 2>>1.txt

ffmpeg -hide_banner -h encoder=hevc_nvenc
# for %i in (2\*.mp4,2\*.mkv) do vspipe -p -c y4m --arg "in=%i" upscale_and_rife_2.vpy .
for %i in (2\*.mp4,2\*.mkv,2\*.jpg) do vspipe -p -c y4m --arg "in=%i" upscale_and_rife_2.vpy --info
for %i in (2\*.mp4,2\*.mkv,2\*.jpg) do vspipe -p -c y4m --arg "in=%i" upscale_and_rife_2.vpy --graph full > 1.dot

for %i in (1\*.mp4,1\*.mkv) do ffmpeg -hide_banner -y -hwaccel d3d11va -ss "00:00:00" -t "00:00:01" -i "%i" -c copy "2\%~ni, test.mkv"

for %i in (2\*.mp4,2\*.mkv) do vspipe -c y4m --arg "in=%i" upscale_and_rife_2.vpy - | ffmpeg -hide_banner -y -i - -i "%i" -map 0:v -map 1 -map -1:v -c:a copy -c:s copy -c:v hevc_nvenc -preset p7 -pix_fmt p010le -profile:v main10 -b:v 0K "3\%~ni.mkv"
```
|name|src|
|-|-|
|ffms2|https://github.com/FFMS/ffms2/releases/download/2.40/ffms2-2.40-msvc.7z|
|upscale_and_rife_2.vpy|https://github.com/barrypp/upscale_tool/blob/b0de74c2f45699101ac53a6084f7d7e9fc415d91/upscale_and_rife_2.vpy|
|!1-all_to_webp_quality99_and_upscale.ps1|https://github.com/barrypp/upscale_tool/blob/b0de74c2f45699101ac53a6084f7d7e9fc415d91/!1-all_to_webp_quality99_and_upscale.ps1|
|vsmlrt.py|https://github.com/barrypp/upscale_tool/blob/c0b85670f300a65c44ce5843adc697156180152d/vsmlrt.py|
|k7sfunc.py|https://github.com/barrypp/upscale_tool/blob/b0de74c2f45699101ac53a6084f7d7e9fc415d91/k7sfunc.py|
|mpv-lazy|mpv-lazy-20230630-vsMega|
|RealESRGAN_x2plus.onnx|https://github.com/HolyWu/vs-realesrgan/releases/download/model/RealESRGAN_x2plus.onnx|
|RealESRGAN_x4plus.onnx|https://github.com/HolyWu/vs-realesrgan/releases/download/model/RealESRGAN_x4plus.onnx|
|ffmpeg|n6.0-18|


## procedure for upscale_and_rife (old)
|name|fps(output)|size|
|-|-|-|
|RealESRGAN_x4plus,RIFEModel.v4_6|2.6 fps|720p to 2160p|
|RealESRGAN_x2plus,RIFEModel.v4_6|4.6 fps|1080p to 2160p|
|RealESRGAN_x4plus_anime_6B,RIFEModel.v4_6|7.7 fps|720p to 2160p|
|realesr-animevideov3,RIFEModel.v4_6|17 fps|1080p to 2160p|
|realesr-animevideov3,RIFEModel.v4_6|24 fps|720p to 2160p|
```
ffmpeg -h encoder=hevc_nvenc
for %i in (*.mp4,*.mkv) do vspipe -p -c y4m --arg "in=%i" upscale_and_rife.vpy .
for %i in (*.mp4,*.mkv) do vspipe -p -c y4m --arg "in=%i" upscale_and_rife.vpy --info
for %i in (*.mp4,*.mkv) do vspipe -p -c y4m --arg "in=%i" upscale_and_rife.vpy --graph full > 1.dot

for %i in (1\*.mp4,1\*.mkv) do ffmpeg -y -hwaccel d3d11va -ss "00:9:20" -t "00:00:10" -i "%i" -c:v hevc_nvenc "2\%~ni, test.mkv"

for %i in (1\*.mp4,1\*.mkv) do vspipe -c y4m --arg "in=%i" upscale_and_rife.vpy - | ffmpeg -y -i - -i "%i" -map 0:v -map 1 -map -1:v -c:a copy -c:s copy -c:v hevc_nvenc -preset p7 -pix_fmt p010le -profile:v main10 -b:v 0K "3\%~ni, 2160p.mkv"

```
|name|src|
|-|-|
|upscale_and_rife.vpy|https://github.com/barrypp/upscale_tool/blob/84990b81ed487c2cd82302004891e4d789ee7198/upscale_and_rife.vpy|
|vsmlrt.py|https://github.com/barrypp/upscale_tool/blob/eadb4fb493563657f0c64074b6f168ffc98b478a/vsmlrt.py|
|vs-mlrt|https://github.com/AmusementClub/vs-mlrt/releases/tag/v12.3.test|
|RealESRGAN_x4plus.onnx|https://github.com/HolyWu/vs-realesrgan/releases/download/model/RealESRGAN_x4plus.onnx|
|ffmpeg|5.1.2|


## benchmark (old)

|name|version|fps(source) for 720p|
|-|-|-|
|rife-ncnn-vulkan,png|Release 20221029|1440frames/18.6966328s = 77.019fps|
|rife-ncnn-vulkan,jpg|Release 20221029|1440frames/13.5232566s = 106.48fps|
|vs-rife-trt,ffmpeg,png|mpv-lazy-2023V1|1440frames/41.31s = 34.858fps|
|vs-rife-trt,ffmpeg,jpg|mpv-lazy-2023V1|1440frames/16.70s = 86.2275fps|
|vs-rife-trt|mpv-lazy-2023V1|1440frames/14.32s = 100.55866fps|
|vs-rife-trt,ffmpeg,png|mpv-lazy-2023V1 [patch](https://github.com/hooke007/MPV_lazy/discussions/123#discussioncomment-4659072)|74fps|
|vs-rife-trt,ffmpeg,jpg|mpv-lazy-2023V1 [patch](https://github.com/hooke007/MPV_lazy/discussions/123#discussioncomment-4659072)|156fps|
|vs-rife-trt|mpv-lazy-2023V1 [patch](https://github.com/hooke007/MPV_lazy/discussions/123#discussioncomment-4659072)|1441framess/9.39s = 153.461fps|
|realcugan-ncnn-vulkan,png|Release 20220728|100frames/12.6426513s = 7.91fps|
|realcugan-ncnn-vulkan,jpg|Release 20220728|100frames/12.8281213s = 7.795fps|
|realesrgan-ncnn-vulkan,png|V0.2.5.0|10frames/23.5290052s = 0.425fps|
|realesrgan-ncnn-vulkan,jpg|V0.2.5.0|10frames/23.3038919s = 0.429fps|
|TensorRT_Real_ESRGA|release 2023-1-12|1.39821 fps/s|
```
Measure-Command { rife-ncnn-vulkan -v -i 1_frames -o 2_rife_frames -j 10:10:10 -m rife-v4.6 -f frame_%08d.png}
Measure-Command { realcugan-ncnn-vulkan -v -i 2_rife_frames -o 3_upscale_frames -j 4:4:4 -s 2}
Measure-Command { realesrgan-ncnn-vulkan -v -i 2_rife_frames -o 3_upscale_frames -j 2:2:2 -n realesrgan-x4plus}
vspipe -c y4m rife_cuda.vpy - | ffmpeg -i - -fps_mode passthrough 2_rife_frames/frame_%08d.png
vspipe -c y4m rife_cuda.vpy - | ffmpeg -i - -fps_mode passthrough -qscale:v 1 -qmin 1 -qmax 1 2_rife_frames/frame_%08d.jpg
vspipe -p -c y4m rife_cuda.vpy .
TensorRT_Real_ESRGA, RealESRGAN_x4plus;maxBatchSize,1;precision_mode,16;OUT_SCALE,4
```

---

|name|version|fps for 2160p|
|-|-|-|
|rife-ncnn-vulkan,png,1:1:1|Release 20221029|80frames/35.4784088s = 2.255fps|
|rife-ncnn-vulkan,png,4:4:4|Release 20221029|80frames/11.6383979s = 6.874fps|
|rife-ncnn-vulkan,png,16:4:16|Release 20221029|80frames/7.2700747s = 11.004fps|
|rife-ncnn-vulkan,png,16:2:16|Release 20221029|80frames/7.0000219s = 11.429fps|
|rife-ncnn-vulkan,png,32:2:32|Release 20221029|80frames/7.0569331s = 11.336fps|
|rife-ncnn-vulkan,png,8:2:8|Release 20221029|80frames/7.7020066s = 10.387fps|
```
Measure-Command { rife-ncnn-vulkan -v -i 1_frames -o 2_rife_frames -j *:*:* -m rife-v4.6 -f frame_%08d.png}
```

---

|name|version|fps for 720p|
|-|-|-|
|realesrgan-ncnn-vulkan,png,4:4:4|V0.2.5.0|10frames/23.5777099s = 0.424fps|
|realesrgan-ncnn-vulkan,png,2:2:2|V0.2.5.0|10frames/23.8314694s = 0.42fps|
|realesrgan-ncnn-vulkan,png,1:2:1|V0.2.5.0|10frames/24.1599941s = 0.414fps|
|realesrgan-ncnn-vulkan,png,2:1:2|V0.2.5.0|10frames/26.1573922s = 0.382fps|
|realesrgan-ncnn-vulkan,png,1:1:1|V0.2.5.0|10frames/26.0006624s = 0.385fps|
```
Measure-Command { realesrgan-ncnn-vulkan -v -i 2_rife_frames -o 3_upscale_frames -j *:*:* -n realesrgan-x4plus}
```
---

|name|version|fps for 720p|
|-|-|-|
|realcugan-ncnn-vulkan,png,8:8:8|Release 20220728|120frames/15.5509565s = 7.717fps|
|realcugan-ncnn-vulkan,png,4:4:4|Release 20220728|120frames/15.431134s = 7.776fps|
|realcugan-ncnn-vulkan,png,2:2:2|Release 20220728|120frames/15.5341921s = 7.725fps|
|realcugan-ncnn-vulkan,png,1:2:1|Release 20220728|120frames/16.3124188s = 7.356fps|
|realcugan-ncnn-vulkan,png,2:1:2|Release 20220728|120frames/19.5704774s = 6.132fps|
|realcugan-ncnn-vulkan,png,1:1:1|Release 20220728|120frames/19.7746196s = 6.068fps|
```
Measure-Command { realcugan-ncnn-vulkan -v -i 2_rife_frames -o 3_upscale_frames -j *:*:* -s 2}
```

10700k+RTX3080+RAMDISK

## source
|name|from|
|-|-|
|rife-ncnn-vulkan|https://github.com/nihui/rife-ncnn-vulkan/releases|
|realcugan-ncnn-vulkan|https://github.com/nihui/realcugan-ncnn-vulkan/releases|
|realesrgan-ncnn-vulkan|https://github.com/xinntao/Real-ESRGAN/releases|
|rife_cuda.vpy|https://github.com/hooke007/MPV_lazy/releases, with minor change to script|
|TensorRT_Real_ESRGAN|https://github.com/barrypp/TensorRT_EX/releases|

