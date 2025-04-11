## based on mpv-lazy

import vapoursynth as vs
from vapoursynth import core
import math
import k7sfunc as k7f

#
in_file = globals()["in"]
is_img = globals()["is_img"] == "True"
model_RealESRGAN = int(globals()["model"]) # RealESRGAN_x2plus = 301, RealESRGAN_x4plus = 302, animejanaiV3-HD-L3 = 5010

#
if is_img :
	with open(in_file) as f:
		lines = [line.rstrip('\n') for line in f]
	clip = core.imwri.Read(filename=lines)
	#clip = core.resize.Bilinear(clip=clip, format=vs.YUV444P10, matrix_s="709")
else :
	clip = core.ffms2.Source(source=in_file)

# RealESRGAN
H_Pre = 2160
Lt_Hd = True
Model = model_RealESRGAN#, 5009, 5010
Gpu = 0
Gpu_T = 1
St_Eng = True if Model == 301 or Model == 302 or Model == 5010 else False
Ws_Size = 0
H_Max = 2160
Lk_Fmt = False
## 整数，预降低处理源高度
## <True|False> 是否对超过HD分辨率（720P）的源进行处理
## <0|2|5005|5006|5007|5008|5009|5010> 使用的模型
## 使用的显卡序号，0为排序一号
## <1|2|3> 使用的显卡线程数
## <True|False> 是否使用静态引擎（需要对不同分辨率的源各进行预处理）；动态引擎自适应不同分辨率（64²→DCI2K）
## <0~1024> 约束显存（MiB），静态引擎的最小值为128（动态引擎自动双倍），设为低于此数的值即为不限制
## 整数，输出高度限制（填你的显示器高度）
## <True|False> 是否锁定像素格式为yuv420p8
#
if Model != 0 and clip.height < 2160 :
	if Model == 301 and clip.height < 1080 :
		Model = 302
	clip = k7f.ESRGAN_NV(clip, lt_hd=Lt_Hd, model=Model, gpu=Gpu, gpu_t=Gpu_T, st_eng=St_Eng, ws_size=Ws_Size,is_img=is_img)
	if clip.height < 2160 :
		clip = k7f.ESRGAN_NV(clip, lt_hd=Lt_Hd, model=Model, gpu=Gpu, gpu_t=Gpu_T, st_eng=St_Eng, ws_size=Ws_Size,is_img=is_img)
	clip = k7f.FMT_CTRL(clip, h_max=H_Max, fmt_pix=1 if Lk_Fmt else 0)

# RIFE
H_Pre = 2160
Lt_D2k = True
Model = 4262
Ext_Proc = False
T_Tta = False
Fps_Num = 2
Fps_Den = 1
Sc_Mode = 0 # for encode
Gpu = 0
Gpu_T = 1
St_Eng = False
Ws_Size = 0
Lk_Fmt = False
## 整数，预降低处理源高度（填你的显示器高度）
## <True|False> 是否对超过DCI2K分辨率的源进行补帧
## <46|4251|426|4262> 使用的模型
## <True|False> 是否使用外部的填充裁切处理
## <True|False> 是否使用ensemble版模型
## 整数，Fps_Num/Fps_Den 的值即帧率倍数
## 整数
## <0|1|2> 场景切换检测的模式，0为禁用
## 使用的显卡序号，0为排序一号
## <1|2|3> 显卡线程数
## <True|False> 是否使用静态引擎（需要对不同分辨率的源各进行预处理）；动态引擎自适应不同分辨率（QVGA→DCI4K）
## 整数，约束显存（MiB），静态引擎的最小值为128（动态引擎自动双倍），设为低于此数的值即最大化利用
## <True|False> 锁定像素格式为yuv420p8
#
if not is_img and clip.fps <= 30 :
	clip = k7f.RIFE_NV(clip, lt_d2k=Lt_D2k, model=Model, ext_proc=Ext_Proc, t_tta=T_Tta, fps_in=float(clip.fps), fps_num=Fps_Num, fps_den=Fps_Den, sc_mode=Sc_Mode, gpu=Gpu, gpu_t=Gpu_T, st_eng=St_Eng, ws_size=Ws_Size)

#
if is_img :
	clip = core.imwri.Write(clip=clip, imgformat="bmp", filename="tmp3/tmp_%d.bmp")
clip.set_output()