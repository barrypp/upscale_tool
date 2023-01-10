# upscale_tool

## benchmark

|name|version|fps|
|-|-|-|
|rife-ncnn-vulkan,png|Release 20221029|1440frames/18.6966328s = 77.019fps|
|rife-ncnn-vulkan,jpg|Release 20221029|1440frames/13.5232566s = 106.48fps|
|realcugan-ncnn-vulkan,png|Release 20220728|100frames/12.6426513s = 7.91fps|
|realcugan-ncnn-vulkan,jpg|Release 20220728|100frames/12.8281213s = 7.795fps|
|realesrgan-ncnn-vulkan,png|V0.2.5.0|10frames/23.5290052s = 0.425fps|
|realesrgan-ncnn-vulkan,jpg|V0.2.5.0|10frames/23.3038919s = 0.429fps|
|vs-rife-trt,ffmpeg,png|mpv-lazy-2023V1|1440frames/41.31s = 34.858fps|
|vs-rife-trt,ffmpeg,jpg|mpv-lazy-2023V1|1440frames/16.70s = 86.2275fps|

|name|cmd|
|-|-|
|rife-ncnn-vulkan,png|Measure-Command { rife-ncnn-vulkan -v -i 1_frames -o 2_rife_frames -j 10:10:10 -m rife-v4.6 -f frame_%08d.png}|
|rife-ncnn-vulkan,jpg|Measure-Command { rife-ncnn-vulkan -v -i 1_frames -o 2_rife_frames -j 10:10:10 -m rife-v4.6 -f frame_%08d.jpg}|
|realcugan-ncnn-vulkan,png|Measure-Command { realcugan-ncnn-vulkan -v -i 2_rife_frames -o 3_upscale_frames -j 4:4:4 -s 2}|
|realcugan-ncnn-vulkan,jpg|Measure-Command { realcugan-ncnn-vulkan -v -i 2_rife_frames -o 3_upscale_frames -j 4:4:4 -s 2 -f jpg}|
|realesrgan-ncnn-vulkan,png|Measure-Command { realesrgan-ncnn-vulkan -v -i 2_rife_frames -o 3_upscale_frames -j 2:2:2 -n realesrgan-x4plus}|
|realesrgan-ncnn-vulkan,jpg|Measure-Command { realesrgan-ncnn-vulkan -v -i 2_rife_frames -o 3_upscale_frames -j 2:2:2 -n realesrgan-x4plus -f jpg} |
|vs-rife-trt,ffmpeg,png|vspipe -c y4m rife_cuda.vpy - \| ffmpeg -i - -fps_mode passthrough 2_rife_frames/frame_%08d.png|
|vs-rife-trt,ffmpeg,jpg|vspipe -c y4m rife_cuda.vpy - \| ffmpeg -i - -fps_mode passthrough -qscale:v 1 -qmin 1 -qmax 1 2_rife_frames/frame_%08d.jpg|

 
|name|from|
|-|-|
|rife-ncnn-vulkan|https://github.com/nihui/rife-ncnn-vulkan/releases|
|realcugan-ncnn-vulkan|https://github.com/nihui/realcugan-ncnn-vulkan/releases|
|realesrgan-ncnn-vulkan|https://github.com/xinntao/Real-ESRGAN/releases|
|rife_cuda.vpy|https://github.com/hooke007/MPV_lazy/releases, with minor change to script|

## environment
10700k+RTX3080+RAMDISK
