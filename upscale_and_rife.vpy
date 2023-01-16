## based on https://github.com/hooke007/MPV_lazy/blob/5ead596d39af346418022bbf5ed1e50a31291a6b/portable_config/vs/rife_cuda.vpy

import vapoursynth as vs
from vapoursynth import core
import math
from vsmlrt import RealESRGANv2, RealESRGANv2Model, Backend
from vsmlrt import RIFE, RIFEModel, CUGAN

#
in_file = globals()["in"]
upscale = "RealESRGAN" #"RealESRGAN", "cugan", None
upfps = "RIFE" #"RIFE", None
model_RealESRGAN = RealESRGANv2Model.RealESRGAN_x4plus_anime_6B #RealESRGAN_x4plus,RealESRGAN_x2plus,RealESRGAN_x4plus_anime_6B
model_RIFE = RIFEModel.v4_6
noise_CUGAN = -1

#
clip = core.ffms2.Source(source=in_file)  # Load a video track in mkv file
if (clip.height >= 2160 or clip.width >= 3840) :
	upscale = None

#
GPU_thread_RealESRGAN = 1  # 使用的显卡线程数 (won't regerate engine)
GPU_thread_CUGAN = 1
GPU_thread_RIFE = 1   	   # 使用的显卡线程数
FPS_up = 2    			   # 补帧倍率（整数）（RIFE）
GPU = 0        			   # 使用的显卡序号，0为排序一号
WS_size_RealESRGAN = 512 # 约束显存（MiB) 不太理解这玩意与实际显存占用的关系
WS_size_CUGAN = 256 # 约束显存（MiB)， bug, not enough memory
WS_size_RIFE = 4096 # 约束显存（MiB)
Lk_fmt = False # 锁定输出像素格式为yuv420p8

#
colorlv = None
if "_ColorRange" in clip.get_frame(0).props :
	colorlv = clip.get_frame(0).props._ColorRange
fmt_in = clip.format.id

fmt_out = fmt_in
if fmt_in not in [vs.YUV410P8, vs.YUV411P8, vs.YUV420P8, vs.YUV422P8, vs.YUV444P8, vs.YUV420P10, vs.YUV422P10, vs.YUV444P10] :
	fmt_out = vs.YUV420P10

#
def resize(clip: vs.VideoNode) -> vs.VideoNode :
	if (clip.height == 2160 or clip.width == 3840) :
		return clip
	else :
		scale = max(clip.height/2160, clip.width/3840)
		return core.resize.Lanczos(clip=clip, height=clip.height/scale, width=clip.width/scale)

#
clip = core.misc.SCDetect(clip=clip, threshold=0.15)
clip = core.resize.Bilinear(clip=clip, format=vs.RGBH, matrix_in_s="709")

#
if upscale == "RealESRGAN" :
	clip = RealESRGANv2(clip=clip, scale=None, model=model_RealESRGAN, backend=Backend.TRT(
		max_shapes=None, opt_shapes=None, fp16=True,
		device_id=GPU, workspace=WS_size_RealESRGAN, use_cuda_graph=True,
		num_streams=GPU_thread_RealESRGAN, static_shape=True, output_format=1, min_shapes=[0, 0]))
elif upscale == "cugan" :
	scale = 3 if clip.height < 1080 and clip.width < 1920 else 2
	clip = CUGAN(clip=clip, noise=noise_CUGAN, scale=scale, version=2, backend=Backend.TRT(
		max_shapes=None, opt_shapes=None, fp16=True,
		device_id=GPU, workspace=WS_size_CUGAN, use_cuda_graph=True,
		num_streams=GPU_thread_CUGAN, static_shape=True, output_format=1, min_shapes=[0, 0]))

#
if upscale is not None :
	clip = resize(clip)

#
if upfps == "RIFE" :
	#
	w_in, h_in = clip.width, clip.height
	scale_model = 1
	#
	tile_size = 32 / scale_model
	w_tmp = math.ceil(w_in / tile_size) * tile_size - w_in
	h_tmp = math.ceil(h_in / tile_size) * tile_size - h_in
	#
	clip = core.std.AddBorders(clip=clip, right=w_tmp, bottom=h_tmp)
	clip = RIFE(clip=clip, multi=FPS_up, scale=scale_model, model=model_RIFE, backend=Backend.TRT(
		max_shapes=None, opt_shapes=None, fp16=True,
		device_id=GPU, workspace=WS_size_RIFE, use_cuda_graph=True,
		num_streams=GPU_thread_RIFE, static_shape=True, output_format=1, min_shapes=[0, 0]))
	clip = core.std.Crop(clip=clip, right=w_tmp, bottom=h_tmp)

#
clip = core.resize.Bilinear(clip=clip, format=vs.YUV420P8 if Lk_fmt else fmt_out, matrix_s="709", range=1 if colorlv==0 else None)
clip.set_output()
