# upscale_tool

## benchmark
|name|version|fps|
|-|-|-|
|rife-ncnn-vulkan|Release 20221029|2880frames/18.6966328s = 154.038fps|
|realcugan-ncnn-vulkan|Release 20220728|100frames/12.6426513s = 7.91fps|
|realesrgan-ncnn-vulkan|V0.2.5.0|10frames/23.5290052s = 0.425fps|
|vs-rife-trt,ffmpeg,png|mpv-lazy-2023V1|2880frames/41.31s = 70fps|

## benchmark cmd
+ rife-ncnn-vulkan
  - https://github.com/nihui/rife-ncnn-vulkan/releases
  - Measure-Command { rife-ncnn-vulkan -v -i 1_frames -o 2_rife_frames -j 10:10:10 -m rife-v4.6 -f frame_%08d.png}
  
+ realcugan-ncnn-vulkan
  - https://github.com/nihui/realcugan-ncnn-vulkan/releases
  - Measure-Command { realcugan-ncnn-vulkan -v -i 2_rife_frames -o 3_upscale_frames -j 4:4:4 -s 2}
  
+ realesrgan-ncnn-vulkan
  - https://github.com/xinntao/Real-ESRGAN/releases
  - Measure-Command { realesrgan-ncnn-vulkan -v -i 2_rife_frames -o 3_upscale_frames -j 2:2:2 -n realesrgan-x4plus}

+ vs-rife-trt,ffmpeg,png
  - https://github.com/hooke007/MPV_lazy/releases, with minor change to script
  - vspipe -c y4m rife_cuda.vpy - | ffmpeg -i - -fps_mode passthrough 2_rife_frames/frame_%08d.png
