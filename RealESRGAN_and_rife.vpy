## based on https://github.com/hooke007/MPV_lazy/blob/5ead596d39af346418022bbf5ed1e50a31291a6b/portable_config/vs/rife_cuda.vpy

import vapoursynth as vs
from vapoursynth import core
import math
from vsmlrt import RealESRGANv2, RealESRGANv2Model, Backend
from vsmlrt import RIFE, RIFEModel

#
in_file = '1.mp4'
model_RealESRGAN = RealESRGANv2Model.RealESRGAN_x4plus
model_RIFE = RIFEModel.v4_6
GPU_thread_RealESRGAN = 1  # 使用的显卡线程数 (won't regerate engine)
GPU_thread_RIFE = 1   	   # 使用的显卡线程数
FPS_up = 2    			   # 补帧倍率（整数）（RIFE）
GPU = 0        			   # 使用的显卡序号，0为排序一号
WS_size_RealESRGAN = 512 # 约束显存（MiB)
WS_size_RIFE = 4096 # 约束显存（MiB），静态引擎的最小值为128（动态引擎自动双倍），设为低于此数的值即最大化利用
Lk_fmt = False # 锁定输出像素格式为yuv420p8

#
input = core.ffms2.Source(source=in_file)  # Load a video track in mkv file
colorlv = input.get_frame(0).props._ColorRange
fmt_in = input.format.id

fmt_out = fmt_in
if fmt_in not in [vs.YUV410P8, vs.YUV411P8, vs.YUV420P8, vs.YUV422P8, vs.YUV444P8, vs.YUV420P10, vs.YUV422P10, vs.YUV444P10] :
	fmt_out = vs.YUV420P10

#
cut0 = core.misc.SCDetect(clip=input, threshold=0.15)
cut1 = core.resize.Bilinear(clip=cut0, format=vs.RGBH, matrix_in_s="709")

#
output_RealESRGAN = cut1
if model_RealESRGAN is not None :
	#
	cut3 = RealESRGANv2(clip=cut1, scale=2160/input.height, model=model_RealESRGAN, backend=Backend.TRT(
		max_shapes=None, opt_shapes=None, fp16=True,
		device_id=GPU, workspace=WS_size_RealESRGAN, use_cuda_graph=True,
		num_streams=GPU_thread_RealESRGAN, static_shape=True, output_format=1, min_shapes=[0, 0]))
	output_RealESRGAN = cut3

#
output_RIFE = output_RealESRGAN
if model_RIFE is not None :
	#
	input = output_RealESRGAN
	w_in, h_in = input.width, input.height
	scale_model = 1
#	if (w_in * h_in > 2048 * 1088) :
#		scale_model = 0.5
	#
	tile_size = 32 / scale_model
	w_tmp = math.ceil(w_in / tile_size) * tile_size - w_in
	h_tmp = math.ceil(h_in / tile_size) * tile_size - h_in
	#
	cut5 = core.std.AddBorders(clip=input, right=w_tmp, bottom=h_tmp)
	cut7 = RIFE(clip=cut5, multi=FPS_up, scale=scale_model, model=model_RIFE, backend=Backend.TRT(
		max_shapes=None, opt_shapes=None, fp16=True,
		device_id=GPU, workspace=WS_size_RIFE, use_cuda_graph=True,
		num_streams=GPU_thread_RIFE, static_shape=True, output_format=1, min_shapes=[0, 0]))
	cut9 = core.std.Crop(clip=cut7, right=w_tmp, bottom=h_tmp)
	output_RIFE = cut9

#
output = core.resize.Bilinear(clip=output_RIFE, format=vs.YUV420P8 if Lk_fmt else fmt_out, matrix_s="709", range=1 if colorlv==0 else None)
output.set_output()
