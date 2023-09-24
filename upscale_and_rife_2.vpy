## based on mpv-lazy

import vapoursynth as vs
from vapoursynth import core
import math
import k7sfunc as k7f

#
in_file = globals()["in"]
is_img = True
upscale = "RealESRGAN" #"RealESRGAN", None
upfps = "None" #"RIFE", None
model_RealESRGAN = 5007#  RealESRGAN_x2plus = 301, RealESRGAN_x4plus = 302, animejanaiV2L3 = 5007

# RealESRGAN
H_Pre = 720
Lt_Hd = True
Model = model_RealESRGAN
Scale = 4 if Model==2 or Model==302 else 2
Gpu = 0
RealESRGAN_Gpu_T = 1 if is_img else 1
RealESRGAN_St_Eng = True if model_RealESRGAN == 302 or model_RealESRGAN == 5007 else False
Ws_Size = 0
H_Max = 2160
Lk_Fmt = False
## 整数，预降低处理源高度
## <True|False> 是否对超过HD分辨率（720P）的源进行处理
## <0|2|5005|5006|5007> 使用的模型
## 使用的显卡序号，0为排序一号
## <1|2|3> 使用的显卡线程数
## <True|False> 是否使用静态引擎（需要对不同分辨率的源各进行预处理）；动态引擎自适应不同分辨率（64²→DCI2K）
## <0~1024> 约束显存（MiB），静态引擎的最小值为128（动态引擎自动双倍），设为低于此数的值即为不限制
## 整数，输出高度限制（填你的显示器高度）
## <True|False> 是否锁定像素格式为yuv420p8

# RIFE
H_Pre = 1440
Lt_D2k = True
Sc_Mode = 1
Fps_Num = 2
T_Tta = False
Ext_Proc = True
Gpu = 0
RIFE_Gpu_T = 1
RIFE_St_Eng = False
Ws_Size = 0
Lk_Fmt = False
## 整数，预降低处理源高度（填你的显示器高度）
## <True|False> 是否对超过DCI2K分辨率的源进行补帧
## <0|1|2> 场景切换检测的模式，0为禁用
## <2|3|4> 补帧倍率
## <True|False> 是否使用ensemble版模型
## <True|False> 是否使用外部的填充裁切处理（禁用将强制锁定为静态引擎）
## 使用的显卡序号，0为排序一号
## <1|2|3> 显卡线程数
## <True|False> 是否使用静态引擎（需要对不同分辨率的源各进行预处理）；动态引擎自适应不同分辨率（QVGA→DCI4K）
## 整数，约束显存（MiB），静态引擎的最小值为128（动态引擎自动双倍），设为低于此数的值即最大化利用
## <True|False> 锁定像素格式为yuv420p8

#
if is_img :
	with open(in_file) as f:
		lines = [line.rstrip('\n') for line in f]
	clip = core.imwri.Read(filename=lines)
	#clip = core.resize.Bilinear(clip=clip, format=vs.YUV444P10, matrix_s="709")
else :
	clip = core.ffms2.Source(source=in_file)


#
if upscale == "RealESRGAN" :
	#ret = k7f.FMT_CTRL(clip, h_max=2160, h_ret=True)
	#clip = k7f.FMT_CTRL(clip, h_max=H_Pre, fmt_pix=1 if Lk_Fmt else 0)
	clip = k7f.ESRGAN_NV(clip, lt_hd=Lt_Hd, model=Model, scale=Scale, gpu=Gpu, gpu_t=RealESRGAN_Gpu_T, st_eng=RealESRGAN_St_Eng, ws_size=Ws_Size,is_img=is_img)
	if clip.height < 2160 :
		clip = k7f.ESRGAN_NV(clip, lt_hd=Lt_Hd, model=Model, scale=Scale, gpu=Gpu, gpu_t=RealESRGAN_Gpu_T, st_eng=RealESRGAN_St_Eng, ws_size=Ws_Size,is_img=is_img)	
	clip = k7f.FMT_CTRL(clip, h_max=H_Max, fmt_pix=1 if Lk_Fmt else 0)


#
if upfps == "RIFE" :
	#ret = k7f.FPS_CTRL(clip, fps_in=container_fps, fps_ret=True)
	#clip = k7f.FMT_CTRL(clip, h_max=H_Pre, fmt_pix=1 if Lk_Fmt else 0)
	clip = k7f.RIFE_NV(clip, lt_d2k=Lt_D2k, sc_mode=Sc_Mode, fps_num=Fps_Num, t_tta=T_Tta, ext_proc=Ext_Proc, gpu=Gpu, gpu_t=RIFE_Gpu_T, st_eng=RIFE_St_Eng, ws_size=Ws_Size)

#
clip = core.imwri.Write(clip=clip, imgformat="webp", filename="3/tmp/tmp_%d.webp", quality=99)
clip.set_output()

