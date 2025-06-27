## based on mpv-lazy

import vapoursynth as vs
from vapoursynth import core
import math
import k7sfunc as k7f

#
in_file = globals()["in"]
is_img = globals()["is_img"] == "True"
model_RealESRGAN_path = globals()["model"]

#
if is_img :
	with open(in_file) as f:
		lines = [line.rstrip('\n') for line in f]
	clip = core.imwri.Read(filename=lines)
	#clip = core.resize.Bilinear(clip=clip, format=vs.YUV444P10, matrix_s="709")
else :
	clip = core.ffms2.Source(source=in_file)


H_Pre = 2160
Model = model_RealESRGAN_path
Fp16_Qnt = True
Gpu = 0
Gpu_T = 1
St_Eng = True
Res_Opt = [clip.width, clip.height]
Res_Max = [1920, 2160]
Ws_Size = 0
H_Max = 2160
Lk_Fmt = False
## 整数，预降低处理源高度
## 指定使用的模型，文件放置位为 .../mpv-lazy/vs-plugins/models/
## <True|False> 是否为fp32模型使用fp16量化
## 使用的显卡序号，0为排序一号
## <1|2|3> 使用的显卡线程数
## <True|False> 是否使用静态引擎，否则为动态
## 动态引擎的优化源分辨率（高度不大于 H_Pre）
## 动态引擎的最大支持源分辨率
## <0~1024> 整数，约束显存（MiB），最小值为128，设为低于此数的值即为不限制
## 整数，输出高度限制（填你的显示器高度）
## <True|False> 是否锁定像素格式为yuv420p8

#
if Model != 0 and clip.height < 2160 :
	if Model == "RealESRGAN_x2plus.onnx" and clip.height < 1080 :
		Model = "RealESRGAN_x4plus.onnx"
	Res_Opt = [clip.width, clip.height]
	clip = k7f.UAI_NV_TRT(clip, clamp=False, model_pth=Model, opt_lv=3, cuda_opt=[0, 0, 0], int8_qnt=False, fp16_qnt=Fp16_Qnt, gpu=Gpu, gpu_t=Gpu_T, st_eng=St_Eng, res_opt=Res_Opt, res_max=Res_Max, ws_size=Ws_Size,is_img=is_img)
	if clip.height < 2160 :
		Res_Opt = [clip.width, clip.height]
		clip = k7f.UAI_NV_TRT(clip, clamp=False, model_pth=Model, opt_lv=3, cuda_opt=[0, 0, 0], int8_qnt=False, fp16_qnt=Fp16_Qnt, gpu=Gpu, gpu_t=Gpu_T, st_eng=St_Eng, res_opt=Res_Opt, res_max=Res_Max, ws_size=Ws_Size,is_img=is_img)
	clip = k7f.FMT_CTRL(clip, h_max=H_Max, fmt_pix=1 if Lk_Fmt else 0)	

# RIFE
H_Pre = 2160
Model = 4262
Fps_Num = 2
Fps_Den = 1
Sc_Mode = 0 # for encode
Gpu = 0
Gpu_T = 1
Ws_Size = 0
Lk_Fmt = False
## 整数，预降低处理源高度（填你的显示器高度）
## <46|4251|426|4262> 使用的模型
## 整数，Fps_Num/Fps_Den 的值即帧率倍数
## 整数
## <0|1|2> 场景切换检测的模式，0为禁用
## 使用的显卡序号，0为排序一号
## <1|2|3> 显卡线程数
## 整数，手动约束引擎构建阶段的显存（MiB），最小值为128，设为低于此数的值即最大化利用
## <True|False> 锁定像素格式为yuv420p8

#
if not is_img and clip.fps <= 30 :
	clip = k7f.RIFE_NV(clip, model=Model, int8_qnt=False, turbo=True, fps_in=float(clip.fps), fps_num=Fps_Num, fps_den=Fps_Den, sc_mode=Sc_Mode, gpu=Gpu, gpu_t=Gpu_T, ws_size=Ws_Size)

#
if is_img :
	clip = core.imwri.Write(clip=clip, imgformat="bmp", filename="tmp3/tmp_%d.bmp")
clip.set_output()