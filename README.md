# upscale_tool

## benchmark

|name|version|fps for 720p|
|-|-|-|
|rife-ncnn-vulkan,png|Release 20221029|1440frames/18.6966328s = 77.019fps|
|rife-ncnn-vulkan,jpg|Release 20221029|1440frames/13.5232566s = 106.48fps|
|realcugan-ncnn-vulkan,png|Release 20220728|100frames/12.6426513s = 7.91fps|
|realcugan-ncnn-vulkan,jpg|Release 20220728|100frames/12.8281213s = 7.795fps|
|realesrgan-ncnn-vulkan,png|V0.2.5.0|10frames/23.5290052s = 0.425fps|
|realesrgan-ncnn-vulkan,jpg|V0.2.5.0|10frames/23.3038919s = 0.429fps|
|vs-rife-trt,ffmpeg,png|mpv-lazy-2023V1|1440frames/41.31s = 34.858fps|
|vs-rife-trt,ffmpeg,jpg|mpv-lazy-2023V1|1440frames/16.70s = 86.2275fps|
|vs-rife-trt|mpv-lazy-2023V1|1440frames/14.32s = 100.55866fps|

|name|version|fps for 2160p|
|-|-|-|
|rife-ncnn-vulkan,png,1:1:1|Release 20221029|80frames/35.4784088s = 2.255fps|
|rife-ncnn-vulkan,png,4:4:4|Release 20221029|80frames/11.6383979s = 6.874fps|
|rife-ncnn-vulkan,png,16:4:16|Release 20221029|80frames/7.2700747s = 11.004fps|
|rife-ncnn-vulkan,png,16:2:16|Release 20221029|80frames/7.0000219s = 11.429fps|
|rife-ncnn-vulkan,png,32:2:32|Release 20221029|80frames/7.0569331s = 11.336fps|
|rife-ncnn-vulkan,png,8:2:8|Release 20221029|80frames/7.7020066s = 10.387fps|

|name|cmd|
|-|-|
|rife-ncnn-vulkan,png|Measure-Command { rife-ncnn-vulkan -v -i 1_frames -o 2_rife_frames -j 10:10:10 -m rife-v4.6 -f frame_%08d.png}|
|rife-ncnn-vulkan,jpg|Measure-Command { rife-ncnn-vulkan -v -i 1_frames -o 2_rife_frames -j 10:10:10 -m rife-v4.6 -f frame_%08d.jpg}|
|rife-ncnn-vulkan,png,*:*:*|Measure-Command { rife-ncnn-vulkan -v -i 1_frames -o 2_rife_frames -j *:*:* -m rife-v4.6 -f frame_%08d.jpg}|
|realcugan-ncnn-vulkan,png|Measure-Command { realcugan-ncnn-vulkan -v -i 2_rife_frames -o 3_upscale_frames -j 4:4:4 -s 2}|
|realcugan-ncnn-vulkan,jpg|Measure-Command { realcugan-ncnn-vulkan -v -i 2_rife_frames -o 3_upscale_frames -j 4:4:4 -s 2 -f jpg}|
|realesrgan-ncnn-vulkan,png|Measure-Command { realesrgan-ncnn-vulkan -v -i 2_rife_frames -o 3_upscale_frames -j 2:2:2 -n realesrgan-x4plus}|
|realesrgan-ncnn-vulkan,jpg|Measure-Command { realesrgan-ncnn-vulkan -v -i 2_rife_frames -o 3_upscale_frames -j 2:2:2 -n realesrgan-x4plus -f jpg} |
|vs-rife-trt,ffmpeg,png|vspipe -c y4m rife_cuda.vpy - \| ffmpeg -i - -fps_mode passthrough 2_rife_frames/frame_%08d.png|
|vs-rife-trt,ffmpeg,jpg|vspipe -c y4m rife_cuda.vpy - \| ffmpeg -i - -fps_mode passthrough -qscale:v 1 -qmin 1 -qmax 1 2_rife_frames/frame_%08d.jpg|
|vs-rife-trt|vspipe -p -c y4m rife_cuda.vpy .|

 
|name|from|
|-|-|
|rife-ncnn-vulkan|https://github.com/nihui/rife-ncnn-vulkan/releases|
|realcugan-ncnn-vulkan|https://github.com/nihui/realcugan-ncnn-vulkan/releases|
|realesrgan-ncnn-vulkan|https://github.com/xinntao/Real-ESRGAN/releases|
|rife_cuda.vpy|https://github.com/hooke007/MPV_lazy/releases, with minor change to script|

## environment
10700k+RTX3080+RAMDISK
