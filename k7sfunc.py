##################################################
### 文档： https://github.com/hooke007/MPV_lazy/wiki/3_K7sfunc
##################################################

__version__ = "0.8.3"

__all__ = [
	"FMT_CHANGE", "FMT_CTRL",
	"FPS_CHANGE", "FPS_CTRL",

	"ACNET_STD", "ARTCNN_NV", "CUGAN_NV", "EDI_US_STD",
	"ESRGAN_DML", "ESRGAN_NV",
	"NGU_HQ",
	"WAIFU_DML", "WAIFU_NV",

	"MVT_LQ", "MVT_STD", "MVT_POT", "MVT_MQ",
	"RIFE_STD", "RIFE_DML", "RIFE_NV",
	"SVP_LQ", "SVP_STD", "SVP_HQ", "SVP_PRO",

	"DPIR_DBLK_NV",
	"BILA_NV", "BM3D_NV",
	"CCD_STD",
	"DFTT_STD", "DFTT_NV",
	"DPIR_NR_NV", "FFT3D_STD",
	"NLM_STD", "NLM_NV",

	"COLOR_P3W_FIX", "CSC_RB",
	"DEBAND_STD",
	"DEINT_LQ", "DEINT_STD", "DEINT_EX",
	"EDI_AA_STD", "EDI_AA_NV",
	"IVTC_STD",
	"STAB_STD", "STAB_HQ",

	"UAI_DML", "UAI_MIGX", "UAI_NV_TRT",
	"UVR_MAD",
]

##################################################
## https://github.com/python/cpython/blob/v3.11.8/Lib/distutils/version.py
##################################################

import re

class Version:
	def __init__ (self, vstring=None):
		if vstring:
			self.parse(vstring)
	def __repr__ (self):
		return "%s ('%s')" % (self.__class__.__name__, str(self))
	def __eq__(self, other):
		c = self._cmp(other)
		if c is NotImplemented:
			return c
		return c == 0
	def __lt__(self, other):
		c = self._cmp(other)
		if c is NotImplemented:
			return c
		return c < 0
	def __le__(self, other):
		c = self._cmp(other)
		if c is NotImplemented:
			return c
		return c <= 0
	def __gt__(self, other):
		c = self._cmp(other)
		if c is NotImplemented:
			return c
		return c > 0
	def __ge__(self, other):
		c = self._cmp(other)
		if c is NotImplemented:
			return c
		return c >= 0

class StrictVersion (Version):
	version_re = re.compile(r'^(\d+) \. (\d+) (\. (\d+))? ([ab](\d+))?$',
							re.VERBOSE | re.ASCII)
	def parse (self, vstring):
		match = self.version_re.match(vstring)
		if not match:
			raise ValueError("invalid version number '%s'" % vstring)
		(major, minor, patch, prerelease, prerelease_num) = \
			match.group(1, 2, 4, 5, 6)
		if patch:
			self.version = tuple(map(int, [major, minor, patch]))
		else:
			self.version = tuple(map(int, [major, minor])) + (0,)
		if prerelease:
			self.prerelease = (prerelease[0], int(prerelease_num))
		else:
			self.prerelease = None
	def __str__ (self):
		if self.version[2] == 0:
			vstring = '.'.join(map(str, self.version[0:2]))
		else:
			vstring = '.'.join(map(str, self.version))
		if self.prerelease:
			vstring = vstring + self.prerelease[0] + str(self.prerelease[1])
		return vstring
	def _cmp (self, other):
		if isinstance(other, str):
			other = StrictVersion(other)
		elif not isinstance(other, StrictVersion):
			return NotImplemented
		if self.version != other.version:
			if self.version < other.version:
				return -1
			else:
				return 1
		if (not self.prerelease and not other.prerelease):
			return 0
		elif (self.prerelease and not other.prerelease):
			return -1
		elif (not self.prerelease and other.prerelease):
			return 1
		elif (self.prerelease and other.prerelease):
			if self.prerelease == other.prerelease:
				return 0
			elif self.prerelease < other.prerelease:
				return -1
			else:
				return 1
		else:
			assert False, "never get here"

class LooseVersion (Version):
	component_re = re.compile(r'(\d+ | [a-z]+ | \.)', re.VERBOSE)
	def __init__ (self, vstring=None):
		if vstring:
			self.parse(vstring)
	def parse (self, vstring):
		self.vstring = vstring
		components = [x for x in self.component_re.split(vstring)
								if x and x != '.']
		for i, obj in enumerate(components):
			try:
				components[i] = int(obj)
			except ValueError:
				pass
		self.version = components
	def __str__ (self):
		return self.vstring
	def __repr__ (self):
		return "LooseVersion ('%s')" % str(self)
	def _cmp (self, other):
		if isinstance(other, str):
			other = LooseVersion(other)
		elif not isinstance(other, LooseVersion):
			return NotImplemented
		if self.version == other.version:
			return 0
		if self.version < other.version:
			return -1
		if self.version > other.version:
			return 1

##################################################
## 初始设置
##################################################

import os
import vapoursynth as vs

vs_thd_init = os.cpu_count()
if vs_thd_init > 8 and vs_thd_init <= 16 :
	vs_thd_dft = 8
elif vs_thd_init > 16 :
	if vs_thd_init <= 32 :
		vs_thd_dft = vs_thd_init // 2
		if vs_thd_dft % 2 != 0 :
			vs_thd_dft = vs_thd_dft - 1
	else :
		vs_thd_dft = 16
else :
	vs_thd_dft = vs_thd_init

vs_api = vs.__api_version__.api_major
if vs_api < 4 :
	raise ImportError("帧服务器 VapourSynth 的版本号过低，至少 R57")

core = vs.core
dfttest2 = None
nnedi3_resample = None
qtgmc = None
vsmlrt = None
onnx = None

import typing
import math
import fractions

##################################################
## 格式转换 # TODO
##################################################

def FMT_CHANGE(
	input : vs.VideoNode,
	fmtc : bool = False, # TODO
	algo : typing.Literal[1, 2, 3, 4] = 1,
	param_a : float = 0.0,
	param_b : float = 0.0,
	w_out : int = 0,
	h_out : int = 0,
	fmt_pix : typing.Literal[-1, 0, 1, 2, 3] = -1,
	dither : typing.Literal[0, 1, 2, 3] = 0,
	vs_t : int = vs_thd_dft,
) -> vs.VideoNode :

	func_name = "FMT_CHANGE"
	if not isinstance(input, vs.VideoNode) :
		raise vs.Error(f"模块 {func_name} 的子参数 input 的值无效")
	if not isinstance(fmtc, bool) :
		raise vs.Error(f"模块 {func_name} 的子参数 fmtc 的值无效")
	if algo not in [1, 2, 3, 4] :
		raise vs.Error(f"模块 {func_name} 的子参数 algo 的值无效")
	if not isinstance(param_a, (int, float)) or not isinstance(param_b, (int, float)) :
		raise vs.Error(f"模块 {func_name} 的子参数 param_a 或 param_b 的值无效")
	if not isinstance(w_out, int) or not isinstance(h_out, int) :
		raise vs.Error(f"模块 {func_name} 的子参数 w_out 或 h_out 的值无效")
	if isinstance(w_out, int) and isinstance(h_out, int) :
		if w_out < 0 or h_out < 0 :
			raise vs.Error(f"模块 {func_name} 的子参数 w_out 或 h_out 的值无效")
	if fmt_pix not in [-1, 0, 1, 2, 3] :
		raise vs.Error(f"模块 {func_name} 的子参数 fmt_pix 的值无效")
	if dither not in [0, 1, 2, 3] :
		raise vs.Error(f"模块 {func_name} 的子参数 dither 的值无效")
	if not isinstance(vs_t, int) or vs_t > vs_thd_init :
		raise vs.Error(f"模块 {func_name} 的子参数 vs_t 的值无效")

	core.num_threads = vs_t
	fmt_in = input.format.id
	algo_val = ["Bilinear", "Bicubic", "Lanczos", "Spline36"][algo - 1]
	resizer = getattr(core.resize, algo_val)
	if fmt_pix > 0 :
		fmt_pix_val = [vs.YUV420P8, vs.YUV420P10, vs.YUV444P16][fmt_pix - 1]
		fmt_out = fmt_pix_val
	elif fmt_pix == 0 :
		fmt_out = fmt_in
		if fmt_in not in [vs.YUV420P8, vs.YUV420P10] :
			fmt_out = vs.YUV420P10
	dither_val = ["none", "ordered", "random", "error_diffusion"][dither]

	output = resizer(clip=input, width=w_out if w_out else None, height=h_out if h_out else None, filter_param_a=param_a, filter_param_b=param_b, format=fmt_pix_val if fmt_pix >= 0 else None, dither_type=dither_val)

	return output

##################################################
## 限制输出的格式与高度
##################################################

def FMT_CTRL(
	input : vs.VideoNode,
	h_max : int = 0,
	h_ret : bool = False,
	spl_b : float = 1/3, # TODO 替换为 FMT_CHANGE
	spl_c : float = 1/3,
	fmt_pix : typing.Literal[0, 1, 2, 3] = 0,
	vs_t : int = vs_thd_dft,
) -> vs.VideoNode :

	func_name = "FMT_CTRL"
	if not isinstance(input, vs.VideoNode) :
		raise vs.Error(f"模块 {func_name} 的子参数 input 的值无效")
	if not isinstance(h_max, int) or h_max < 0 :
		raise vs.Error(f"模块 {func_name} 的子参数 h_max 的值无效")
	if not isinstance(h_ret, bool) :
		raise vs.Error(f"模块 {func_name} 的子参数 h_ret 的值无效")
	if not isinstance(spl_b, (int, float)) :
		raise vs.Error(f"模块 {func_name} 的子参数 spl_b 的值无效")
	if not isinstance(spl_c, (int, float)) :
		raise vs.Error(f"模块 {func_name} 的子参数 spl_c 的值无效")
	if fmt_pix not in [0, 1, 2, 3] :
		raise vs.Error(f"模块 {func_name} 的子参数 fmt_pix 的值无效")
	if not isinstance(vs_t, int) or vs_t > vs_thd_init :
		raise vs.Error(f"模块 {func_name} 的子参数 vs_t 的值无效")

	core.num_threads = vs_t
	fmt_src = input.format
	fmt_in = fmt_src.id
	spl_b, spl_c = float(spl_b), float(spl_c)
	w_in, h_in = input.width, input.height
	# https://github.com/mpv-player/mpv/blob/master/video/filter/vf_vapoursynth.c
	fmt_mpv = [vs.RGB24, vs.YUV420P8, vs.YUV420P10, vs.YUV422P8, vs.YUV422P10, vs.YUV410P8, vs.YUV411P8, vs.YUV440P8, vs.YUV444P8, vs.YUV444P10]
	fmt_pass = [vs.YUV420P8, vs.YUV420P10, vs.YUV444P16]
	fmt_safe = [vs.YUV444P8, vs.YUV444P10, vs.YUV444P16]

	if fmt_pix :
		fmt_pix_val = fmt_pass[fmt_pix - 1]
		fmt_out = fmt_pix_val
		if fmt_out == fmt_in :
			clip = input
		else :
			if (fmt_out not in fmt_safe) and (fmt_in in fmt_safe) :
				if not (w_in % 2 == 0) :
					w_in = w_in - 1
				if not (h_in % 2 == 0) :
					h_in = h_in - 1
				clip = core.resize.Bicubic(clip=input, width=w_in, height=h_in, filter_param_a=spl_b, filter_param_b=spl_c, format=fmt_out)
			else :
				clip = core.resize.Bilinear(clip=input, format=fmt_out)
	else :
		if fmt_in not in fmt_mpv :
			fmt_out = vs.YUV420P10
			if (fmt_out not in fmt_safe) and (fmt_in in fmt_safe) :
				if not (w_in % 2 == 0) :
					w_in = w_in - 1
				if not (h_in % 2 == 0) :
					h_in = h_in - 1
				clip = core.resize.Bicubic(clip=input, width=w_in, height=h_in, filter_param_a=spl_b, filter_param_b=spl_c, format=fmt_out)
			else :
				clip = core.resize.Bilinear(clip=input, format=fmt_out)
		else :
			fmt_out = fmt_in
			clip = input

	if h_max :
		if h_in > h_max :
			if h_ret :
				raise Exception("源高度超过限制的范围，已临时中止。")
			else :
				w_ds = w_in * (h_max / h_in)
				h_ds = h_max
				if fmt_src.subsampling_w or fmt_src.subsampling_h :
					if not (w_ds % 2 == 0) :
						w_ds = math.floor(w_ds / 2) * 2
					if not (h_ds % 2 == 0) :
						h_ds = math.floor(h_ds / 2) * 2

	if not h_max and not fmt_pix :
		output = clip
	elif h_max and not fmt_pix :
		if h_max >= h_in :
			output = clip
		else :
			output = core.resize.Bicubic(clip=clip, width=w_ds, height=h_ds, filter_param_a=spl_b, filter_param_b=spl_c)
	elif not h_max and fmt_pix :
		if fmt_pix_val == fmt_out :
			output = clip
		else :
			output = core.resize.Bilinear(clip=clip, format=fmt_pix_val)
	else :
		if h_max >= h_in :
			if fmt_pix_val == fmt_out :
				output = clip
			else :
				output = core.resize.Bilinear(clip=clip, format=fmt_pix_val)
		else :
			if fmt_pix_val == fmt_out :
				output = core.resize.Bicubic(clip=clip, width=w_ds, height=h_ds, filter_param_a=spl_b, filter_param_b=spl_c)
			else :
				output = core.resize.Bicubic(clip=clip, width=w_ds, height=h_ds, filter_param_a=spl_b, filter_param_b=spl_c)

	return output

##################################################
## PORT adjust (a3af7cb57cb37747b0667346375536e65b1fed17)
## 均衡器 # helper
##################################################

def EQ(
	input : vs.VideoNode,
	hue : typing.Optional[float] = None,
	sat : typing.Optional[float] = None,
	bright : typing.Optional[float] = None,
	cont : typing.Optional[float] = None,
	coring : bool = True,
	vs_t : int = vs_thd_dft,
) -> vs.VideoNode :

	core.num_threads = vs_t
	fmt_src = input.format
	fmt_cf_in = fmt_src.color_family
	fmt_bit_in = fmt_src.bits_per_sample

	if hue is not None or sat is not None :
		hue = 0.0 if hue is None else hue
		sat = 1.0 if sat is None else sat
		hue = hue * math.pi / 180.0
		hue_sin = math.sin(hue)
		hue_cos = math.cos(hue)
		gray = 128 << (fmt_bit_in - 8)
		chroma_min = 0
		chroma_max = (2 ** fmt_bit_in) - 1
		if coring:
			chroma_min = 16 << (fmt_bit_in - 8)
			chroma_max = 240 << (fmt_bit_in - 8)
		expr_u = "x {} - {} * y {} - {} * + {} + {} max {} min".format(gray, hue_cos * sat, gray, hue_sin * sat, gray, chroma_min, chroma_max)
		expr_v = "y {} - {} * x {} - {} * - {} + {} max {} min".format(gray, hue_cos * sat, gray, hue_sin * sat, gray, chroma_min, chroma_max)
		src_u = input.std.ShufflePlanes(planes=1, colorfamily=vs.GRAY)
		src_v = input.std.ShufflePlanes(planes=2, colorfamily=vs.GRAY)
		dst_u = core.std.Expr(clips=[src_u, src_v], expr=expr_u)
		dst_v = core.std.Expr(clips=[src_u, src_v], expr=expr_v)

		output = core.std.ShufflePlanes(clips=[input, dst_u, dst_v], planes=[0, 0, 0], colorfamily=fmt_cf_in)

	if bright is not None or cont is not None :
		bright = 0.0 if bright is None else bright
		cont = 1.0 if cont is None else cont
		luma_lut = []
		luma_min = 0
		luma_max = (2 ** fmt_bit_in) - 1
		if coring :
			luma_min = 16 << (fmt_bit_in - 8)
			luma_max = 235 << (fmt_bit_in - 8)
		for i in range(2 ** fmt_bit_in) :
			val = int((i - luma_min) * cont + bright + luma_min + 0.5)
			luma_lut.append(min(max(val, luma_min), luma_max))

		output = input.std.Lut(planes=0, lut=luma_lut)

	return output

##################################################
## 提取高频层 # helper
##################################################

def LAYER_HIGH(
	input : vs.VideoNode,
	blur_m : typing.Literal[0, 1, 2] = 2,
	vs_t : int = vs_thd_dft,
) -> vs.VideoNode :

	core.num_threads = vs_t
	fmt_in = input.format.id

	if fmt_in == vs.YUV444P16 :
		cut0 = input
	else :
		cut0 = core.resize.Bilinear(clip=input, format=vs.YUV444P16)
	if blur_m == 0 :
		output_blur = cut0
		output_diff = None
	elif blur_m == 1 :
		blur = core.rgvs.RemoveGrain(clip=cut0, mode=20)
		blur = core.rgvs.RemoveGrain(clip=blur, mode=20)
		output_blur = core.rgvs.RemoveGrain(clip=blur, mode=20)
	elif blur_m == 2 :
		blur = core.std.Convolution(clip=cut0, matrix=[1, 1, 1, 1, 1, 1, 1, 1, 1])
		blur = core.std.Convolution(clip=blur, matrix=[1, 1, 1, 1, 1, 1, 1, 1, 1])
		output_blur = core.std.Convolution(clip=blur, matrix=[1, 1, 1, 1, 1, 1, 1, 1, 1])

	if blur_m :
		output_diff = core.std.MakeDiff(clipa=cut0, clipb=blur)

	return output_blur, output_diff

##################################################
## 提取线条 # helper
##################################################

def LINE_MASK(
	input : vs.VideoNode,
	cpu : bool = True,
	gpu : typing.Literal[-1, 0, 1, 2] = -1,
	plane : typing.List[int] = [0],
	vs_t : int = vs_thd_dft,
) -> vs.VideoNode :

	core.num_threads = vs_t

	if cpu : # r13+
		output = core.tcanny.TCanny(clip=input, sigma=1.5, t_h=8.0, t_l=1.0, mode=0, op=1, planes=plane)
	else : # r12
		output = core.tcanny.TCannyCL(clip=input, sigma=1.5, t_h=8.0, t_l=1.0, mode=0, op=1, device=gpu, planes=plane)

	return output

##################################################
## 分离平面 # helper
##################################################

def PLANE_EXTR(
	input : vs.VideoNode,
	vs_t : int = vs_thd_dft,
) -> vs.VideoNode :

	core.num_threads = vs_t

	''' obs
	output = []
	for plane in range(input.format.num_planes) :
		clips = core.std.ShufflePlanes(clips=input, planes=plane, colorfamily=vs.GRAY)
		output.append(clips)
	'''

	output = core.std.SplitPlanes(clip=input)

	return output

##################################################
## 动态范围修正 # helper
##################################################

def RANGE_CHANGE(
	input : vs.VideoNode,
	l2f : bool = True,
	vs_t : int = vs_thd_dft,
) -> vs.VideoNode :

	core.num_threads = vs_t
	fmt_in = input.format.id
	
	cut0 = input
	if fmt_in in [vs.YUV420P8, vs.YUV422P8, vs.YUV410P8, vs.YUV411P8, vs.YUV440P8, vs.YUV444P8] :
		lv_val_pre = 0
	elif fmt_in in [vs.YUV420P10, vs.YUV422P10, vs.YUV444P10] :
		lv_val_pre = 1
	elif fmt_in in [vs.YUV420P16, vs.YUV422P16, vs.YUV444P16] :
		lv_val_pre = 2
	else :
		cut0 = core.resize.Bilinear(format=vs.YUV444P16)
		lv_val_pre = 2
	
	lv_val1 = [16, 64, 4096][lv_val_pre]
	lv_val2 = [235, 940, 60160][lv_val_pre]
	lv_val2_alt = [240, 960, 61440][lv_val_pre]
	lv_val3 = 0
	lv_val4 = [255, 1023, 65535][lv_val_pre]
	if l2f :
		cut1 = core.std.Levels(clip=cut0, min_in=lv_val1, max_in=lv_val2, min_out=lv_val3, max_out=lv_val4, planes=0)
		output = core.std.Levels(clip=cut1, min_in=lv_val1, max_in=lv_val2_alt, min_out=lv_val3, max_out=lv_val4, planes=[1,2])
	else :
		cut1 = core.std.Levels(clip=cut0, min_in=lv_val3, max_in=lv_val4, min_out=lv_val1, max_out=lv_val2, planes=0)
		output = core.std.Levels(clip=cut1, min_in=lv_val3, max_in=lv_val4, min_out=lv_val1, max_out=lv_val2_alt, planes=[1,2])

	return output

##################################################
## 解析ONNX # helper
##################################################

def ONNX_ANZ(
	input : str = "",
	check_mdl : bool = True,
) :

	func_name = "ONNX_ANZ"
	global onnx
	if onnx is None :
		try :
			import onnx
		except ImportError :
			raise ImportError(f"模块 {func_name} 依赖错误：缺失库 onnx")
	from onnx.checker import ValidationError

	if check_mdl :
		model_path = input
		try:
			onnx.checker.check_model(model_path)
		except ValidationError as e:
			print(f"模型无效，错误信息: {e}")
		except Exception as e:
			print(f"其他错误: {e}")

		input_info = onnx.load(model_path).graph.input[0]
		input_info = input_info.type.tensor_type
		elem_type = input_info.elem_type  ## 10➡️FP16 或 1➡️FP32
		#shape = input_info.shape[0]

	return elem_type

##################################################
## MOD HAvsFunc (e1fcce2b4645ed4acde9192606d00bcac1b5c9e5)
## 变更源帧率
##################################################

def FPS_CHANGE(
	input : vs.VideoNode,
	fps_in : float = 24.0,
	fps_out : float = 60.0,
	vs_t : int = vs_thd_dft,
) -> vs.VideoNode :

	func_name = "FPS_CHANGE"
	if not isinstance(input, vs.VideoNode) :
		raise vs.Error(f"模块 {func_name} 的子参数 input 的值无效")
	if not isinstance(fps_in, (int, float)) or fps_in <= 0.0 :
		raise vs.Error(f"模块 {func_name} 的子参数 fps_in 的值无效")
	if not isinstance(fps_out, (int, float)) or fps_out <= 0.0 or fps_out == fps_in :
		raise vs.Error(f"模块 {func_name} 的子参数 fps_out 的值无效")
	if not isinstance(vs_t, int) or vs_t > vs_thd_init :
		raise vs.Error(f"模块 {func_name} 的子参数 vs_t 的值无效")

	core.num_threads = vs_t

	def _ChangeFPS(clip: vs.VideoNode, fpsnum: int, fpsden: int = 1) -> vs.VideoNode :
		factor = (fpsnum / fpsden) * (clip.fps_den / clip.fps_num)
		def _frame_adjuster(n: int) -> vs.VideoNode :
			real_n = math.floor(n / factor)
			one_frame_clip = clip[real_n] * (len(clip) + 100)
			return one_frame_clip
		attribute_clip = clip.std.BlankClip(length=math.floor(len(clip) * factor), fpsnum=fpsnum, fpsden=fpsden)
		return attribute_clip.std.FrameEval(eval=_frame_adjuster)

	src = core.std.AssumeFPS(clip=input, fpsnum=fps_in * 1e6, fpsden=1e6)
	fin = _ChangeFPS(clip=src, fpsnum=fps_out * 1e6, fpsden=1e6)
	output = core.std.AssumeFPS(clip=fin, fpsnum=fps_out * 1e6, fpsden=1e6)

	return output

##################################################
## 限制源帧率
##################################################

def FPS_CTRL(
	input : vs.VideoNode,
	fps_in : float = 23.976,
	fps_max : float = 32.0,
	fps_out : typing.Optional[str] = None,
	fps_ret : bool = False,
	vs_t : int = vs_thd_dft,
) -> vs.VideoNode :

	func_name = "FPS_CTRL"
	if not isinstance(input, vs.VideoNode) :
		raise vs.Error(f"模块 {func_name} 的子参数 input 的值无效")
	if not isinstance(fps_in, (int, float)) or fps_in <= 0.0 :
		raise vs.Error(f"模块 {func_name} 的子参数 fps_in 的值无效")
	if fps_out is not None :
		if not isinstance(fps_out, (int, float)) or fps_out <= 0.0 :
			raise vs.Error(f"模块 {func_name} 的子参数 fps_out 的值无效")
	if not isinstance(fps_ret, bool) :
		raise vs.Error(f"模块 {func_name} 的子参数 fps_ret 的值无效")
	if not isinstance(vs_t, int) or vs_t > vs_thd_init :
		raise vs.Error(f"模块 {func_name} 的子参数 vs_t 的值无效")

	core.num_threads = vs_t

	if fps_in > fps_max :
		if fps_ret :
			raise Exception("源帧率超过限制的范围，已临时中止。")
		else :
			output = FPS_CHANGE(input=input, fps_in=fps_in, fps_out=fps_out if fps_out else fps_max)
	else :
		output = input

	return output

##################################################
## ACNet放大
##################################################

def ACNET_STD(
	input : vs.VideoNode,
	nr : typing.Literal[0, 1] = 1,
	nr_lv : typing.Literal[1, 2, 3] = 1,
	gpu : typing.Literal[0, 1, 2] = 0,
	gpu_m : typing.Literal[1, 2] = 1,
	vs_t : int = vs_thd_dft,
) -> vs.VideoNode :

	func_name = "ACNET_STD"
	if not isinstance(input, vs.VideoNode) :
		raise vs.Error(f"模块 {func_name} 的子参数 input 的值无效")
	if nr not in [0, 1] :
		raise vs.Error(f"模块 {func_name} 的子参数 nr 的值无效")
	if nr_lv not in [1, 2, 3] :
		raise vs.Error(f"模块 {func_name} 的子参数 nr_lv 的值无效")
	if gpu not in [0, 1, 2] :
		raise vs.Error(f"模块 {func_name} 的子参数 gpu 的值无效")
	if gpu_m not in [1, 2] :
		raise vs.Error(f"模块 {func_name} 的子参数 gpu_m 的值无效")
	if not isinstance(vs_t, int) or vs_t > vs_thd_init :
		raise vs.Error(f"模块 {func_name} 的子参数 vs_t 的值无效")

	if not hasattr(core, "anime4kcpp") :
		raise ModuleNotFoundError(f"模块 {func_name} 依赖错误：缺失插件，检查项目 anime4kcpp")

	core.num_threads = vs_t
	fmt_in = input.format.id

	if fmt_in == vs.YUV444P16 :
		cut0 = input
	else :
		cut0 = core.resize.Bilinear(clip=input, format=vs.YUV444P16)
	cut1 = core.anime4kcpp.Anime4KCPP(src=cut0, zoomFactor=2, ACNet=1, GPUMode=1, GPGPUModel="opencl" if gpu_m==1 else "cuda", HDN=nr, HDNLevel=nr_lv, platformID=gpu, deviceID=gpu)
	output = core.resize.Bilinear(clip=cut1, format=fmt_in)

	return output

##################################################
## ArtCNN放大 TensorRT
##################################################

def ARTCNN_NV(
	input : vs.VideoNode,
	lt_hd : bool = False,
	model : typing.Literal[6, 7, 8] = 8,
	gpu : typing.Literal[0, 1, 2] = 0,
	gpu_t : int = 2,
	st_eng : bool = False,
	ws_size : int = 0,
	vs_t : int = vs_thd_dft,
) -> vs.VideoNode :

	func_name = "ARTCNN_NV"
	if not isinstance(input, vs.VideoNode) :
		raise vs.Error(f"模块 {func_name} 的子参数 input 的值无效")
	if not isinstance(lt_hd, bool) :
		raise vs.Error(f"模块 {func_name} 的子参数 lt_hd 的值无效")
	if model not in [6, 7, 8] :
		raise vs.Error(f"模块 {func_name} 的子参数 model 的值无效")
	if gpu not in [0, 1, 2] :
		raise vs.Error(f"模块 {func_name} 的子参数 gpu 的值无效")
	if not isinstance(gpu_t, int) or gpu_t <= 0 :
		raise vs.Error(f"模块 {func_name} 的子参数 gpu_t 的值无效")
	if not isinstance(st_eng, bool) :
		raise vs.Error(f"模块 {func_name} 的子参数 st_eng 的值无效")
	if not isinstance(ws_size, int) or ws_size < 0 :
		raise vs.Error(f"模块 {func_name} 的子参数 ws_size 的值无效")
	if not isinstance(vs_t, int) or vs_t > vs_thd_init :
		raise vs.Error(f"模块 {func_name} 的子参数 vs_t 的值无效")

	if not hasattr(core, "trt") :
		raise ModuleNotFoundError(f"模块 {func_name} 依赖错误：缺失插件，检查项目 trt")

	plg_dir = os.path.dirname(core.trt.Version()["path"]).decode()
	mdl_fname = ["ArtCNN_R16F96", "ArtCNN_R8F64", "ArtCNN_R8F64_DS"][[6, 7, 8].index(model)]
	mdl_pth = plg_dir + "/models/ArtCNN/" + mdl_fname + ".onnx"
	if not os.path.exists(mdl_pth) :
		raise vs.Error(f"模块 {func_name} 所请求的模型缺失")

	global vsmlrt
	if vsmlrt is None :
		try :
			import vsmlrt
		except ImportError :
			raise ImportError(f"模块 {func_name} 依赖错误：缺失脚本 vsmlrt")
	if LooseVersion(vsmlrt.__version__) < LooseVersion("3.21.13") :
		raise ImportError(f"模块 {func_name} 依赖错误：缺失脚本 vsmlrt 的版本号过低，至少 3.21.13")

	core.num_threads = vs_t
	w_in, h_in = input.width, input.height
	size_in = w_in * h_in
	colorlv = getattr(input.get_frame(0).props, "_ColorRange", 0)
	fmt_in = input.format.id

	if (not lt_hd and (size_in > 1280 * 720)) or (size_in > 2048 * 1080) :
		raise Exception("源分辨率超过限制的范围，已临时中止。")
	if not st_eng and (((w_in > 2048) or (h_in > 1080)) or ((w_in < 64) or (h_in < 64))) :
		raise Exception("源分辨率不属于动态引擎支持的范围，已临时中止。")

	cut0 = core.resize.Bilinear(clip=input, format=vs.YUV444PH)

	cut0_y = core.std.ShufflePlanes(clips=cut0, planes=0, colorfamily=vs.GRAY)
	cut1_y = vsmlrt.ArtCNN(clip=cut0_y, model=model, backend=vsmlrt.BackendV2.TRT(
		num_streams=gpu_t, force_fp16=True, output_format=1,
		workspace=None if ws_size < 128 else (ws_size if st_eng else ws_size * 2),
		use_cuda_graph=True, use_cublas=False, use_cudnn=False,
		static_shape=st_eng, min_shapes=[0, 0] if st_eng else [384, 384],
		opt_shapes=None if st_eng else ([1920, 1080] if lt_hd else [1280, 720]), max_shapes=None if st_eng else ([2048, 1080] if lt_hd else [1280, 720]),
		device_id=gpu, short_path=True))
	cut1_uv = core.resize.Bilinear(clip=cut0, width=cut1_y.width, height=cut1_y.height)
	cut2 = core.std.ShufflePlanes(clips=[cut1_y, cut1_uv], planes=[0, 1, 2], colorfamily=vs.YUV)
	output = core.resize.Bilinear(clip=cut2, format=fmt_in)

	return output

##################################################
## Real-CUGAN放大
##################################################

def CUGAN_NV(
	input : vs.VideoNode,
	lt_hd : bool = False,
	nr_lv : typing.Literal[-1, 0, 3] = -1,
	sharp_lv : float = 1.0,
	gpu : typing.Literal[0, 1, 2] = 0,
	gpu_t : int = 2,
	st_eng : bool = False,
	ws_size : int = 0,
	vs_t : int = vs_thd_dft,
) -> vs.VideoNode :

	func_name = "CUGAN_NV"
	if not isinstance(input, vs.VideoNode) :
		raise vs.Error(f"模块 {func_name} 的子参数 input 的值无效")
	if not isinstance(lt_hd, bool) :
		raise vs.Error(f"模块 {func_name} 的子参数 lt_hd 的值无效")
	if nr_lv not in [-1, 0, 3] :
		raise vs.Error(f"模块 {func_name} 的子参数 nr_lv 的值无效")
	if not isinstance(sharp_lv, (int, float)) or sharp_lv < 0.0 or sharp_lv > 2.0 :
		raise vs.Error(f"模块 {func_name} 的子参数 sharp_lv 的值无效")
	if gpu not in [0, 1, 2] :
		raise vs.Error(f"模块 {func_name} 的子参数 gpu 的值无效")
	if not isinstance(gpu_t, int) or gpu_t <= 0 :
		raise vs.Error(f"模块 {func_name} 的子参数 gpu_t 的值无效")
	if not isinstance(st_eng, bool) :
		raise vs.Error(f"模块 {func_name} 的子参数 st_eng 的值无效")
	if not isinstance(ws_size, int) or ws_size < 0 :
		raise vs.Error(f"模块 {func_name} 的子参数 ws_size 的值无效")
	if not isinstance(vs_t, int) or vs_t > vs_thd_init :
		raise vs.Error(f"模块 {func_name} 的子参数 vs_t 的值无效")

	if not hasattr(core, "trt") :
		raise ModuleNotFoundError(f"模块 {func_name} 依赖错误：缺失插件，检查项目 trt")

	plg_dir = os.path.dirname(core.trt.Version()["path"]).decode()
	mdl_fname = ["pro-no-denoise3x-up2x", "pro-conservative-up2x", "pro-denoise3x-up2x"][[-1, 0, 3].index(nr_lv)]
	mdl_pth = plg_dir + "/models/cugan/" + mdl_fname + ".onnx"
	if not os.path.exists(mdl_pth) :
		raise vs.Error(f"模块 {func_name} 所请求的模型缺失")

	global vsmlrt
	if vsmlrt is None :
		try :
			import vsmlrt
		except ImportError :
			raise ImportError(f"模块 {func_name} 依赖错误：缺失脚本 vsmlrt")
	if LooseVersion(vsmlrt.__version__) < LooseVersion("3.18.1") :
		raise ImportError(f"模块 {func_name} 依赖错误：缺失脚本 vsmlrt 版本号过低，至少 3.18.1")

	core.num_threads = vs_t
	w_in, h_in = input.width, input.height
	size_in = w_in * h_in
	colorlv = getattr(input.get_frame(0).props, "_ColorRange", 0)
	fmt_in = input.format.id

	if (not lt_hd and (size_in > 1280 * 720)) or (size_in > 2048 * 1080) :
		raise Exception("源分辨率超过限制的范围，已临时中止。")
	if not st_eng and (((w_in > 2048) or (h_in > 1080)) or ((w_in < 64) or (h_in < 64))) :
		raise Exception("源分辨率不属于动态引擎支持的范围，已临时中止。")

	cut1 = core.resize.Bilinear(clip=input, format=vs.RGBH, matrix_in_s="709")
	cut2 = vsmlrt.CUGAN(clip=cut1, noise=nr_lv, scale=2, alpha=sharp_lv, version=2, backend=vsmlrt.BackendV2.TRT(
		num_streams=gpu_t, force_fp16=True, output_format=1,
		workspace=None if ws_size < 128 else (ws_size if st_eng else ws_size * 2),
		use_cuda_graph=True, use_cublas=False, use_cudnn=False,
		static_shape=st_eng, min_shapes=[0, 0] if st_eng else [384, 384],
		opt_shapes=None if st_eng else ([1920, 1080] if lt_hd else [1280, 720]), max_shapes=None if st_eng else ([2048, 1080] if lt_hd else [1280, 720]),
		device_id=gpu, short_path=True))
	output = core.resize.Bilinear(clip=cut2, format=fmt_in, matrix_s="709", range=1 if colorlv==0 else None)

	return output

##################################################
## NNEDI3放大
##################################################

def EDI_US_STD(
	input : vs.VideoNode,
	ext_proc : bool = True,
	nsize : typing.Literal[0, 4] = 4,
	nns : typing.Literal[2, 3, 4] = 3,
	cpu : bool = True,
	gpu : typing.Literal[-1, 0, 1, 2] = -1,
	vs_t : int = vs_thd_dft,
) -> vs.VideoNode :

	func_name = "EDI_US_STD"
	if not isinstance(input, vs.VideoNode) :
		raise vs.Error(f"模块 {func_name} 的子参数 input 的值无效")
	if not isinstance(ext_proc, bool) :
		raise vs.Error(f"模块 {func_name} 的子参数 ext_proc 的值无效")
	if nsize not in [0, 4] :
		raise vs.Error(f"模块 {func_name} 的子参数 nsize 的值无效")
	if nns not in [2, 3, 4] :
		raise vs.Error(f"模块 {func_name} 的子参数 nns 的值无效")
	if not isinstance(cpu, bool) :
		raise vs.Error(f"模块 {func_name} 的子参数 cpu 的值无效")
	if gpu not in [-1, 0, 1, 2] :
		raise vs.Error(f"模块 {func_name} 的子参数 gpu 的值无效")
	if not isinstance(vs_t, int) or vs_t > vs_thd_init :
		raise vs.Error(f"模块 {func_name} 的子参数 vs_t 的值无效")

	if not hasattr(core, "fmtc") :
		raise ModuleNotFoundError(f"模块 {func_name} 依赖错误：缺失插件，检查项目 fmtc")
	if cpu :
		if not hasattr(core, "znedi3") :
			raise ModuleNotFoundError(f"模块 {func_name} 依赖错误：缺失插件，检查项目 znedi3")
	else :
		if not hasattr(core, "nnedi3cl") :
			raise ModuleNotFoundError(f"模块 {func_name} 依赖错误：缺失插件，检查项目 nnedi3cl")

	global nnedi3_resample
	if nnedi3_resample is None :
		try :
			import nnedi3_resample
		except ImportError :
			raise ImportError(f"模块 {func_name} 依赖错误：缺失脚本 nnedi3_resample")
	if LooseVersion(nnedi3_resample.__version__) < LooseVersion("2") :
		raise ImportError(f"模块 {func_name} 依赖错误：缺失脚本 nnedi3_resample 的版本号过低，至少 2")

	core.num_threads = vs_t

	if ext_proc :
		fmt_in = input.format.id
		if fmt_in in [vs.YUV410P8, vs.YUV420P8, vs.YUV420P10] :
			clip = core.resize.Bilinear(clip=input, format=vs.YUV420P16)
		elif fmt_in in [vs.YUV411P8, vs.YUV422P8, vs.YUV422P10] :
			clip = core.resize.Bilinear(clip=input, format=vs.YUV422P16)
		elif fmt_in == vs.YUV444P16 :
			clip = input
		else :
			clip = core.resize.Bilinear(clip=input, format=vs.YUV444P16)
	else :
		clip = input

	output = nnedi3_resample.nnedi3_resample(input=clip, target_width=input.width * 2, target_height=input.height * 2,
		nsize=nsize, nns=nns, qual=1, etype=0, pscrn=2, mode="znedi3" if cpu else "nnedi3cl", device=gpu)
	if ext_proc :
		output = core.resize.Bilinear(clip=output, format=fmt_in)

	return output

##################################################
## Real-ESRGAN放大
##################################################

def ESRGAN_DML(
	input : vs.VideoNode,
	lt_hd : bool = False,
	model : typing.Literal[0, 2, 5005, 5006, 5007, 5008, 5009, 5010] = 5005,
	gpu : typing.Literal[0, 1, 2] = 0,
	gpu_t : int = 2,
	vs_t : int = vs_thd_dft,
) -> vs.VideoNode :

	func_name = "ESRGAN_DML"
	if not isinstance(input, vs.VideoNode) :
		raise vs.Error(f"模块 {func_name} 的子参数 input 的值无效")
	if not isinstance(lt_hd, bool) :
		raise vs.Error(f"模块 {func_name} 的子参数 lt_hd 的值无效")
	if model not in [0, 2, 5005, 5006, 5007, 5008, 5009, 5010] :
		raise vs.Error(f"模块 {func_name} 的子参数 model 的值无效")
	if gpu not in [0, 1, 2] :
		raise vs.Error(f"模块 {func_name} 的子参数 gpu 的值无效")
	if not isinstance(gpu_t, int) or gpu_t <= 0 :
		raise vs.Error(f"模块 {func_name} 的子参数 gpu_t 的值无效")
	if not isinstance(vs_t, int) or vs_t > vs_thd_init :
		raise vs.Error(f"模块 {func_name} 的子参数 vs_t 的值无效")

	if not hasattr(core, "ort") :
		raise ModuleNotFoundError(f"模块 {func_name} 依赖错误：缺失插件，检查项目 ort")

	plg_dir = os.path.dirname(core.ort.Version()["path"]).decode()
	mdl_fname = ["RealESRGANv2-animevideo-xsx2", "realesr-animevideov3", "animejanaiV2L1", "animejanaiV2L2", "animejanaiV2L3", "animejanaiV3-HD-L1", "animejanaiV3-HD-L2", "animejanaiV3-HD-L3"][[0, 2, 5005, 5006, 5007, 5008, 5009, 5010].index(model)]
	mdl_pth = plg_dir + "/models/RealESRGANv2/" + mdl_fname + ".onnx"
	if not os.path.exists(mdl_pth) :
		raise vs.Error(f"模块 {func_name} 所请求的模型缺失")

	global vsmlrt
	if vsmlrt is None :
		try :
			import vsmlrt
		except ImportError :
			raise ImportError(f"模块 {func_name} 依赖错误：缺失脚本 vsmlrt")
	if LooseVersion(vsmlrt.__version__) < LooseVersion("3.15.47") :
		raise ImportError(f"模块 {func_name} 依赖错误：缺失脚本 vsmlrt 的版本号过低，至少 3.15.47")

	core.num_threads = vs_t
	w_in, h_in = input.width, input.height
	size_in = w_in * h_in
	colorlv = getattr(input.get_frame(0).props, "_ColorRange", 0)
	fmt_in = input.format.id

	if (not lt_hd and (size_in > 1280 * 720)) or (size_in > 2048 * 1080) :
		raise Exception("源分辨率超过限制的范围，已临时中止。")

	cut1 = core.resize.Bilinear(clip=input, format=vs.RGBS, matrix_in_s="709")
	cut2 = vsmlrt.RealESRGANv2(clip=cut1, scale=4 if model==2 else 2, model=model, backend=vsmlrt.BackendV2.ORT_DML(
		device_id=gpu, num_streams=gpu_t, fp16=True))
	output = core.resize.Bilinear(clip=cut2, format=fmt_in, matrix_s="709", range=1 if colorlv==0 else None)

	return output

##################################################
## Real-ESRGAN放大
##################################################

def ESRGAN_NV(
	input : vs.VideoNode,
	lt_hd : bool = False,
	model : typing.Literal[0, 2, 5005, 5006, 5007, 5008, 5009, 5010] = 5005,
	gpu : typing.Literal[0, 1, 2] = 0,
	gpu_t : int = 2,
	st_eng : bool = False,
	ws_size : int = 0,
	vs_t : int = vs_thd_dft,
) -> vs.VideoNode :

	func_name = "ESRGAN_NV"
	if not isinstance(input, vs.VideoNode) :
		raise vs.Error(f"模块 {func_name} 的子参数 input 的值无效")
	if not isinstance(lt_hd, bool) :
		raise vs.Error(f"模块 {func_name} 的子参数 lt_hd 的值无效")
	if model not in [0, 2, 5005, 5006, 5007, 5008, 5009, 5010] :
		raise vs.Error(f"模块 {func_name} 的子参数 model 的值无效")
	if gpu not in [0, 1, 2] :
		raise vs.Error(f"模块 {func_name} 的子参数 gpu 的值无效")
	if not isinstance(gpu_t, int) or gpu_t <= 0 :
		raise vs.Error(f"模块 {func_name} 的子参数 gpu_t 的值无效")
	if not isinstance(st_eng, bool) :
		raise vs.Error(f"模块 {func_name} 的子参数 st_eng 的值无效")
	if not isinstance(ws_size, int) or ws_size < 0 :
		raise vs.Error(f"模块 {func_name} 的子参数 ws_size 的值无效")
	if not isinstance(vs_t, int) or vs_t > vs_thd_init :
		raise vs.Error(f"模块 {func_name} 的子参数 vs_t 的值无效")

	if not hasattr(core, "trt") :
		raise ModuleNotFoundError(f"模块 {func_name} 依赖错误：缺失插件，检查项目 trt")

	plg_dir = os.path.dirname(core.trt.Version()["path"]).decode()
	mdl_fname = ["RealESRGANv2-animevideo-xsx2", "realesr-animevideov3", "animejanaiV2L1", "animejanaiV2L2", "animejanaiV2L3", "animejanaiV3-HD-L1", "animejanaiV3-HD-L2", "animejanaiV3-HD-L3"][[0, 2, 5005, 5006, 5007, 5008, 5009, 5010].index(model)]
	mdl_pth = plg_dir + "/models/RealESRGANv2/" + mdl_fname + ".onnx"
	if not os.path.exists(mdl_pth) :
		raise vs.Error(f"模块 {func_name} 所请求的模型缺失")

	global vsmlrt
	if vsmlrt is None :
		try :
			import vsmlrt
		except ImportError :
			raise ImportError(f"模块 {func_name} 依赖错误：缺失脚本 vsmlrt")
	if LooseVersion(vsmlrt.__version__) < LooseVersion("3.18.23") :
		raise ImportError(f"模块 {func_name} 依赖错误：缺失脚本 vsmlrt 的版本号过低，至少 3.18.23")

	core.num_threads = vs_t
	w_in, h_in = input.width, input.height
	size_in = w_in * h_in
	colorlv = getattr(input.get_frame(0).props, "_ColorRange", 0)
	fmt_in = input.format.id

	if (not lt_hd and (size_in > 1280 * 720)) or (size_in > 2048 * 1080) :
		raise Exception("源分辨率超过限制的范围，已临时中止。")
	if not st_eng and (((w_in > 2048) or (h_in > 1080)) or ((w_in < 64) or (h_in < 64))) :
		raise Exception("源分辨率不属于动态引擎支持的范围，已临时中止。")

	cut1 = core.resize.Bilinear(clip=input, format=vs.RGBH, matrix_in_s="709")
	cut2 = vsmlrt.RealESRGANv2(clip=cut1, scale=4 if model==2 else 2, model=model, backend=vsmlrt.BackendV2.TRT(
		num_streams=gpu_t, force_fp16=True, output_format=1,
		workspace=None if ws_size < 128 else (ws_size if st_eng else ws_size * 2),
		use_cuda_graph=True, use_cublas=False, use_cudnn=False,
		static_shape=st_eng, min_shapes=[0, 0] if st_eng else [384, 384],
		opt_shapes=None if st_eng else ([1920, 1080] if lt_hd else [1280, 720]), max_shapes=None if st_eng else ([2048, 1080] if lt_hd else [1280, 720]),
		device_id=gpu, short_path=True))
	output = core.resize.Bilinear(clip=cut2, format=fmt_in, matrix_s="709", range=1 if colorlv==0 else None)

	return output

##################################################
## NGU放大
##################################################

def NGU_HQ(
	input : vs.VideoNode,
	vs_t : int = vs_thd_dft,
) -> vs.VideoNode :

	func_name = "NGU_HQ"
	if not isinstance(input, vs.VideoNode) :
		raise vs.Error(f"模块 {func_name} 的子参数 input 的值无效")
	if not isinstance(vs_t, int) or vs_t > vs_thd_init :
		raise vs.Error(f"模块 {func_name} 的子参数 vs_t 的值无效")

	if not hasattr(core, "madvr") :
		raise ModuleNotFoundError(f"模块 {func_name} 依赖错误：缺失插件，检查项目 madvr")

	core.num_threads = vs_t
	w_in, h_in = input.width, input.height
	w_rs, h_rs = w_in * 2, h_in * 2
	colorlv = getattr(input.get_frame(0).props, "_ColorRange", 0)
	fmt_in = input.format.id

	mad_param = ["upscale(newWidth=%d,newHeight=%d,algo=nguAaHigh)" % (w_rs, h_rs), "setOutputFormat(format=yuv420,bitdepth=10)"]
	if fmt_in == vs.YUV420P10 :
		cut0 = input
	else :
		cut0 = core.resize.Bilinear(clip=input, format=vs.YUV420P10)
	output = core.madvr.Process(clip=cut0, commands=mad_param, adapter=False)
	if colorlv == 0 :
		output = core.resize.Bilinear(clip=output, range=1)

	return output

##################################################
## Waifu2x放大
##################################################

def WAIFU_DML(
	input : vs.VideoNode,
	lt_hd : bool = False,
	model : typing.Literal[3, 5, 6] = 3,
	nr_lv : typing.Literal[-1, 0, 1, 2, 3] = 1,
	gpu : typing.Literal[0, 1, 2] = 0,
	gpu_t : int = 2,
	vs_t : int = vs_thd_dft,
) -> vs.VideoNode :

	func_name = "WAIFU_DML"
	if not isinstance(input, vs.VideoNode) :
		raise vs.Error(f"模块 {func_name} 的子参数 input 的值无效")
	if not isinstance(lt_hd, bool) :
		raise vs.Error(f"模块 {func_name} 的子参数 lt_hd 的值无效")
	if model not in [3, 5, 6] :
		raise vs.Error(f"模块 {func_name} 的子参数 model 的值无效")
	if nr_lv not in [-1, 0, 1, 2, 3] :
		raise vs.Error(f"模块 {func_name} 的子参数 nr_lv 的值无效")
	if gpu not in [0, 1, 2] :
		raise vs.Error(f"模块 {func_name} 的子参数 gpu 的值无效")
	if not isinstance(gpu_t, int) or gpu_t <= 0 :
		raise vs.Error(f"模块 {func_name} 的子参数 gpu_t 的值无效")
	if not isinstance(vs_t, int) or vs_t > vs_thd_init :
		raise vs.Error(f"模块 {func_name} 的子参数 vs_t 的值无效")

	if not hasattr(core, "ort") :
		raise ModuleNotFoundError(f"模块 {func_name} 依赖错误：缺失插件，检查项目 ort")

	plg_dir = os.path.dirname(core.ort.Version()["path"]).decode()
	mdl_pname = {3:"upconv_7_anime_style_art_rgb/", 5:"upresnet10/", 6:"cunet/"}.get(model)
	mdl_fname = ["scale2.0x_model", "noise0_scale2.0x_model", "noise1_scale2.0x_model", "noise2_scale2.0x_model", "noise3_scale2.0x_model"][[-1, 0, 1, 2, 3].index(nr_lv)]
	mdl_pth = plg_dir + "/models/waifu2x/" + mdl_pname + mdl_fname + ".onnx"
	if not os.path.exists(mdl_pth) :
		raise vs.Error(f"模块 {func_name} 所请求的模型缺失")

	global vsmlrt
	if vsmlrt is None :
		try :
			import vsmlrt
		except ImportError :
			raise ImportError(f"模块 {func_name} 依赖错误：缺失脚本 vsmlrt")
	if LooseVersion(vsmlrt.__version__) < LooseVersion("3.15.25") :
		raise ImportError(f"模块 {func_name} 依赖错误：缺失脚本 vsmlrt 的版本号过低，至少 3.15.25")

	core.num_threads = vs_t
	w_in, h_in = input.width, input.height
	size_in = w_in * h_in
	colorlv = getattr(input.get_frame(0).props, "_ColorRange", 0)
	fmt_in = input.format.id

	if (not lt_hd and (size_in > 1280 * 720)) or (size_in > 2048 * 1080) :
		raise Exception("源分辨率超过限制的范围，已临时中止。")

	cut1 = core.resize.Bilinear(clip=input, format=vs.RGBS, matrix_in_s="709")
	cut2 = vsmlrt.Waifu2x(clip=cut1, noise=nr_lv, scale=2, model=model, backend=vsmlrt.BackendV2.ORT_DML(
		device_id=gpu, num_streams=gpu_t, fp16=True))
	output = core.resize.Bilinear(clip=cut2, format=fmt_in, matrix_s="709", range=1 if colorlv==0 else None)

	return output

##################################################
## Waifu2x放大
##################################################

def WAIFU_NV(
	input : vs.VideoNode,
	lt_hd : bool = False,
	model : typing.Literal[3, 5, 6] = 3,
	nr_lv : typing.Literal[-1, 0, 1, 2, 3] = 1,
	gpu : typing.Literal[0, 1, 2] = 0,
	gpu_t : int = 2,
	st_eng : bool = False,
	ws_size : int = 0,
	vs_t : int = vs_thd_dft,
) -> vs.VideoNode :

	func_name = "WAIFU_NV"
	if not isinstance(input, vs.VideoNode) :
		raise vs.Error(f"模块 {func_name} 的子参数 input 的值无效")
	if not isinstance(lt_hd, bool) :
		raise vs.Error(f"模块 {func_name} 的子参数 lt_hd 的值无效")
	if model not in [3, 5, 6] :
		raise vs.Error(f"模块 {func_name} 的子参数 model 的值无效")
	if nr_lv not in [-1, 0, 1, 2, 3] :
		raise vs.Error(f"模块 {func_name} 的子参数 nr_lv 的值无效")
	if gpu not in [0, 1, 2] :
		raise vs.Error(f"模块 {func_name} 的子参数 gpu 的值无效")
	if not isinstance(gpu_t, int) or gpu_t <= 0 :
		raise vs.Error(f"模块 {func_name} 的子参数 gpu_t 的值无效")
	if not isinstance(st_eng, bool) :
		raise vs.Error(f"模块 {func_name} 的子参数 st_eng 的值无效")
	if not isinstance(ws_size, int) or ws_size < 0 :
		raise vs.Error(f"模块 {func_name} 的子参数 ws_size 的值无效")
	if not isinstance(vs_t, int) or vs_t > vs_thd_init :
		raise vs.Error(f"模块 {func_name} 的子参数 vs_t 的值无效")

	if not hasattr(core, "trt") :
		raise ModuleNotFoundError(f"模块 {func_name} 依赖错误：缺失插件，检查项目 trt")

	plg_dir = os.path.dirname(core.trt.Version()["path"]).decode()
	mdl_pname = {3:"upconv_7_anime_style_art_rgb/", 5:"upresnet10/", 6:"cunet/"}.get(model)
	mdl_fname = ["scale2.0x_model", "noise0_scale2.0x_model", "noise1_scale2.0x_model", "noise2_scale2.0x_model", "noise3_scale2.0x_model"][[-1, 0, 1, 2, 3].index(nr_lv)]
	mdl_pth = plg_dir + "/models/waifu2x/" + mdl_pname + mdl_fname + ".onnx"
	if not os.path.exists(mdl_pth) :
		raise vs.Error(f"模块 {func_name} 所请求的模型缺失")

	global vsmlrt
	if vsmlrt is None :
		try :
			import vsmlrt
		except ImportError :
			raise ImportError(f"模块 {func_name} 依赖错误：缺失脚本 vsmlrt")
	if LooseVersion(vsmlrt.__version__) < LooseVersion("3.18.1") :
		raise ImportError(f"模块 {func_name} 依赖错误：缺失脚本 vsmlrt 的版本号过低，至少 3.18.1")

	core.num_threads = vs_t
	w_in, h_in = input.width, input.height
	size_in = w_in * h_in
	colorlv = getattr(input.get_frame(0).props, "_ColorRange", 0)
	fmt_in = input.format.id

	if (not lt_hd and (size_in > 1280 * 720)) or (size_in > 2048 * 1080) :
		raise Exception("源分辨率超过限制的范围，已临时中止。")
	if not st_eng and (((w_in > 2048) or (h_in > 1080)) or ((w_in < 64) or (h_in < 64))) :
		raise Exception("源分辨率不属于动态引擎支持的范围，已临时中止。")

	cut1 = core.resize.Bilinear(clip=input, format=vs.RGBH, matrix_in_s="709")
	cut2 = vsmlrt.Waifu2x(clip=cut1, noise=nr_lv, scale=2, model=model, backend=vsmlrt.BackendV2.TRT(
		num_streams=gpu_t, force_fp16=True, output_format=1,
		workspace=None if ws_size < 128 else (ws_size if st_eng else ws_size * 2),
		use_cuda_graph=True, use_cublas=False, use_cudnn=False,
		static_shape=st_eng, min_shapes=[0, 0] if st_eng else [384, 384],
		opt_shapes=None if st_eng else ([1920, 1080] if lt_hd else [1280, 720]), max_shapes=None if st_eng else ([2048, 1080] if lt_hd else [1280, 720]),
		device_id=gpu, short_path=True))
	output = core.resize.Bilinear(clip=cut2, format=fmt_in, matrix_s="709", range=1 if colorlv==0 else None)

	return output

##################################################
## MVtools补帧
##################################################

def MVT_LQ(
	input : vs.VideoNode,
	fps_in : float = 23.976,
	fps_out : float = 59.940,
	recal : bool = True,
	block : bool = True,
	vs_t : int = vs_thd_dft,
) -> vs.VideoNode :

	func_name = "MVT_LQ"
	if not isinstance(input, vs.VideoNode) :
		raise vs.Error(f"模块 {func_name} 的子参数 input 的值无效")
	if not isinstance(fps_in, (int, float)) or fps_in <= 0.0 :
		raise vs.Error(f"模块 {func_name} 的子参数 fps_in 的值无效")
	if not isinstance(fps_out, (int, float)) or fps_out <= 0.0 or fps_out <= fps_in :
		raise vs.Error(f"模块 {func_name} 的子参数 fps_out 的值无效")
	if not isinstance(recal, bool) :
		raise vs.Error(f"模块 {func_name} 的子参数 recal 的值无效")
	if not isinstance(block, bool) :
		raise vs.Error(f"模块 {func_name} 的子参数 block 的值无效")
	if not isinstance(vs_t, int) or vs_t > vs_thd_init :
		raise vs.Error(f"模块 {func_name} 的子参数 vs_t 的值无效")

	if not hasattr(core, "mv") :
		raise ModuleNotFoundError(f"模块 {func_name} 依赖错误：缺失插件，检查项目 mv")

	core.num_threads = vs_t
	w_in, h_in = input.width, input.height
	blk_size = 32
	w_tmp = math.ceil(w_in / blk_size) * blk_size - w_in
	h_tmp = math.ceil(h_in / blk_size) * blk_size - h_in
	if w_tmp + h_tmp > 0 :
		cut0 = core.std.AddBorders(clip=input, right=w_tmp, bottom=h_tmp)
	else :
		cut0 = input

	cut1 = core.std.AssumeFPS(clip=cut0, fpsnum=int(fps_in * 1e6), fpsden=1e6)
	cut_s = core.mv.Super(clip=cut1, pel=1, sharp=0)
	cut_b = core.mv.Analyse(super=cut_s, blksize=blk_size, search=2, isb=True)
	cut_f = core.mv.Analyse(super=cut_s, blksize=blk_size, search=2)

	if recal :
		cut_b = core.mv.Recalculate(super=cut_s, vectors=cut_b, thsad=200, blksize=blk_size / 2, search=2, searchparam=1)
		cut_f = core.mv.Recalculate(super=cut_s, vectors=cut_f, thsad=200, blksize=blk_size / 2, search=2, searchparam=1)
	else :
		cut_b, cut_f = cut_b, cut_f

	if block :
		output = core.mv.BlockFPS(clip=cut1, super=cut_s, mvbw=cut_b, mvfw=cut_f, num=fps_out * 1e6, den=1e6)
	else :
		output = core.mv.FlowFPS(clip=cut1, super=cut_s, mvbw=cut_b, mvfw=cut_f, num=fps_out * 1e6, den=1e6, mask=1)
	if w_tmp + h_tmp > 0 :
		output = core.std.Crop(clip=output, right=w_tmp, bottom=h_tmp)

	return output

##################################################
## MOD https://gist.github.com/KCCat/1b3a7b7f085a066af3719859f88ded02
## MVtools补帧
##################################################

def MVT_STD(
	input : vs.VideoNode,
	fps_in : float = 23.976,
	fps_out : float = 60.0,
	vs_t : int = vs_thd_dft,
) -> vs.VideoNode :

	func_name = "MVT_STD"
	if not isinstance(input, vs.VideoNode) :
		raise vs.Error(f"模块 {func_name} 的子参数 input 的值无效")
	if not isinstance(fps_in, (int, float)) or fps_in <= 0.0 :
		raise vs.Error(f"模块 {func_name} 的子参数 fps_in 的值无效")
	if not isinstance(fps_out, (int, float)) or fps_out <= 0.0 or fps_out <= fps_in :
		raise vs.Error(f"模块 {func_name} 的子参数 fps_out 的值无效")
	if not isinstance(vs_t, int) or vs_t > vs_thd_init :
		raise vs.Error(f"模块 {func_name} 的子参数 vs_t 的值无效")

	if not hasattr(core, "mv") :
		raise ModuleNotFoundError(f"模块 {func_name} 依赖错误：缺失插件，检查项目 mv")

	def _ffps(fps) :
		rfps = int('%.0f' % fps)
		if ( abs(fps - (rfps/1.001)) < abs(fps - (rfps/1.000)) ) :
			vfps, vden = rfps*1000, 1001
		else :
			vfps, vden = rfps*1000, 1000
		return vfps, vden
	vfps, vden = _ffps(fps_in)

	core.num_threads = vs_t
	w_in, h_in = input.width, input.height
	blk_size = 80
	w_tmp = math.ceil(w_in / blk_size) * blk_size - w_in
	h_tmp = math.ceil(h_in / blk_size) * blk_size - h_in
	if w_tmp + h_tmp > 0 :
		cut0 = core.std.AddBorders(clip=input, right=w_tmp, bottom=h_tmp)
	else :
		cut0 = input

	cut1 = core.std.AssumeFPS(clip=cut0, fpsnum=int(vfps), fpsden=vden)
	cut_s = core.mv.Super(clip=cut1, sharp=1, rfilter=4)
	cut_b = core.mv.Analyse(super=cut_s, blksize=64, searchparam=0, pelsearch=3, isb=True, lambda_=0, lsad=10000, overlapv=16, badrange=0, search_coarse=4)
	cut_f = core.mv.Analyse(super=cut_s, blksize=64, searchparam=0, pelsearch=3, lambda_=0, lsad=10000, overlapv=16, badrange=0, search_coarse=4)

	output = core.mv.BlockFPS(clip=cut1, super=cut_s, mvbw=cut_b, mvfw=cut_f, num=fps_out * 1000, den=vden, mode=2, thscd1=970, thscd2=255, blend=False)
	if w_tmp + h_tmp > 0 :
		output = core.std.Crop(clip=output, right=w_tmp, bottom=h_tmp)

	return output

##################################################
## MVtools补帧
##################################################

def MVT_POT(
	input : vs.VideoNode,
	fps_in : float = 23.976,
	fps_out : float = 59.940,
	vs_t : int = vs_thd_dft,
) -> vs.VideoNode :

	func_name = "MVT_POT"
	if not isinstance(input, vs.VideoNode) :
		raise vs.Error(f"模块 {func_name} 的子参数 input 的值无效")
	if not isinstance(fps_in, (int, float)) or fps_in <= 0.0 :
		raise vs.Error(f"模块 {func_name} 的子参数 fps_in 的值无效")
	if not isinstance(fps_out, (int, float)) or fps_out <= 0.0 or fps_out <= fps_in :
		raise vs.Error(f"模块 {func_name} 的子参数 fps_out 的值无效")
	if not isinstance(vs_t, int) or vs_t > vs_thd_init :
		raise vs.Error(f"模块 {func_name} 的子参数 vs_t 的值无效")

	if not hasattr(core, "mv") :
		raise ModuleNotFoundError(f"模块 {func_name} 依赖错误：缺失插件，检查项目 mv")

	core.num_threads = vs_t
	max_flow_width  = 1280
	max_flow_height = 720
	th_block_diff = 8*8*7
	th_flow_diff  = 8*8*7
	th_block_changed = 14
	th_flow_changed  = 14
	blocksize  = 2**4
	target_num = int(fps_out * 1e6)
	target_den = int(1e6)
	source_num = int(fps_in * 1e6)
	source_den = int(1e6)

	clip = core.std.AssumeFPS(input, fpsnum=source_num, fpsden=source_den)
	sup  = core.mv.Super(clip, pel=2, hpad=blocksize, vpad=blocksize)
	bv   = core.mv.Analyse(sup, blksize=blocksize, isb=True , chroma=True, search=3, searchparam=2)
	fv   = core.mv.Analyse(sup, blksize=blocksize, isb=False, chroma=True, search=3, searchparam=2)
	use_block = clip.width > max_flow_width or clip.height > max_flow_height

	if use_block :
		output = core.mv.BlockFPS(clip, sup, bv, fv, num=target_num, den=target_den, mode=3, thscd1=th_block_diff, thscd2=th_block_changed)
	else :
		output = core.mv.FlowFPS(clip, sup, bv, fv, num=target_num, den=target_den, mask=0, thscd1=th_flow_diff, thscd2=th_flow_changed)

	return output

##################################################
## MOD xvs (b24d5594206635f7373838acb80643d2ab141222)
## MVtools补帧
##################################################

def MVT_MQ(
	input : vs.VideoNode,
	fps_in : float = 23.976,
	fps_out : float = 59.940,
	qty_lv : typing.Literal[1, 2, 3] = 1,
	block : bool = True,
	blksize : typing.Literal[4, 8, 16, 32] = 8,
	thscd1 : int = 360,
	thscd2 : int = 80,
	vs_t : int = vs_thd_dft,
) -> vs.VideoNode :

	func_name = "MVT_MQ"
	if not isinstance(input, vs.VideoNode) :
		raise vs.Error(f"模块 {func_name} 的子参数 input 的值无效")
	if not isinstance(fps_in, (int, float)) or fps_in <= 0.0 :
		raise vs.Error(f"模块 {func_name} 的子参数 fps_in 的值无效")
	if not isinstance(fps_out, (int, float)) or fps_out <= 0.0 or fps_out <= fps_in :
		raise vs.Error(f"模块 {func_name} 的子参数 fps_out 的值无效")
	if qty_lv not in [1, 2, 3] :
		raise vs.Error(f"模块 {func_name} 的子参数 qty_lv 的值无效")
	if not isinstance(block, bool) :
		raise vs.Error(f"模块 {func_name} 的子参数 block 的值无效")
	if blksize not in [4, 8, 16, 32] :
		raise vs.Error(f"模块 {func_name} 的子参数 blksize 的值无效")
	if not (isinstance(thscd1, int) and thscd1 >= 0) :
		raise vs.Error(f"模块 {func_name} 的子参数 thscd1 的值无效")
	if not (isinstance(thscd2, int) and (thscd2 >= 0 and thscd2 <= 255)) :
		raise vs.Error(f"模块 {func_name} 的子参数 thscd2 的值无效")
	if not isinstance(vs_t, int) or vs_t > vs_thd_init :
		raise vs.Error(f"模块 {func_name} 的子参数 vs_t 的值无效")

	if not hasattr(core, "mv") :
		raise ModuleNotFoundError(f"模块 {func_name} 依赖错误：缺失插件，检查项目 mv")

	core.num_threads = vs_t
	blksizev = blksize
	search = [0, 3, 3][(qty_lv - 1)]
	block_mode = [0, 0, 3][(qty_lv - 1)]
	flow_mask = [0, 1, 2][(qty_lv - 1)]
	analParams = { 'overlap':0,'overlapv':0,'search':search,'dct':0,'truemotion':True,
		'blksize':blksize,'blksizev':blksizev,'searchparam':2,'badsad':10000,'badrange':24,
		'divide':0 }
	bofp = { 'thscd1':thscd1,'thscd2':thscd2,'blend':True,'num':int(fps_out * 1e6),'den':1e6 }

	cut0 = core.std.AssumeFPS(input, fpsnum=int(fps_in * 1e6), fpsden=1e6)
	sup = core.mv.Super(input, pel=2, sharp=2, rfilter=4)
	bvec = core.mv.Analyse(sup, isb=True, **analParams)
	fvec = core.mv.Analyse(sup, isb=False, **analParams)
	if block == True :
		output =  core.mv.BlockFPS(cut0, sup, bvec, fvec, **bofp, mode=block_mode)
	else :
		output = core.mv.FlowFPS(cut0, sup, bvec, fvec, **bofp, mask=flow_mask)

	return output

##################################################
## RIFE补帧 Vulkan
##################################################

def RIFE_STD(
	input : vs.VideoNode,
	model : typing.Literal[23, 70, 72, 73] = 23,
	t_tta : bool = False,
	fps_num : int = 2,
	fps_den : int = 1,
	sc_mode : typing.Literal[0, 1, 2] = 1,
	skip : bool = True,
	stat_th : float = 60.0,
	gpu : typing.Literal[0, 1, 2] = 0,
	gpu_t : int = 2,
	vs_t : int = vs_thd_dft,
) -> vs.VideoNode :

	func_name = "RIFE_STD"
	if not isinstance(input, vs.VideoNode) :
		raise vs.Error(f"模块 {func_name} 的子参数 input 的值无效")
	if model not in [23, 70, 72, 73] :
		raise vs.Error(f"模块 {func_name} 的子参数 model 的值无效")
	if not isinstance(t_tta, bool) :
		raise vs.Error(f"模块 {func_name} 的子参数 t_tta 的值无效")
	if not isinstance(fps_num, int) or fps_num < 2 :
		raise vs.Error(f"模块 {func_name} 的子参数 fps_num 的值无效")
	if not isinstance(fps_den, int) or fps_den >= fps_num or fps_num/fps_den <= 1 :
		raise vs.Error(f"模块 {func_name} 的子参数 fps_den 的值无效")
	if sc_mode not in [0, 1, 2] :
		raise vs.Error(f"模块 {func_name} 的子参数 sc_mode 的值无效")
	if not isinstance(skip, bool) :
		raise vs.Error(f"模块 {func_name} 的子参数 skip 的值无效")
	if not isinstance(stat_th, (int, float)) or stat_th <= 0.0 or stat_th > 60.0 :
		raise vs.Error(f"模块 {func_name} 的子参数 stat_th 的值无效")
	if gpu not in [0, 1, 2] :
		raise vs.Error(f"模块 {func_name} 的子参数 gpu 的值无效")
	if not isinstance(gpu_t, int) or gpu_t <= 0 :
		raise vs.Error(f"模块 {func_name} 的子参数 gpu_t 的值无效")
	if not isinstance(vs_t, int) or vs_t > vs_thd_init :
		raise vs.Error(f"模块 {func_name} 的子参数 vs_t 的值无效")

	if not hasattr(core, "rife") :
		raise ModuleNotFoundError(f"模块 {func_name} 依赖错误：缺失插件，检查项目 rife")
	if skip :
		if not hasattr(core, "vmaf") :
			raise ModuleNotFoundError(f"模块 {func_name} 依赖错误：缺失插件，检查项目 vmaf")
	if sc_mode == 1 :
		if not hasattr(core, "misc") :
			raise ModuleNotFoundError(f"模块 {func_name} 依赖错误：缺失插件，检查项目 misc")
	elif sc_mode == 2 :
		if not hasattr(core, "mv") :
			raise ModuleNotFoundError(f"模块 {func_name} 依赖错误：缺失插件，检查项目 mv")

	core.num_threads = vs_t
	fmt_in = input.format.id
	colorlv = getattr(input.get_frame(0).props, "_ColorRange", 0)

	if sc_mode == 0 :
		cut0 = input
	elif sc_mode == 1 :
		cut0 = core.misc.SCDetect(clip=input, threshold=0.15)
	elif sc_mode == 2 :
		sup = core.mv.Super(clip=input, pel=1)
		vec = core.mv.Analyse(super=sup, isb=True)
		cut0 = core.mv.SCDetection(clip=input, vectors=vec, thscd1=240, thscd2=130)
	if model >= 63 :
		t_tta = False

	cut1 = core.resize.Bilinear(clip=cut0, format=vs.RGBS, matrix_in_s="709")
	cut2 = core.rife.RIFE(clip=cut1, model=(model+1) if t_tta else model, factor_num=fps_num, factor_den=fps_den, gpu_id=gpu, gpu_thread=gpu_t, sc=True if sc_mode else False, skip=skip, skip_threshold=stat_th)
	output = core.resize.Bilinear(clip=cut2, format=fmt_in, matrix_s="709", range=1 if colorlv==0 else None)

	return output

##################################################
## RIFE补帧 DirectML
##################################################

def RIFE_DML(
	input : vs.VideoNode,
	model : typing.Literal[46, 4251, 426, 4262] = 46,
	turbo : bool = True,
	fps_in : float = 23.976,
	fps_num : int = 2,
	fps_den : int = 1,
	sc_mode : typing.Literal[0, 1, 2] = 1,
	gpu : typing.Literal[0, 1, 2] = 0,
	gpu_t : int = 2,
	vs_t : int = vs_thd_dft,
) -> vs.VideoNode :

	func_name = "RIFE_DML"
	if not isinstance(input, vs.VideoNode) :
		raise vs.Error(f"模块 {func_name} 的子参数 input 的值无效")
	if model not in [46, 4251, 426, 4262] :
		raise vs.Error(f"模块 {func_name} 的子参数 model 的值无效")
	if not isinstance(turbo, bool) :
		raise vs.Error(f"模块 {func_name} 的子参数 turbo 的值无效")
	if not isinstance(fps_in, (int, float)) or fps_in <= 0.0 :
		raise vs.Error(f"模块 {func_name} 的子参数 fps_in 的值无效")
	if not isinstance(fps_num, int) or fps_num < 2 :
		raise vs.Error(f"模块 {func_name} 的子参数 fps_num 的值无效")
	if not isinstance(fps_den, int) or fps_den >= fps_num or fps_num/fps_den <= 1 :
		raise vs.Error(f"模块 {func_name} 的子参数 fps_den 的值无效")
	if sc_mode not in [0, 1, 2] :
		raise vs.Error(f"模块 {func_name} 的子参数 sc_mode 的值无效")
	if gpu not in [0, 1, 2] :
		raise vs.Error(f"模块 {func_name} 的子参数 gpu 的值无效")
	if not isinstance(gpu_t, int) or gpu_t <= 0 :
		raise vs.Error(f"模块 {func_name} 的子参数 gpu_t 的值无效")
	if not isinstance(vs_t, int) or vs_t > vs_thd_init :
		raise vs.Error(f"模块 {func_name} 的子参数 vs_t 的值无效")

	if not hasattr(core, "ort") :
		raise ModuleNotFoundError(f"模块 {func_name} 依赖错误：缺失插件，检查项目 ort")
	if sc_mode == 1 :
		if not hasattr(core, "misc") :
			raise ModuleNotFoundError(f"模块 {func_name} 依赖错误：缺失插件，检查项目 misc")
	elif sc_mode == 2 :
		if not hasattr(core, "mv") :
			raise ModuleNotFoundError(f"模块 {func_name} 依赖错误：缺失插件，检查项目 mv")
	if not (fps_num/fps_den).is_integer() :
		if not hasattr(core, "akarin") :
			raise ModuleNotFoundError(f"模块 {func_name} 依赖错误：缺失插件，检查项目 akarin")

	#ext_proc = True
	#t_tta = False
	if turbo :
		ext_proc = False
		t_tta = False
	else :
		ext_proc = True
		t_tta = True

	plg_dir = os.path.dirname(core.ort.Version()["path"]).decode()
	mdl_pname = "rife/" if ext_proc else "rife_v2/"
	if model in [4251, 426, 4262] :  ## https://github.com/AmusementClub/vs-mlrt/blob/2adfbab790eebe51c62c886400b0662570dfe3e9/scripts/vsmlrt.py#L1031-L1032
		t_tta = False
	if t_tta :
		mdl_fname = ["rife_v4.6_ensemble"][[46].index(model)]
	else :
		mdl_fname = ["rife_v4.6", "rife_v4.25_lite", "rife_v4.26", "rife_v4.26_heavy"][[46, 4251, 426, 4262].index(model)]
	mdl_pth = plg_dir + "/models/" + mdl_pname + mdl_fname + ".onnx"
	if not os.path.exists(mdl_pth) :
		raise vs.Error(f"模块 {func_name} 所请求的模型缺失")

	global vsmlrt
	if vsmlrt is None :
		try :
			import vsmlrt
		except ImportError :
			raise ImportError(f"模块 {func_name} 依赖错误：缺失脚本 vsmlrt")
	if LooseVersion(vsmlrt.__version__) < LooseVersion("3.22.13") :
		raise ImportError(f"模块 {func_name} 依赖错误：缺失脚本 vsmlrt 的版本号过低，至少 3.22.13")

	core.num_threads = vs_t
	w_in, h_in = input.width, input.height
	size_in = w_in * h_in
	colorlv = getattr(input.get_frame(0).props, "_ColorRange", 0)
	fmt_in = input.format.id
	fps_factor = fps_num/fps_den

	if (size_in > 4096 * 2176) :
		raise Exception("源分辨率超过限制的范围，已临时中止。")

	scale_model = 1
	if (size_in > 2048 * 1088) :
		scale_model = 0.5
		if not ext_proc :  ## https://github.com/AmusementClub/vs-mlrt/blob/abc5b1c777a5dde6bad51a099f28eba99375ef4e/scripts/vsmlrt.py#L1002
			scale_model = 1
	if model >= 47 :  ## https://github.com/AmusementClub/vs-mlrt/blob/2adfbab790eebe51c62c886400b0662570dfe3e9/scripts/vsmlrt.py#L1036-L1037
		scale_model = 1

	tile_size = 32  ## https://github.com/AmusementClub/vs-mlrt/blob/2adfbab790eebe51c62c886400b0662570dfe3e9/scripts/vsmlrt.py#L1014-L1023
	if model == 4251 :
		tile_size = 128
	elif model in [426, 4262] :
		tile_size = 64
	tile_size = tile_size / scale_model
	w_tmp = math.ceil(w_in / tile_size) * tile_size - w_in
	h_tmp = math.ceil(h_in / tile_size) * tile_size - h_in

	if sc_mode == 0 :
		cut0 = input
	elif sc_mode == 1 :
		cut0 = core.misc.SCDetect(clip=input, threshold=0.15)
	elif sc_mode == 2 :
		sup = core.mv.Super(clip=input, pel=1)
		vec = core.mv.Analyse(super=sup, isb=True)
		cut0 = core.mv.SCDetection(clip=input, vectors=vec, thscd1=240, thscd2=130)

	cut1 = core.resize.Bilinear(clip=cut0, format=vs.RGBS, matrix_in_s="709")
	if ext_proc :
		if w_tmp + h_tmp > 0 :
			cut1 = core.std.AddBorders(clip=cut1, right=w_tmp, bottom=h_tmp)
		fin = vsmlrt.RIFE(clip=cut1, multi=fractions.Fraction(fps_num, fps_den), scale=scale_model, model=model, ensemble=t_tta, _implementation=1, video_player=True, backend=vsmlrt.BackendV2.ORT_DML(
			num_streams=gpu_t, fp16=True, device_id=gpu))
		if w_tmp + h_tmp > 0 :
			fin = core.std.Crop(clip=fin, right=w_tmp, bottom=h_tmp)
	else :
		fin = vsmlrt.RIFE(clip=cut1, multi=fractions.Fraction(fps_num, fps_den), scale=scale_model, model=model, ensemble=t_tta, _implementation=2, video_player=True, backend=vsmlrt.BackendV2.ORT_DML(
			num_streams=gpu_t, fp16=False))  ## https://github.com/AmusementClub/vs-mlrt/issues/56#issuecomment-2801745592
	output = core.resize.Bilinear(clip=fin, format=fmt_in, matrix_s="709", range=1 if colorlv==0 else None)
	if not fps_factor.is_integer() :
		output = core.std.AssumeFPS(clip=output, fpsnum=fps_in * fps_num * 1e6, fpsden=fps_den * 1e6)

	return output

##################################################
## RIFE补帧 TensorRT
##################################################

def RIFE_NV(
	input : vs.VideoNode,
	model : typing.Literal[46, 4251, 426, 4262] = 46,
	int8_qnt : bool = False,
	turbo : bool = True,
	fps_in : float = 23.976,
	fps_num : int = 2,
	fps_den : int = 1,
	sc_mode : typing.Literal[0, 1, 2] = 1,
	gpu : typing.Literal[0, 1, 2] = 0,
	gpu_t : int = 2,
	ws_size : int = 0,
	vs_t : int = vs_thd_dft,
) -> vs.VideoNode :

	func_name = "RIFE_NV"
	if not isinstance(input, vs.VideoNode) :
		raise vs.Error(f"模块 {func_name} 的子参数 input 的值无效")
	if model not in [46, 4251, 426, 4262] :
		raise vs.Error(f"模块 {func_name} 的子参数 model 的值无效")
	if not isinstance(int8_qnt, bool) :
		raise vs.Error(f"模块 {func_name} 的子参数 int8_qnt 的值无效")
	if not isinstance(turbo, bool) :
		raise vs.Error(f"模块 {func_name} 的子参数 turbo 的值无效")
	if not isinstance(fps_in, (int, float)) or fps_in <= 0.0 :
		raise vs.Error(f"模块 {func_name} 的子参数 fps_in 的值无效")
	if not isinstance(fps_num, int) or fps_num < 2 :
		raise vs.Error(f"模块 {func_name} 的子参数 fps_num 的值无效")
	if not isinstance(fps_den, int) or fps_den >= fps_num or fps_num/fps_den <= 1 :
		raise vs.Error(f"模块 {func_name} 的子参数 fps_den 的值无效")
	if sc_mode not in [0, 1, 2] :
		raise vs.Error(f"模块 {func_name} 的子参数 sc_mode 的值无效")
	if gpu not in [0, 1, 2] :
		raise vs.Error(f"模块 {func_name} 的子参数 gpu 的值无效")
	if not isinstance(gpu_t, int) or gpu_t <= 0 :
		raise vs.Error(f"模块 {func_name} 的子参数 gpu_t 的值无效")
	if not isinstance(ws_size, int) or ws_size < 0 :
		raise vs.Error(f"模块 {func_name} 的子参数 ws_size 的值无效")
	if not isinstance(vs_t, int) or vs_t > vs_thd_init :
		raise vs.Error(f"模块 {func_name} 的子参数 vs_t 的值无效")

	if not hasattr(core, "trt") :
		raise ModuleNotFoundError(f"模块 {func_name} 依赖错误：缺失插件，检查项目 trt")
	if sc_mode == 1 :
		if not hasattr(core, "misc") :
			raise ModuleNotFoundError(f"模块 {func_name} 依赖错误：缺失插件，检查项目 misc")
	elif sc_mode == 2 :
		if not hasattr(core, "mv") :
			raise ModuleNotFoundError(f"模块 {func_name} 依赖错误：缺失插件，检查项目 mv")
	if not (fps_num/fps_den).is_integer() :
		if not hasattr(core, "akarin") :
			raise ModuleNotFoundError(f"模块 {func_name} 依赖错误：缺失插件，检查项目 akarin")

	#ext_proc = True
	#t_tta = False
	if turbo :
		ext_proc = False
		t_tta = False
	else :
		ext_proc = True
		t_tta = True

	plg_dir = os.path.dirname(core.trt.Version()["path"]).decode()
	mdl_pname = "rife/" if ext_proc else "rife_v2/"
	if model in [4251, 426, 4262] :  ## https://github.com/AmusementClub/vs-mlrt/blob/2adfbab790eebe51c62c886400b0662570dfe3e9/scripts/vsmlrt.py#L1031-L1032
		t_tta = False
	if t_tta :
		mdl_fname = ["rife_v4.6_ensemble"][[46].index(model)]
	else :
		mdl_fname = ["rife_v4.6", "rife_v4.25_lite", "rife_v4.26", "rife_v4.26_heavy"][[46, 4251, 426, 4262].index(model)]
	mdl_pth = plg_dir + "/models/" + mdl_pname + mdl_fname + ".onnx"
	if not os.path.exists(mdl_pth) :
		raise vs.Error(f"模块 {func_name} 所请求的模型缺失")

	global vsmlrt
	if vsmlrt is None :
		try :
			import vsmlrt
		except ImportError :
			raise ImportError(f"模块 {func_name} 依赖错误：缺失脚本 vsmlrt")
	if LooseVersion(vsmlrt.__version__) < LooseVersion("3.22.10") :
		raise ImportError(f"模块 {func_name} 依赖错误：缺失脚本 vsmlrt 的版本号过低，至少 3.22.10")

	core.num_threads = vs_t
	w_in, h_in = input.width, input.height
	size_in = w_in * h_in
	colorlv = getattr(input.get_frame(0).props, "_ColorRange", 0)
	fmt_in = input.format.id
	fps_factor = fps_num/fps_den

	st_eng = False
	if not ext_proc and model >= 47 : # https://github.com/AmusementClub/vs-mlrt/issues/72
		st_eng = True
	if (size_in > 4096 * 2176) :
		raise Exception("源分辨率超过限制的范围，已临时中止。")
	if not st_eng and (((w_in > 4096) or (h_in > 2176)) or ((w_in < 384) or (h_in < 384))) :
		raise Exception("源分辨率不属于动态引擎支持的范围，已临时中止。")

	scale_model = 1
	if st_eng and (size_in > 2048 * 1088) :
		scale_model = 0.5
		if not ext_proc :  ## https://github.com/AmusementClub/vs-mlrt/blob/abc5b1c777a5dde6bad51a099f28eba99375ef4e/scripts/vsmlrt.py#L1002
			scale_model = 1
	if model >= 47 :  ## https://github.com/AmusementClub/vs-mlrt/blob/2adfbab790eebe51c62c886400b0662570dfe3e9/scripts/vsmlrt.py#L1036-L1037
		scale_model = 1

	tile_size = 32  ## https://github.com/AmusementClub/vs-mlrt/blob/2adfbab790eebe51c62c886400b0662570dfe3e9/scripts/vsmlrt.py#L1014-L1023
	if model == 4251 :
		tile_size = 128
	elif model in [426, 4262] :
		tile_size = 64
	tile_size = tile_size / scale_model
	w_tmp = math.ceil(w_in / tile_size) * tile_size - w_in
	h_tmp = math.ceil(h_in / tile_size) * tile_size - h_in

	shape_list = {
		32: {"min": (10, 8), "opt": (60, 34), "max1": (128, 68), "max2": (64, 34)},
		64: {"min": (5, 4), "opt": (30, 17), "max1": (64, 34), "max2": (32, 17)},
		128: {"min": (3, 2), "opt": (15, 9), "max1": (32, 17), "max2": (16, 9)},}
	shape_cfg = shape_list[tile_size]
	min_shapes = [tile_size * x for x in shape_cfg["min"]]
	opt_shapes = [tile_size * x for x in shape_cfg["opt"]]
	max_shapes1 = [tile_size * x for x in shape_cfg["max1"]]
	max_shapes2 = [tile_size * x for x in shape_cfg["max2"]]

	if sc_mode == 0 :
		cut0 = input
	elif sc_mode == 1 :
		cut0 = core.misc.SCDetect(clip=input, threshold=0.15)
	elif sc_mode == 2 :
		sup = core.mv.Super(clip=input, pel=1)
		vec = core.mv.Analyse(super=sup, isb=True)
		cut0 = core.mv.SCDetection(clip=input, vectors=vec, thscd1=240, thscd2=130)

	cut1 = core.resize.Bilinear(clip=cut0, format=vs.RGBH, matrix_in_s="709")
	if ext_proc :
		if w_tmp + h_tmp > 0 :
			cut1 = core.std.AddBorders(clip=cut1, right=w_tmp, bottom=h_tmp)
		fin = vsmlrt.RIFE(clip=cut1, multi=fractions.Fraction(fps_num, fps_den), scale=scale_model, model=model, ensemble=t_tta, _implementation=1, video_player=True, backend=vsmlrt.BackendV2.TRT(
			num_streams=gpu_t, int8=int8_qnt, fp16=True, output_format=1,
			workspace=None if ws_size < 128 else (ws_size if st_eng else ws_size * 2),
			use_cuda_graph=True, use_cublas=False, use_cudnn=False,
			static_shape=st_eng, min_shapes=[0, 0] if st_eng else min_shapes,
			opt_shapes=None if st_eng else opt_shapes, max_shapes=None if st_eng else (max_shapes1 if (size_in > 2048 * 1088) else max_shapes2),
			device_id=gpu, short_path=True))
		if w_tmp + h_tmp > 0 :
			fin = core.std.Crop(clip=fin, right=w_tmp, bottom=h_tmp)
	else :
		fin = vsmlrt.RIFE(clip=cut1, multi=fractions.Fraction(fps_num, fps_den), scale=scale_model, model=model, ensemble=t_tta, _implementation=2, video_player=True, backend=vsmlrt.BackendV2.TRT(
			num_streams=gpu_t, int8=int8_qnt, fp16=True, output_format=1,
			workspace=None if ws_size < 128 else ws_size,
			use_cuda_graph=True, use_cublas=False, use_cudnn=False,
			static_shape=st_eng, min_shapes=[0, 0],
			opt_shapes=None, max_shapes=None,
			device_id=gpu, short_path=True))
	output = core.resize.Bilinear(clip=fin, format=fmt_in, matrix_s="709", range=1 if colorlv==0 else None)
	if not fps_factor.is_integer() :
		output = core.std.AssumeFPS(clip=output, fpsnum=fps_in * fps_num * 1e6, fpsden=fps_den * 1e6)

	return output

##################################################
## SVP补帧
##################################################

def SVP_LQ(
	input : vs.VideoNode,
	fps_in : float = 23.976,
	fps_num : typing.Literal[2, 3, 4] = 2,
	cpu : typing.Literal[0, 1] = 0,
	gpu : typing.Literal[0, 11, 12, 21] = 0,
	vs_t : int = vs_thd_dft,
) -> vs.VideoNode :

	func_name = "SVP_LQ"
	if not isinstance(input, vs.VideoNode) :
		raise vs.Error(f"模块 {func_name} 的子参数 input 的值无效")
	if not isinstance(fps_in, (int, float)) or fps_in <= 0.0 :
		raise vs.Error(f"模块 {func_name} 的子参数 fps_in 的值无效")
	if fps_num not in [2, 3, 4] :
		raise vs.Error(f"模块 {func_name} 的子参数 fps_num 的值无效")
	if cpu not in [0, 1] :
		raise vs.Error(f"模块 {func_name} 的子参数 cpu 的值无效")
	if gpu not in [0, 11, 12, 21] :
		raise vs.Error(f"模块 {func_name} 的子参数 gpu 的值无效")
	if not isinstance(vs_t, int) or vs_t > vs_thd_init :
		raise vs.Error(f"模块 {func_name} 的子参数 vs_t 的值无效")

	if not hasattr(core, "svp1") or not hasattr(core, "svp2") :
		raise ModuleNotFoundError(f"模块 {func_name} 依赖错误：缺失插件，检查项目 svp1 svp2")

	core.num_threads = vs_t
	fps_num = fps_num
	acc = 1 if cpu == 0 else 0

	smooth_param = "{rate:{num:%d,den:1,abs:false},algo:21,gpuid:%d,mask:{area:100},scene:{mode:0,limits:{m1:1800,m2:3600,scene:5200,zero:100,blocks:45}}}" % (fps_num, gpu)
	super_param = "{pel:2,gpu:%d,scale:{up:2,down:4}}" % (acc)
	analyse_param = "{block:{w:32,h:16,overlap:2},main:{levels:4,search:{type:4,distance:-8,coarse:{type:2,distance:-5,bad:{range:0}}},penalty:{lambda:10.0,plevel:1.5,pzero:110,pnbour:65}},refine:[{thsad:200,search:{type:4,distance:2}}]}"

	clip = input
	if clip.format.id == vs.YUV420P8 :
		clip8 = clip
	elif clip.format.id == vs.YUV420P10 :
		clip8 = core.resize.Bilinear(clip=clip, format=vs.YUV420P8)
	else :
		clip = core.resize.Bilinear(clip=clip, format=vs.YUV420P10, dither_type="random")
		clip8 = core.resize.Bilinear(clip=clip, format=vs.YUV420P8)

	svps = core.svp1.Super(clip8, super_param)
	svpv = core.svp1.Analyse(svps["clip"], svps["data"], clip if acc else clip8, analyse_param)
	output = core.svp2.SmoothFps(clip if acc else clip8, svps["clip"], svps["data"], svpv["clip"], svpv["data"], smooth_param, src=clip if acc else clip8, fps=fps_in)

	return output

##################################################
## SVP补帧
##################################################

def SVP_STD(
	input : vs.VideoNode,
	fps_in : float = 23.976,
	fps_out : float = 59.940,
	cpu : typing.Literal[0, 1] = 0,
	gpu : typing.Literal[0, 11, 12, 21] = 0,
	vs_t : int = vs_thd_dft,
) -> vs.VideoNode :

	func_name = "SVP_STD"
	if not isinstance(input, vs.VideoNode) :
		raise vs.Error(f"模块 {func_name} 的子参数 input 的值无效")
	if not isinstance(fps_in, (int, float)) or fps_in <= 0.0 :
		raise vs.Error(f"模块 {func_name} 的子参数 fps_in 的值无效")
	if not isinstance(fps_out, (int, float)) or fps_out <= 0.0 or fps_out <= fps_in :
		raise vs.Error(f"模块 {func_name} 的子参数 fps_out 的值无效")
	if cpu not in [0, 1] :
		raise vs.Error(f"模块 {func_name} 的子参数 cpu 的值无效")
	if gpu not in [0, 11, 12, 21] :
		raise vs.Error(f"模块 {func_name} 的子参数 gpu 的值无效")
	if not isinstance(vs_t, int) or vs_t > vs_thd_init :
		raise vs.Error(f"模块 {func_name} 的子参数 vs_t 的值无效")

	if not hasattr(core, "svp1") or not hasattr(core, "svp2") :
		raise ModuleNotFoundError(f"模块 {func_name} 依赖错误：缺失插件，检查项目 svp1 svp2")

	core.num_threads = vs_t
	fmt_in = input.format.id
	fps_out = fps_out * 1e6
	acc = 1 if cpu == 0 else 0

	smoothfps_params = "{rate:{num:%f,den:1000000,abs:true},algo:21,gpuid:%d,mask:{area:100},scene:{limits:{m1:1800,m2:3600,scene:5200,zero:100,blocks:45}}}" % (fps_out, gpu)
	super_params = "{pel:2,gpu:%d,scale:{up:2,down:4}}" % (acc)
	analyse_params = "{block:{w:32,h:32,overlap:2},main:{levels:4,search:{type:4,distance:-8,coarse:{type:4,distance:-5,bad:{range:0}}},penalty:{plevel:1.3,pzero:110,pnbour:75}},refine:[{thsad:200,search:{type:4,distance:2}}]}"

	if fmt_in == vs.YUV420P8 :
		clip_f = input
	else :
		clip_f = core.resize.Bilinear(clip=input, format=vs.YUV420P8)
	super = core.svp1.Super(clip_f, super_params)
	vectors = core.svp1.Analyse(super["clip"], super["data"], input if acc else clip_f, analyse_params)
	smooth = core.svp2.SmoothFps(input if acc else clip_f, super["clip"], super["data"], vectors["clip"], vectors["data"], smoothfps_params, src=input if acc else clip_f, fps=fps_in)
	output = core.std.AssumeFPS(smooth, fpsnum=smooth.fps_num, fpsden=smooth.fps_den)

	return output

##################################################
## PORT https://github.com/natural-harmonia-gropius
## SVP补帧
##################################################

def SVP_HQ(
	input : vs.VideoNode,
	fps_in : float = 23.976,
	fps_dp : float = 59.940,
	cpu : typing.Literal[0, 1] = 0,
	gpu : typing.Literal[0, 11, 12, 21] = 0,
	vs_t : int = vs_thd_dft,
) -> vs.VideoNode :

	func_name = "SVP_HQ"
	if not isinstance(input, vs.VideoNode) :
		raise vs.Error(f"模块 {func_name} 的子参数 input 的值无效")
	if not isinstance(fps_in, (int, float)) or fps_in <= 0.0 :
		raise vs.Error(f"模块 {func_name} 的子参数 fps_in 的值无效")
	if not isinstance(fps_dp, (int, float)) or fps_dp < 23.976 :
		raise vs.Error(f"模块 {func_name} 的子参数 fps_dp 的值无效")
	if cpu not in [0, 1] :
		raise vs.Error(f"模块 {func_name} 的子参数 cpu 的值无效")
	if gpu not in [0, 11, 12, 21] :
		raise vs.Error(f"模块 {func_name} 的子参数 gpu 的值无效")
	if not isinstance(vs_t, int) or vs_t > vs_thd_init :
		raise vs.Error(f"模块 {func_name} 的子参数 vs_t 的值无效")

	if not hasattr(core, "svp1") or not hasattr(core, "svp2") :
		raise ModuleNotFoundError(f"模块 {func_name} 依赖错误：缺失插件，检查项目 svp1 svp2")

	core.num_threads = vs_t
	fps = fps_in or 23.976
	freq = fps_dp or 59.970
	acc = 1 if cpu == 0 else 0
	overlap = 2 if cpu == 0 else 3
	w, h = input.width, input.height

	if (freq - fps < 2) :
		raise Exception("Interpolation is not necessary.")

	target_fps = 60

	sp = "{gpu:%d}" % (acc)
	ap = "{block:{w:32,h:16,overlap:%d},main:{levels:5,search:{type:4,distance:-12,coarse:{type:4,distance:-1,trymany:true,bad:{range:0}}},penalty:{lambda:3.33,plevel:1.33,lsad:3300,pzero:110,pnbour:50}},refine:[{thsad:400},{thsad:200,search:{type:4,distance:-4}}]}" % (overlap)
	fp = "{gpuid:%d,algo:23,rate:{num:%d,den:%d,abs:true},mask:{cover:80,area:30,area_sharp:0.75},scene:{mode:0,limits:{scene:6000,zero:100,blocks:40}}}" % (gpu, round(min(max(target_fps, fps * 2, freq / 2), freq)) * 1000, 1001)

	def _toYUV420(clip) :
		if clip.format.id == vs.YUV420P8 :
			clip8 = clip
		elif clip.format.id == vs.YUV420P10 :
			clip8 = core.resize.Bilinear(clip=clip, format=vs.YUV420P8)
		else :
			clip = core.resize.Bilinear(clip=clip, format=vs.YUV420P10)
			clip8 = core.resize.Bilinear(clip=clip, format=vs.YUV420P8)
		return clip, clip8

	def _svpflow(clip, fps, sp, ap, fp) :
		clip, clip8 = _toYUV420(clip)
		s = core.svp1.Super(clip8, sp)
		r = s["clip"], s["data"]
		v = core.svp1.Analyse(*r, clip, ap)
		r = *r, v["clip"], v["data"]
		clip = core.svp2.SmoothFps(clip if acc else clip8, *r, fp, src=clip, fps=fps)
		return clip

	output = _svpflow(input, fps, sp, ap, fp)

	return output

##################################################
## CREDIT https://github.com/BlackMickey
## SVP补帧
##################################################

def SVP_PRO(
	input : vs.VideoNode,
	fps_in : float = 23.976,
	fps_num : int = 2,
	fps_den : int = 1,
	abs : bool = False,
	cpu : typing.Literal[0, 1] = 0,
	nvof : bool = False,
	gpu : typing.Literal[0, 11, 12, 21] = 0,
	vs_t : int = vs_thd_dft,
) -> vs.VideoNode :

	func_name = "SVP_PRO"
	if not isinstance(input, vs.VideoNode) :
		raise vs.Error(f"模块 {func_name} 的子参数 input 的值无效")
	if not isinstance(fps_in, (int, float)) or fps_in <= 0.0 :
		raise vs.Error(f"模块 {func_name} 的子参数 fps_in 的值无效")
	if not (isinstance(fps_num, int) and fps_num > 1) :
		raise vs.Error(f"模块 {func_name} 的子参数 fps_num 的值无效")
	if not (isinstance(fps_den, int) and fps_den >= 1 and fps_den < fps_num) :
		raise vs.Error(f"模块 {func_name} 的子参数 fps_den 的值无效")
	if not isinstance(abs, bool) :
		raise vs.Error(f"模块 {func_name} 的子参数 abs 的值无效")
	if abs and (fps_num / fps_den <= fps_in) :
		raise vs.Error(f"模块 {func_name} 的子参数 fps_num 或 fps_den 的值无效")
	if cpu not in [0, 1] :
		raise vs.Error(f"模块 {func_name} 的子参数 cpu 的值无效")
	if not isinstance(nvof, bool) :
		raise vs.Error(f"模块 {func_name} 的子参数 nvof 的值无效")
	if nvof and cpu :
		raise vs.Error(f"模块 {func_name} 的子参数 cpu 的值无效")
	if gpu not in [0, 11, 12, 21] :
		raise vs.Error(f"模块 {func_name} 的子参数 gpu 的值无效")
	if not isinstance(vs_t, int) or vs_t > vs_thd_init :
		raise vs.Error(f"模块 {func_name} 的子参数 vs_t 的值无效")

	if not hasattr(core, "svp1") or not hasattr(core, "svp2") :
		raise ModuleNotFoundError(f"模块 {func_name} 依赖错误：缺失插件，检查项目 svp1 svp2")

	core.num_threads = vs_t
	w_in, h_in = input.width, input.height
	size_in = w_in * h_in
	multi = "true" if abs else "false"
	acc = 1 if cpu == 0 else 0
	ana_lv = 5 if size_in > 510272 else 2

	super_param = "{pel:1,gpu:%d,full:true,scale:{up:2,down:4}}" % (acc)
	analyse_param = "{vectors:3,block:{w:32,h:32,overlap:1},main:{levels:%d,search:{type:4,distance:3,sort:true,satd:false,coarse:{width:960,type:4,distance:4,satd:true,trymany:false,bad:{sad:1000,range:0}}},penalty:{lambda:3.0,plevel:1.3,lsad:8000,pnew:50,pglobal:50,pzero:100,pnbour:65,prev:0}},refine:[{thsad:800,search:{type:4,distance:1,satd:false},penalty:{pnew:50}}]}" % (ana_lv)
	smooth_param = "{rate:{num:%d,den:%d,abs:%s},algo:13,block:false,cubic:%d,gpuid:%d,linear:true,mask:{cover:40,area:16,area_sharp:0.7},scene:{mode:3,blend:false,limits:{m1:2400,m2:3601,scene:5002,zero:125,blocks:40},luma:1.5}}" % (fps_num, fps_den, multi, acc, gpu)
	smooth_nvof_param = smooth_param

	clip = input
	if clip.format.id == vs.YUV420P8 :
		clip8 = clip
	elif clip.format.id == vs.YUV420P10 :
		clip8 = core.resize.Bilinear(clip=clip, format=vs.YUV420P8)
	else :
		clip = core.resize.Bilinear(clip=clip, format=vs.YUV420P10)
		clip8 = core.resize.Bilinear(clip=clip, format=vs.YUV420P8)

	if nvof :
		output  = core.svp2.SmoothFps_NVOF(clip, smooth_nvof_param, nvof_src=clip8, src=clip,fps=fps_in)
	else :
		super = core.svp1.Super(clip8, super_param)
		vectors = core.svp1.Analyse(super["clip"], super["data"], clip if acc else clip8, analyse_param)
		output = core.svp2.SmoothFps(clip if acc else clip8, super["clip"], super["data"], vectors["clip"], vectors["data"], smooth_param, src=clip if acc else clip8, fps=fps_in)

	return output

##################################################
## DPIR去块
##################################################

def DPIR_DBLK_NV(
	input : vs.VideoNode,
	lt_hd : bool = False,
	model : typing.Literal[2, 3] = 2,
	nr_lv : float = 50.0,
	gpu : typing.Literal[0, 1, 2] = 0,
	gpu_t : int = 2,
	st_eng : bool = False,
	ws_size : int = 0,
	vs_t : int = vs_thd_dft,
) -> vs.VideoNode :

	func_name = "DPIR_DBLK_NV"
	if not isinstance(input, vs.VideoNode) :
		raise vs.Error(f"模块 {func_name} 的子参数 input 的值无效")
	if not isinstance(lt_hd, bool) :
		raise vs.Error(f"模块 {func_name} 的子参数 lt_hd 的值无效")
	if model not in [2, 3] :
		raise vs.Error(f"模块 {func_name} 的子参数 model 的值无效")
	if not isinstance(nr_lv, (int, float)) or nr_lv <= 0.0 :
		raise vs.Error(f"模块 {func_name} 的子参数 nr_lv 的值无效")
	if gpu not in [0, 1, 2] :
		raise vs.Error(f"模块 {func_name} 的子参数 gpu 的值无效")
	if not isinstance(gpu_t, int) or gpu_t <= 0 :
		raise vs.Error(f"模块 {func_name} 的子参数 gpu_t 的值无效")
	if not isinstance(st_eng, bool) :
		raise vs.Error(f"模块 {func_name} 的子参数 st_eng 的值无效")
	if not isinstance(ws_size, int) or ws_size < 0 :
		raise vs.Error(f"模块 {func_name} 的子参数 ws_size 的值无效")
	if not isinstance(vs_t, int) or vs_t > vs_thd_init :
		raise vs.Error(f"模块 {func_name} 的子参数 vs_t 的值无效")

	if not hasattr(core, "trt") :
		raise ModuleNotFoundError(f"模块 {func_name} 依赖错误：缺失插件，检查项目 trt")

	plg_dir = os.path.dirname(core.trt.Version()["path"]).decode()
	mdl_fname = ["drunet_deblocking_grayscale", "drunet_deblocking_color"][[2, 3].index(model)]
	mdl_pth = plg_dir + "/models/dpir/" + mdl_fname + ".onnx"
	if not os.path.exists(mdl_pth) :
		raise vs.Error(f"模块 {func_name} 所请求的模型缺失")

	global vsmlrt
	if vsmlrt is None :
		try :
			import vsmlrt
		except ImportError :
			raise ImportError(f"模块 {func_name} 依赖错误：缺失脚本 vsmlrt")
	if LooseVersion(vsmlrt.__version__) < LooseVersion("3.18.1") :
		raise ImportError(f"模块 {func_name} 依赖错误：缺失脚本 vsmlrt 的版本号过低，至少 3.18.1")

	core.num_threads = vs_t
	w_in, h_in = input.width, input.height
	size_in = w_in * h_in
	colorlv = getattr(input.get_frame(0).props, "_ColorRange", 0)
	fmt_src = input.format
	fmt_in = fmt_src.id
	fmt_bit_in = fmt_src.bits_per_sample
	fmt_cf_in = fmt_src.color_family

	if (not lt_hd and (size_in > 1280 * 720)) or (size_in > 2048 * 1080) :
		raise Exception("源分辨率超过限制的范围，已临时中止。")
	if not st_eng and (((w_in > 2048) or (h_in > 1080)) or ((w_in < 64) or (h_in < 64))) :
		raise Exception("源分辨率不属于动态引擎支持的范围，已临时中止。")

	tile_size = 8
	w_tmp = math.ceil(w_in / tile_size) * tile_size - w_in
	h_tmp = math.ceil(h_in / tile_size) * tile_size - h_in
	if w_tmp + h_tmp > 0 :
		cut0 = core.std.AddBorders(clip=input, right=w_tmp, bottom=h_tmp)
	else :
		cut0 = input

	if model == 2 :
#		cut1 = core.resize.Bilinear(clip=cut0, format=vs.GRAYH, matrix_in_s="709")
#		cut2 = core.std.ShufflePlanes(clips=cut1, planes=0, colorfamily=vs.GRAY)
		cut1 = core.std.ShufflePlanes(clips=cut0, planes=0, colorfamily=vs.GRAY)
		cut2 = core.resize.Bilinear(clip=cut1, format=vs.GRAYH, matrix_in_s="709")
	else :
		cut2 = core.resize.Bilinear(clip=cut0, format=vs.RGBH, matrix_in_s="709")

	fin = vsmlrt.DPIR(clip=cut2, strength=nr_lv, model=model, backend=vsmlrt.BackendV2.TRT(
		num_streams=gpu_t, force_fp16=True, output_format=1,
		workspace=None if ws_size < 128 else (ws_size if st_eng else ws_size * 2),
		use_cuda_graph=True, use_cublas=False, use_cudnn=False,
		static_shape=st_eng, min_shapes=[0, 0] if st_eng else [384, 384],
		opt_shapes=None if st_eng else ([1920, 1080] if lt_hd else [1280, 720]), max_shapes=None if st_eng else ([2048, 1080] if lt_hd else [1280, 720]),
		device_id=gpu, short_path=True))

	if model == 2 :
		pre_mg = core.resize.Bilinear(clip=fin, format=fin.format.replace(bits_per_sample=fmt_bit_in, sample_type=0))
#		pre_mg = core.resize.Bilinear(clip=fin, format=fmt_in, matrix_s="709", range=1 if colorlv==0 else None)
		output = core.std.ShufflePlanes(clips=[pre_mg, cut0, cut0], planes=[0, 1, 2], colorfamily=fmt_cf_in)
	else :
		output = core.resize.Bilinear(clip=fin, format=fmt_in, matrix_s="709", range=1 if colorlv==0 else None)

	if w_tmp + h_tmp > 0 :
		output = core.std.Crop(clip=output, right=w_tmp, bottom=h_tmp)

	return output

##################################################
## Bilateral降噪
##################################################

def BILA_NV(
	input : vs.VideoNode,
	nr_spat : typing.List[float] = [3.0, 0.0, 0.0],
	nr_csp : typing.List[float] = [0.02, 0.0, 0.0],
	gpu : typing.Literal[0, 1, 2] = 0,
	gpu_t : int = 4,
	vs_t : int = vs_thd_dft,
) -> vs.VideoNode :

	func_name = "BILA_NV"
	if not isinstance(input, vs.VideoNode) :
		raise vs.Error(f"模块 {func_name} 的子参数 input 的值无效")
	if not (isinstance(nr_spat, list) and len(nr_spat) == 3) :
		raise vs.Error(f"模块 {func_name} 的子参数 nr_spat 的值无效")
	if not (isinstance(nr_csp, list) and len(nr_csp) == 3) :
		raise vs.Error(f"模块 {func_name} 的子参数 nr_csp 的值无效")
	if gpu not in [0, 1, 2] :
		raise vs.Error(f"模块 {func_name} 的子参数 gpu 的值无效")
	if not isinstance(gpu_t, int) or gpu_t <= 0 :
		raise vs.Error(f"模块 {func_name} 的子参数 gpu_t 的值无效")
	if not isinstance(vs_t, int) or vs_t > vs_thd_init :
		raise vs.Error(f"模块 {func_name} 的子参数 vs_t 的值无效")

	if not hasattr(core, "bilateralgpu_rtc") :
		raise ModuleNotFoundError(f"模块 {func_name} 依赖错误：缺失插件，检查项目 bilateralgpu_rtc")

	core.num_threads = vs_t
	fmt_in = input.format.id

	if fmt_in == vs.YUV444P16 :
		cut0 = input
	else :
		cut0 = core.resize.Bilinear(clip=input, format=vs.YUV444P16)
	cut1 = core.bilateralgpu_rtc.Bilateral(clip=cut0, sigma_spatial=nr_spat, sigma_color=nr_csp, device_id=gpu, num_streams=gpu_t, use_shared_memory=True)
	output = core.resize.Bilinear(clip=cut1, format=fmt_in)

	return output

##################################################
## BM3D降噪
##################################################

def BM3D_NV(
	input : vs.VideoNode,
	nr_lv : typing.List[int] = [5,0,0],
	bs_ref : typing.Literal[1, 2, 3, 4, 5, 6, 7, 8] = 8,
	bs_out : typing.Literal[1, 2, 3, 4, 5, 6, 7, 8] = 7,
	gpu : typing.Literal[0, 1, 2] = 0,
	vs_t : int = vs_thd_dft,
) -> vs.VideoNode :

	func_name = "BM3D_NV"
	if not isinstance(input, vs.VideoNode) :
		raise vs.Error(f"模块 {func_name} 的子参数 input 的值无效")
	if not (isinstance(nr_lv, list) and len(nr_lv) == 3 and all(isinstance(i, int) for i in nr_lv)) :
		raise vs.Error(f"模块 {func_name} 的子参数 nr_lv 的值无效")
	if bs_ref not in [1, 2, 3, 4, 5, 6, 7, 8] :
		raise vs.Error(f"模块 {func_name} 的子参数 bs_ref 的值无效")
	if bs_out not in [1, 2, 3, 4, 5, 6, 7, 8] or bs_out >= bs_ref :
		raise vs.Error(f"模块 {func_name} 的子参数 bs_out 的值无效")
	if gpu not in [0, 1, 2] :
		raise vs.Error(f"模块 {func_name} 的子参数 gpu 的值无效")
	if not isinstance(vs_t, int) or vs_t > vs_thd_init :
		raise vs.Error(f"模块 {func_name} 的子参数 vs_t 的值无效")

	if not hasattr(core, "bm3dcuda_rtc") :
		raise ModuleNotFoundError(f"模块 {func_name} 依赖错误：缺失插件，检查项目 bm3dcuda_rtc")

	core.num_threads = vs_t
	fmt_in = input.format.id

	cut0 = core.resize.Bilinear(clip=input, format=vs.YUV444PS)
	ref = core.bm3dcuda_rtc.BM3D(clip=cut0, sigma=nr_lv, block_step=bs_ref, device_id=gpu)
	cut1 = core.bm3dcuda_rtc.BM3D(clip=cut0, ref=ref, sigma=nr_lv, block_step=bs_out, device_id=gpu)
	output = core.resize.Bilinear(clip=cut1, format=fmt_in)

	return output

##################################################
## PORT jvsfunc (7bed2d843fd513505b209470fd82c71ef8bcc0dd)
## 减少彩色噪点
##################################################

def CCD_STD(
	input : vs.VideoNode,
	nr_lv : float = 20.0,
	vs_t : int = vs_thd_dft,
) -> vs.VideoNode :

	func_name = "CCD_STD"
	if not isinstance(input, vs.VideoNode) :
		raise vs.Error(f"模块 {func_name} 的子参数 input 的值无效")
	if not isinstance(nr_lv, (int, float)) or nr_lv <= 0.0 :
		raise vs.Error(f"模块 {func_name} 的子参数 nr_lv 的值无效")
	if not isinstance(vs_t, int) or vs_t > vs_thd_init :
		raise vs.Error(f"模块 {func_name} 的子参数 vs_t 的值无效")

	if not hasattr(core, "akarin") :
		raise ModuleNotFoundError(f"模块 {func_name} 依赖错误：缺失插件，检查项目 akarin")

	core.num_threads = vs_t
	colorlv = getattr(input.get_frame(0).props, "_ColorRange", 0)
	fmt_in = input.format.id

	def _ccd(src: vs.VideoNode, threshold: float = 4) -> vs.VideoNode :
		thr = threshold**2/195075.0
		r = core.std.ShufflePlanes([src, src, src], [0, 0, 0], vs.RGB)
		g = core.std.ShufflePlanes([src, src, src], [1, 1, 1], vs.RGB)
		b = core.std.ShufflePlanes([src, src, src], [2, 2, 2], vs.RGB)
		ex_ccd = core.akarin.Expr([r, g, b, src],
			'x[-12,-12] x - 2 pow y[-12,-12] y - 2 pow z[-12,-12] z - 2 pow + + A! '
			'x[-4,-12] x - 2 pow y[-4,-12] y - 2 pow z[-4,-12] z - 2 pow + + B! '
			'x[4,-12] x - 2 pow y[4,-12] y - 2 pow z[4,-12] z - 2 pow + + C! '
			'x[12,-12] x - 2 pow y[12,-12] y - 2 pow z[12,-12] z - 2 pow + + D! '
			'x[-12,-4] x - 2 pow y[-12,-4] y - 2 pow z[-12,-4] z - 2 pow + + E! '
			'x[-4,-4] x - 2 pow y[-4,-4] y - 2 pow z[-4,-4] z - 2 pow + + F! '
			'x[4,-4] x - 2 pow y[4,-4] y - 2 pow z[4,-4] z - 2 pow + + G! '
			'x[12,-4] x - 2 pow y[12,-4] y - 2 pow z[12,-4] z - 2 pow + + H! '
			'x[-12,4] x - 2 pow y[-12,4] y - 2 pow z[-12,4] z - 2 pow + + I! '
			'x[-4,4] x - 2 pow y[-4,4] y - 2 pow z[-4,4] z - 2 pow + + J! '
			'x[4,4] x - 2 pow y[4,4] y - 2 pow z[4,4] z - 2 pow + + K! '
			'x[12,4] x - 2 pow y[12,4] y - 2 pow z[12,4] z - 2 pow + + L! '
			'x[-12,12] x - 2 pow y[-12,12] y - 2 pow z[-12,12] z - 2 pow + + M! '
			'x[-4,12] x - 2 pow y[-4,12] y - 2 pow z[-4,12] z - 2 pow + + N! '
			'x[4,12] x - 2 pow y[4,12] y - 2 pow z[4,12] z - 2 pow + + O! '
			'x[12,12] x - 2 pow y[12,12] y - 2 pow z[12,12] z - 2 pow + + P! '
			f'A@ {thr} < 1 0 ? B@ {thr} < 1 0 ? C@ {thr} < 1 0 ? D@ {thr} < 1 0 ? '
			f'E@ {thr} < 1 0 ? F@ {thr} < 1 0 ? G@ {thr} < 1 0 ? H@ {thr} < 1 0 ? '
			f'I@ {thr} < 1 0 ? J@ {thr} < 1 0 ? K@ {thr} < 1 0 ? L@ {thr} < 1 0 ? '
			f'M@ {thr} < 1 0 ? N@ {thr} < 1 0 ? O@ {thr} < 1 0 ? P@ {thr} < 1 0 ? '
			'+ + + + + + + + + + + + + + + 1 + Q! '
			f'A@ {thr} < a[-12,-12] 0 ? B@ {thr} < a[-4,-12] 0 ? '
			f'C@ {thr} < a[4,-12] 0 ? D@ {thr} < a[12,-12] 0 ? '
			f'E@ {thr} < a[-12,-4] 0 ? F@ {thr} < a[-4,-4] 0 ? '
			f'G@ {thr} < a[4,-4] 0 ? H@ {thr} < a[12,-4] 0 ? '
			f'I@ {thr} < a[-12,4] 0 ? J@ {thr} < a[-4,4] 0 ? '
			f'K@ {thr} < a[4,4] 0 ? L@ {thr} < a[12,4] 0 ? '
			f'M@ {thr} < a[-12,12] 0 ? N@ {thr} < a[-4,12] 0 ? '
			f'O@ {thr} < a[4,12] 0 ? P@ {thr} < a[12,12] 0 ? '
			'+ + + + + + + + + + + + + + + a + Q@ /')
		return ex_ccd

	cut = core.resize.Bilinear(clip=input, format=vs.RGBS, matrix_in_s="709")
	fin = _ccd(src=cut, threshold=nr_lv)
	output = core.resize.Bilinear(clip=fin, format=fmt_in, matrix_s="709", range=1 if colorlv==0 else None)

	return output

##################################################
## DFTTest降噪
##################################################

def DFTT_STD(
	input : vs.VideoNode,
	plane : typing.List[int] = [0],
	nr_lv : float = 8.0,
	size_sb : int = 16,
	size_so : int = 12,
	size_tb : int = 3,
	vs_t : int = vs_thd_dft,
) -> vs.VideoNode :

	func_name = "DFTT_STD"
	if not isinstance(input, vs.VideoNode) :
		raise vs.Error(f"模块 {func_name} 的子参数 input 的值无效")
	if plane not in ([0], [1], [2], [0, 1], [0, 2], [1, 2], [0, 1, 2]) :
		raise vs.Error(f"模块 {func_name} 的子参数 plane 的值无效")
	if not isinstance(nr_lv, (int, float)) or nr_lv <= 0 :
		raise vs.Error(f"模块 {func_name} 的子参数 nr_lv 的值无效")
	if not isinstance(size_sb, int) or size_sb <= 0 :
		raise vs.Error(f"模块 {func_name} 的子参数 size_sb 的值无效")
	if not isinstance(size_so, int) or size_so <= 0 :
		raise vs.Error(f"模块 {func_name} 的子参数 size_so 的值无效")
	if not isinstance(size_tb, int) or size_tb <= 0 :
		raise vs.Error(f"模块 {func_name} 的子参数 size_tb 的值无效")
	if not isinstance(vs_t, int) or vs_t > vs_thd_init :
		raise vs.Error(f"模块 {func_name} 的子参数 vs_t 的值无效")

	if not hasattr(core, "dfttest2_cpu") :
		raise ModuleNotFoundError(f"模块 {func_name} 依赖错误：缺失插件，检查项目 dfttest2_cpu")

	global dfttest2
	if dfttest2 is None :
		try :
			import dfttest2
		except ImportError :
			raise ImportError(f"模块 {func_name} 依赖错误：缺失脚本 dfttest2")
	if LooseVersion(dfttest2.__version__) < LooseVersion("0.3.3") :
		raise ImportError(f"模块 {func_name} 依赖错误：缺失脚本 dfttest2 的版本号过低，至少 0.3.3")

	core.num_threads = vs_t
	fmt_in = input.format.id

	if fmt_in == vs.YUV444P16 :
		cut0 = input
	else :
		cut0 = core.resize.Bilinear(clip=input, format=vs.YUV444P16)
	cut1 = dfttest2.DFTTest2(clip=cut0, planes=plane, sigma=nr_lv, sbsize=size_sb, sosize=size_so, tbsize=size_tb, backend=dfttest2.Backend.CPU())
	output = core.resize.Bilinear(clip=cut1, format=fmt_in)

	return output

##################################################
## DFTTest降噪
##################################################

def DFTT_NV(
	input : vs.VideoNode,
	plane : typing.List[int] = [0],
	nr_lv : float = 8.0,
	size_sb : int = 16,
	size_so : int = 12,
	size_tb : int = 3,
	gpu : typing.Literal[0, 1, 2] = 0,
	gpu_t : int = 4,
	vs_t : int = vs_thd_dft,
) -> vs.VideoNode :

	func_name = "DFTT_NV"
	if not isinstance(input, vs.VideoNode) :
		raise vs.Error(f"模块 {func_name} 的子参数 input 的值无效")
	if plane not in ([0], [1], [2], [0, 1], [0, 2], [1, 2], [0, 1, 2]) :
		raise vs.Error(f"模块 {func_name} 的子参数 plane 的值无效")
	if not isinstance(nr_lv, (int, float)) or nr_lv <= 0 :
		raise vs.Error(f"模块 {func_name} 的子参数 nr_lv 的值无效")
	if not isinstance(size_sb, int) or size_sb <= 0 :
		raise vs.Error(f"模块 {func_name} 的子参数 size_sb 的值无效")
	if not isinstance(size_so, int) or size_so <= 0 :
		raise vs.Error(f"模块 {func_name} 的子参数 size_so 的值无效")
	if not isinstance(size_tb, int) or size_tb <= 0 :
		raise vs.Error(f"模块 {func_name} 的子参数 size_tb 的值无效")
	if gpu not in [0, 1, 2] :
		raise vs.Error(f"模块 {func_name} 的子参数 gpu 的值无效")
	if not isinstance(gpu_t, int) or gpu_t <= 0 :
		raise vs.Error(f"模块 {func_name} 的子参数 gpu_t 的值无效")
	if not isinstance(vs_t, int) or vs_t > vs_thd_init :
		raise vs.Error(f"模块 {func_name} 的子参数 vs_t 的值无效")

	if not hasattr(core, "dfttest2_nvrtc") :
		raise ModuleNotFoundError(f"模块 {func_name} 依赖错误：缺失插件，检查项目 dfttest2_nvrtc")

	core.num_threads = vs_t
	fmt_in = input.format.id

	global dfttest2
	if dfttest2 is None :
		try :
			import dfttest2
		except ImportError :
			raise ImportError(f"模块 {func_name} 依赖错误：缺失脚本 dfttest2")
	if LooseVersion(dfttest2.__version__) < LooseVersion("0.3.3") :
		raise ImportError(f"模块 {func_name} 依赖错误：缺失脚本 dfttest2 的版本号过低，至少 0.3.3")

	if fmt_in == vs.YUV444P16 :
		cut0 = input
	else :
		cut0 = core.resize.Bilinear(clip=input, format=vs.YUV444P16)
	cut1 = dfttest2.DFTTest2(clip=cut0, planes=plane, sigma=nr_lv, sbsize=size_sb, sosize=size_so, tbsize=size_tb, backend=dfttest2.Backend.NVRTC(device_id=gpu, num_streams=gpu_t))
	output = core.resize.Bilinear(clip=cut1, format=fmt_in)

	return output

##################################################
## DPIR降噪
##################################################

def DPIR_NR_NV(
	input : vs.VideoNode,
	lt_hd : bool = False,
	model : typing.Literal[0, 1] = 0,
	nr_lv : float = 5.0,
	gpu : typing.Literal[0, 1, 2] = 0,
	gpu_t : int = 2,
	st_eng : bool = False,
	ws_size : int = 0,
	vs_t : int = vs_thd_dft,
) -> vs.VideoNode :

	func_name = "DPIR_NR_NV"
	if not isinstance(input, vs.VideoNode) :
		raise vs.Error(f"模块 {func_name} 的子参数 input 的值无效")
	if not isinstance(lt_hd, bool) :
		raise vs.Error(f"模块 {func_name} 的子参数 lt_hd 的值无效")
	if model not in [0, 1] :
		raise vs.Error(f"模块 {func_name} 的子参数 model 的值无效")
	if not isinstance(nr_lv, (int, float)) or nr_lv <= 0.0 :
		raise vs.Error(f"模块 {func_name} 的子参数 nr_lv 的值无效")
	if gpu not in [0, 1, 2] :
		raise vs.Error(f"模块 {func_name} 的子参数 gpu 的值无效")
	if not isinstance(gpu_t, int) or gpu_t <= 0 :
		raise vs.Error(f"模块 {func_name} 的子参数 gpu_t 的值无效")
	if not isinstance(st_eng, bool) :
		raise vs.Error(f"模块 {func_name} 的子参数 st_eng 的值无效")
	if not isinstance(ws_size, int) or ws_size < 0 :
		raise vs.Error(f"模块 {func_name} 的子参数 ws_size 的值无效")
	if not isinstance(vs_t, int) or vs_t > vs_thd_init :
		raise vs.Error(f"模块 {func_name} 的子参数 vs_t 的值无效")

	if not hasattr(core, "trt") :
		raise ModuleNotFoundError(f"模块 {func_name} 依赖错误：缺失插件，检查项目 trt")

	plg_dir = os.path.dirname(core.trt.Version()["path"]).decode()
	mdl_fname = ["drunet_gray", "drunet_color"][[0, 1].index(model)]
	mdl_pth = plg_dir + "/models/dpir/" + mdl_fname + ".onnx"
	if not os.path.exists(mdl_pth) :
		raise vs.Error(f"模块 {func_name} 所请求的模型缺失")

	global vsmlrt
	if vsmlrt is None :
		try :
			import vsmlrt
		except ImportError :
			raise ImportError(f"模块 {func_name} 依赖错误：缺失脚本 vsmlrt")
	if LooseVersion(vsmlrt.__version__) < LooseVersion("3.18.1") :
		raise ImportError(f"模块 {func_name} 依赖错误：缺失脚本 vsmlrt 的版本号过低，至少 3.18.1")

	core.num_threads = vs_t
	w_in, h_in = input.width, input.height
	size_in = w_in * h_in
	colorlv = getattr(input.get_frame(0).props, "_ColorRange", 0)
	fmt_src = input.format
	fmt_in = fmt_src.id
	fmt_bit_in = fmt_src.bits_per_sample
	fmt_cf_in = fmt_src.color_family

	if (not lt_hd and (size_in > 1280 * 720)) or (size_in > 2048 * 1080) :
		raise Exception("源分辨率超过限制的范围，已临时中止。")
	if not st_eng and (((w_in > 2048) or (h_in > 1080)) or ((w_in < 64) or (h_in < 64))) :
		raise Exception("源分辨率不属于动态引擎支持的范围，已临时中止。")

	tile_size = 8
	w_tmp = math.ceil(w_in / tile_size) * tile_size - w_in
	h_tmp = math.ceil(h_in / tile_size) * tile_size - h_in
	if w_tmp + h_tmp > 0 :
		cut0 = core.std.AddBorders(clip=input, right=w_tmp, bottom=h_tmp)
	else :
		cut0 = input

	if model == 0 :
#		cut1 = core.resize.Bilinear(clip=cut0, format=vs.GRAYH, matrix_in_s="709")
#		cut2 = core.std.ShufflePlanes(clips=cut1, planes=0, colorfamily=vs.GRAY)
		cut1 = core.std.ShufflePlanes(clips=cut0, planes=0, colorfamily=vs.GRAY)
		cut2 = core.resize.Bilinear(clip=cut1, format=vs.GRAYH, matrix_in_s="709")
	else :
		cut2 = core.resize.Bilinear(clip=cut0, format=vs.RGBH, matrix_in_s="709")

	fin = vsmlrt.DPIR(clip=cut2, strength=nr_lv, model=model, backend=vsmlrt.BackendV2.TRT(
		num_streams=gpu_t, force_fp16=True, output_format=1,
		workspace=None if ws_size < 128 else (ws_size if st_eng else ws_size * 2),
		use_cuda_graph=True, use_cublas=False, use_cudnn=False,
		static_shape=st_eng, min_shapes=[0, 0] if st_eng else [384, 384],
		opt_shapes=None if st_eng else ([1920, 1080] if lt_hd else [1280, 720]), max_shapes=None if st_eng else ([2048, 1080] if lt_hd else [1280, 720]),
		device_id=gpu, short_path=True))

	if model == 0 :
		pre_mg = core.resize.Bilinear(clip=fin, format=fin.format.replace(bits_per_sample=fmt_bit_in, sample_type=0))
#		pre_mg = core.resize.Bilinear(clip=fin, format=fmt_in, matrix_s="709", range=1 if colorlv==0 else None)
		output = core.std.ShufflePlanes(clips=[pre_mg, cut0, cut0], planes=[0, 1, 2], colorfamily=fmt_cf_in)
	else :
		output = core.resize.Bilinear(clip=fin, format=fmt_in, matrix_s="709", range=1 if colorlv==0 else None)

	if w_tmp + h_tmp > 0 :
		output = core.std.Crop(clip=output, right=w_tmp, bottom=h_tmp)

	return output

##################################################
## FFT3D降噪
##################################################

def FFT3D_STD(
	input : vs.VideoNode,
	mode : typing.Literal[1, 2] = 1,
	nr_lv : float = 2.0,
	plane : typing.List[int] = [0],
	frame_bk : typing.Literal[-1, 0, 1, 2, 3, 4, 5] = 3,
	cpu_t : int = 6,
	vs_t : int = vs_thd_dft,
) -> vs.VideoNode :

	func_name = "FFT3D_STD"
	if not isinstance(input, vs.VideoNode) :
		raise vs.Error(f"模块 {func_name} 的子参数 input 的值无效")
	if mode not in [1, 2] :
		raise vs.Error(f"模块 {func_name} 的子参数 mode 的值无效")
	if not isinstance(nr_lv, (int, float)) or nr_lv <= 0.0 :
		raise vs.Error(f"模块 {func_name} 的子参数 nr_lv 的值无效")
	if plane not in ([0], [1], [2], [0, 1], [0, 2], [1, 2], [0, 1, 2]) :
		raise vs.Error(f"模块 {func_name} 的子参数 plane 的值无效")
	if frame_bk not in [-1, 0, 1, 2, 3, 4, 5] :
		raise vs.Error(f"模块 {func_name} 的子参数 frame_bk 的值无效")
	if not isinstance(cpu_t, int) or cpu_t < 1 :
		raise vs.Error(f"模块 {func_name} 的子参数 cpu_t 的值无效")
	if not isinstance(vs_t, int) or vs_t > vs_thd_init :
		raise vs.Error(f"模块 {func_name} 的子参数 vs_t 的值无效")

	if not hasattr(core, "trt") :
		raise ModuleNotFoundError(f"模块 {func_name} 依赖错误：缺失插件，检查项目 trt")
	if mode == 1 :
		if not hasattr(core, "fft3dfilter") :
			raise ModuleNotFoundError(f"模块 {func_name} 依赖错误：缺失插件，检查项目 fft3dfilter")
	elif mode == 2 :
		if not hasattr(core, "neo_fft3d") :
			raise ModuleNotFoundError(f"模块 {func_name} 依赖错误：缺失插件，检查项目 neo_fft3d")

	core.num_threads = vs_t

	if mode == 1 :
		output = core.fft3dfilter.FFT3DFilter(clip=input, sigma=nr_lv, planes=plane, bt=frame_bk, ncpu=cpu_t)
	elif mode == 2 :
		output = core.neo_fft3d.FFT3D(clip=input, sigma=nr_lv, planes=plane, bt=frame_bk, ncpu=cpu_t, mt=False)

	return output

##################################################
## NLmeans降噪
##################################################

def NLM_STD(
	input : vs.VideoNode,
	blur_m : typing.Literal[0, 1, 2] = 2,
	nlm_m : typing.Literal[1, 2] = 1,
	frame_num : int = 1,
	rad_sw : int = 2,
	rad_snw : int = 2,
	nr_lv : float = 3.0,
	gpu : typing.Literal[0, 1, 2] = 0,
	vs_t : int = vs_thd_dft,
) -> vs.VideoNode :

	func_name = "NLM_STD"
	if not isinstance(input, vs.VideoNode) :
		raise vs.Error(f"模块 {func_name} 的子参数 input 的值无效")
	if blur_m not in [0, 1, 2] :
		raise vs.Error(f"模块 {func_name} 的子参数 blur_m 的值无效")
	if nlm_m not in [1, 2] :
		raise vs.Error(f"模块 {func_name} 的子参数 nlm_m 的值无效")
	if not isinstance(frame_num, int) or frame_num < 0 :
		raise vs.Error(f"模块 {func_name} 的子参数 frame_num 的值无效")
	if not isinstance(rad_sw, int) or rad_sw < 0 :
		raise vs.Error(f"模块 {func_name} 的子参数 rad_sw 的值无效")
	if not isinstance(rad_snw, int) or rad_snw < 0 :
		raise vs.Error(f"模块 {func_name} 的子参数 rad_snw 的值无效")
	if not isinstance(nr_lv, (int, float)) or nr_lv <= 0.0 :
		raise vs.Error(f"模块 {func_name} 的子参数 nr_lv 的值无效")
	if gpu not in [0, 1, 2] :
		raise vs.Error(f"模块 {func_name} 的子参数 gpu 的值无效")
	if not isinstance(vs_t, int) or vs_t > vs_thd_init :
		raise vs.Error(f"模块 {func_name} 的子参数 vs_t 的值无效")

	if blur_m == 1 :
		if not hasattr(core, "rgvs") :
			raise ModuleNotFoundError(f"模块 {func_name} 依赖错误：缺失插件，检查项目 rgvs")
	if nlm_m == 1 :
		if not hasattr(core, "knlm") :
			raise ModuleNotFoundError(f"模块 {func_name} 依赖错误：缺失插件，检查项目 knlm")
	elif nlm_m == 2 :
		if not hasattr(core, "nlm_ispc") :
			raise ModuleNotFoundError(f"模块 {func_name} 依赖错误：缺失插件，检查项目 nlm_ispc")

	core.num_threads = vs_t
	fmt_in = input.format.id
	blur, diff = LAYER_HIGH(input=input, blur_m=blur_m, vs_t=vs_t)

	if blur_m :
		if nlm_m == 1 :
			cut1 = core.knlm.KNLMeansCL(clip=diff, d=frame_num, a=rad_sw, s=rad_snw, h=nr_lv,
				channels="auto", wmode=2, wref=1.0, rclip=None, device_type="GPU", device_id=gpu)
		elif nlm_m == 2 :
			cut1 = core.nlm_ispc.NLMeans(clip=diff, d=frame_num, a=rad_sw, s=rad_snw, h=nr_lv,
				channels="AUTO", wmode=2, wref=1.0, rclip=None)
		merge = core.std.MergeDiff(clipa=blur, clipb=cut1)
	else :
		if nlm_m == 1 :
			cut1 = core.knlm.KNLMeansCL(clip=blur, d=frame_num, a=rad_sw, s=rad_snw, h=nr_lv,
				channels="auto", wmode=2, wref=1.0, rclip=None, device_type="GPU", device_id=gpu)
		elif nlm_m == 2 :
			cut1 = core.nlm_ispc.NLMeans(clip=blur, d=frame_num, a=rad_sw, s=rad_snw, h=nr_lv,
				channels="AUTO", wmode=2, wref=1.0, rclip=None)
	output = core.resize.Bilinear(clip=merge if blur_m else cut1, format=fmt_in)

	return output

##################################################
## NLmeans降噪
##################################################

def NLM_NV(
	input : vs.VideoNode,
	blur_m : typing.Literal[0, 1, 2] = 2,
	frame_num : int = 1,
	rad_sw : int = 2,
	rad_snw : int = 2,
	nr_lv : float = 3.0,
	gpu : typing.Literal[0, 1, 2] = 0,
	gpu_t : int = 4,
	vs_t : int = vs_thd_dft,
) -> vs.VideoNode :

	func_name = "NLM_NV"
	if not isinstance(input, vs.VideoNode) :
		raise vs.Error(f"模块 {func_name} 的子参数 input 的值无效")
	if blur_m not in [0, 1, 2] :
		raise vs.Error(f"模块 {func_name} 的子参数 blur_m 的值无效")
	if not isinstance(frame_num, int) or frame_num < 0 :
		raise vs.Error(f"模块 {func_name} 的子参数 frame_num 的值无效")
	if not isinstance(rad_sw, int) or rad_sw < 0 :
		raise vs.Error(f"模块 {func_name} 的子参数 rad_sw 的值无效")
	if not isinstance(rad_snw, int) or rad_snw < 0 :
		raise vs.Error(f"模块 {func_name} 的子参数 rad_snw 的值无效")
	if not isinstance(nr_lv, (int, float)) or nr_lv <= 0.0 :
		raise vs.Error(f"模块 {func_name} 的子参数 nr_lv 的值无效")
	if gpu not in [0, 1, 2] :
		raise vs.Error(f"模块 {func_name} 的子参数 gpu 的值无效")
	if not isinstance(gpu_t, int) or gpu_t <= 0 :
		raise vs.Error(f"模块 {func_name} 的子参数 gpu_t 的值无效")
	if not isinstance(vs_t, int) or vs_t > vs_thd_init :
		raise vs.Error(f"模块 {func_name} 的子参数 vs_t 的值无效")

	if not hasattr(core, "nlm_cuda") :
		raise ModuleNotFoundError(f"模块 {func_name} 依赖错误：缺失插件，检查项目 nlm_cuda")
	if blur_m == 1 :
		if not hasattr(core, "rgvs") :
			raise ModuleNotFoundError(f"模块 {func_name} 依赖错误：缺失插件，检查项目 rgvs")

	core.num_threads = vs_t
	fmt_in = input.format.id
	blur, diff = LAYER_HIGH(input=input, blur_m=blur_m, vs_t=vs_t)

	if blur_m :
		cut1 = core.nlm_cuda.NLMeans(clip=diff, d=frame_num, a=rad_sw, s=rad_snw, h=nr_lv,
			channels="AUTO", wmode=2, wref=1.0, rclip=None, device_id=gpu, num_streams=gpu_t)
		merge = core.std.MergeDiff(clipa=blur, clipb=cut1)
	else :
		cut1 = core.nlm_cuda.NLMeans(clip=blur, d=frame_num, a=rad_sw, s=rad_snw, h=nr_lv,
			channels="AUTO", wmode=2, wref=1.0, rclip=None, device_id=gpu, num_streams=gpu_t)
	output = core.resize.Bilinear(clip=merge if blur_m else cut1, format=fmt_in)

	return output

##################################################
## https://github.com/mpv-player/mpv/issues/11460
## 修复p3错误转换后的白点
##################################################

def COLOR_P3W_FIX(
	input : vs.VideoNode,
	linear : bool = False,
	vs_t : int = vs_thd_dft,
) -> vs.VideoNode :

	func_name = "COLOR_P3W_FIX"
	if not isinstance(input, vs.VideoNode) :
		raise vs.Error(f"模块 {func_name} 的子参数 input 的值无效")
	if not isinstance(linear, bool) :
		raise vs.Error(f"模块 {func_name} 的子参数 linear 的值无效")
	if not isinstance(vs_t, int) or vs_t > vs_thd_init :
		raise vs.Error(f"模块 {func_name} 的子参数 vs_t 的值无效")

	if not hasattr(core, "fmtc") :
		raise ModuleNotFoundError(f"模块 {func_name} 依赖错误：缺失插件，检查项目 fmtc")

	core.num_threads = vs_t
	colorlv = input.get_frame(0).props._ColorRange

	cut = core.resize.Bilinear(clip=input, format=vs.RGB48, matrix_in_s="709")
	if linear :
		cut = core.fmtc.transfer(clip=cut, transs="1886", transd="linear")
	cut = core.fmtc.primaries(clip=cut, prims="p3d65", primd="p3dci", wconv=True)
	if linear :
		cut = core.fmtc.transfer(clip=cut, transs="linear", transd="1886")

	output = core.resize.Bilinear(clip=cut, format=vs.YUV420P8, matrix_s="709", range=1 if colorlv==0 else None)

	return output

##################################################
## MOD HAvsFunc (e236281cd8c1dd6b1b0cc906844944b79b1b52fa)
## 修正红蓝色度偏移
##################################################

def CSC_RB(
	input : vs.VideoNode,
	cx : int = 4,
	cy : int = 4,
	sat_lv1 : float = 4.0,
	sat_lv2 : float = 0.8,
	blur : bool = False,
	vs_t : int = vs_thd_dft,
) -> vs.VideoNode :

	func_name = "CSC_RB"
	if not isinstance(input, vs.VideoNode) :
		raise vs.Error(f"模块 {func_name} 的子参数 input 的值无效")
	if not isinstance(cx, int) :
		raise vs.Error(f"模块 {func_name} 的子参数 cx 的值无效")
	if not isinstance(cy, int) :
		raise vs.Error(f"模块 {func_name} 的子参数 cy 的值无效")
	if not isinstance(thr, (int, float)) :
		raise vs.Error(f"模块 {func_name} 的子参数 thr 的值无效")
	if not isinstance(sat_lv, (int, float)) :
		raise vs.Error(f"模块 {func_name} 的子参数 sat_lv 的值无效")
	if not isinstance(blur, bool) :
		raise vs.Error(f"模块 {func_name} 的子参数 blur 的值无效")
	if not isinstance(vs_t, int) or vs_t > vs_thd_init :
		raise vs.Error(f"模块 {func_name} 的子参数 vs_t 的值无效")

	core.num_threads = vs_t
	neutral = 1 << (input.format.bits_per_sample - 1)
	peak = (1 << input.format.bits_per_sample) - 1
	def _cround(x) :
		return math.floor(x + 0.5) if x > 0 else math.ceil(x - 0.5)
	def _scale(value, peak) :
		return _cround(value * peak / 255) if peak != 1 else value / 255
	def _Levels(clip, input_low, gamma, input_high, output_low, output_high, coring=True) :
		gamma = 1 / gamma
		divisor = input_high - input_low + (input_high == input_low)
		tvLow, tvHigh = _scale(16, peak), [_scale(235, peak), _scale(240, peak)]
		scaleUp, scaleDown = peak / _scale(219, peak), _scale(219, peak) / peak
		def _get_lut1(x) :
			p = ((x - tvLow) * scaleUp - input_low) / divisor if coring else (x - input_low) / divisor
			p = min(max(p, 0), 1) ** gamma * (output_high - output_low) + output_low
			return min(max(_cround(p * scaleDown + tvLow), tvLow), tvHigh[0]) if coring else min(max(_cround(p), 0), peak)
		def _get_lut2(x) :
			q = _cround((x - neutral) * (output_high - output_low) / divisor + neutral)
			return min(max(q, tvLow), tvHigh[1]) if coring else min(max(q, 0), peak)
		last = clip.std.Lut(planes=[0], function=_get_lut1)
		if clip.format.color_family != vs.GRAY :
			last = last.std.Lut(planes=[1, 2], function=_get_lut2)
		return last
	def _GetPlane(clip, plane=0) :
		sFormat = clip.format
		sNumPlanes = sFormat.num_planes
		last = core.std.ShufflePlanes(clips=clip, planes=plane, colorfamily=vs.GRAY)
		return last

	fmt_cf_in = input.format.color_family
	vch = _GetPlane(EQ(input, sat=sat_lv1, vs_t=vs_t), 2)
	area = vch
	if blur :
		area = vch.std.Convolution(matrix=[1, 2, 1, 2, 4, 2, 1, 2, 1])

	red = _Levels(area, _scale(255, peak), 1.0, _scale(255, peak), _scale(255, peak), 0)
	blue = _Levels(area, 0, 1.0, 0, 0, _scale(255, peak))
	mask = core.std.Merge(clipa=red, clipb=blue)

	if not blur :
		mask = mask.std.Convolution(matrix=[1, 2, 1, 2, 4, 2, 1, 2, 1])
	mask = _Levels(mask, _scale(250, peak), 1.0, _scale(250, peak), _scale(255, peak), 0)
	mask = mask.std.Convolution(matrix=[0, 0, 0, 1, 0, 0, 0, 0, 0], divisor=1, saturate=False).std.Convolution(
		matrix=[1, 1, 1, 1, 1, 1, 0, 0, 0], divisor=8, saturate=False)
	mask = _Levels(mask, _scale(10, peak), 1.0, _scale(10, peak), 0, _scale(255, peak)).std.Inflate()
	input_c = EQ(input.resize.Spline16(src_left=cx, src_top=cy), sat=sat_lv2, vs_t=vs_t)
	fu = core.std.MaskedMerge(clipa=_GetPlane(input, 1), clipb=_GetPlane(input_c, 1), mask=mask)
	fv = core.std.MaskedMerge(clipa=_GetPlane(input, 2), clipb=_GetPlane(input_c, 2), mask=mask)

	output = core.std.ShufflePlanes([input, fu, fv], planes=[0, 0, 0], colorfamily=fmt_cf_in)

	return output

##################################################
## f3kdb去色带
##################################################

def DEBAND_STD(
	input : vs.VideoNode,
	bd_range : int = 15,
	bdy_rth : int = 48,
	bdc_rth : int = 48,
	grainy : int = 48,
	grainc : int = 48,
	spl_m : typing.Literal[1, 2, 3, 4] = 4,
	grain_dy : bool = True,
	depth : typing.Literal[8, 10] = 8,
	vs_t : int = vs_thd_dft,
) -> vs.VideoNode :

	func_name = "DEBAND_STD"
	if not isinstance(input, vs.VideoNode) :
		raise vs.Error(f"模块 {func_name} 的子参数 input 的值无效")
	if not isinstance(bd_range, int) or bd_range < 1 :
		raise vs.Error(f"模块 {func_name} 的子参数 bd_range 的值无效")
	if not isinstance(bdy_rth, int) or bdy_rth < 1 :
		raise vs.Error(f"模块 {func_name} 的子参数 bdy_rth 的值无效")
	if not isinstance(bdc_rth, int) or bdc_rth < 1 :
		raise vs.Error(f"模块 {func_name} 的子参数 bdc_rth 的值无效")
	if not isinstance(grainy, int) or grainy < 1 :
		raise vs.Error(f"模块 {func_name} 的子参数 grainy 的值无效")
	if not isinstance(grainc, int) or grainc < 1 :
		raise vs.Error(f"模块 {func_name} 的子参数 grainc 的值无效")
	if spl_m not in [1, 2, 3, 4] :
		raise vs.Error(f"模块 {func_name} 的子参数 spl_m 的值无效")
	if not isinstance(grain_dy, bool) :
		raise vs.Error(f"模块 {func_name} 的子参数 grain_dy 的值无效")
	if depth not in [8, 10] :
		raise vs.Error(f"模块 {func_name} 的子参数 depth 的值无效")
	if not isinstance(vs_t, int) or vs_t > vs_thd_init :
		raise vs.Error(f"模块 {func_name} 的子参数 vs_t 的值无效")

	if not hasattr(core, "neo_f3kdb") :
		raise ModuleNotFoundError(f"模块 {func_name} 依赖错误：缺失插件，检查项目 neo_f3kdb")

	core.num_threads = vs_t
	fmt_in = fmt_in = input.format.id
	color_lv = getattr(input.get_frame(0).props, "_ColorRange", 0)

	if fmt_in == vs.YUV444P16 :
		cut0 = input
	else :
		cut0 = core.resize.Bilinear(clip=input, format=vs.YUV444P16)
	output = core.neo_f3kdb.Deband(clip=cut0, range=bd_range, y=bdy_rth, cb=bdc_rth, cr=bdc_rth, grainy=grainy, grainc=grainc, sample_mode=spl_m, dynamic_grain=grain_dy, mt=True, keep_tv_range=True if color_lv==1 else False, output_depth=depth)

	return output

##################################################
## 简易反交错
##################################################

def DEINT_LQ(
	input : vs.VideoNode,
	deint_m : typing.Literal[1, 2] = 1,
	tff : bool = True,
	vs_t : int = vs_thd_dft,
) -> vs.VideoNode :

	func_name = "DEINT_STD"
	if not isinstance(input, vs.VideoNode) :
		raise vs.Error(f"模块 {func_name} 的子参数 input 的值无效")
	if deint_m not in [1, 2] :
		raise vs.Error(f"模块 {func_name} 的子参数 deint_m 的值无效")
	if not isinstance(tff, bool) :
		raise vs.Error(f"模块 {func_name} 的子参数 tff 的值无效")
	if not isinstance(vs_t, int) or vs_t > vs_thd_init :
		raise vs.Error(f"模块 {func_name} 的子参数 vs_t 的值无效")

	if not hasattr(core, "bwdif") :
		raise ModuleNotFoundError(f"模块 {func_name} 依赖错误：缺失插件，检查项目 bwdif")

	core.num_threads = vs_t

	if deint_m == 1 :
		output = core.resize.Bob(clip=input, filter="bicubic", tff=tff)
	elif deint_m == 2 :
		output = core.bwdif.Bwdif(clip=input, field=3 if tff else 2)

	return output

##################################################
## 基于nnedi3/eedi3作参考的反交错
##################################################

def DEINT_STD(
	input : vs.VideoNode,
	ref_m : typing.Literal[1, 2, 3] = 1,
	tff : bool = True,
	gpu : typing.Literal[-1, 0, 1, 2] = -1,
	deint_m : typing.Literal[1, 2, 3] = 1,
	vs_t : int = vs_thd_dft,
) -> vs.VideoNode :

	func_name = "DEINT_STD"
	if not isinstance(input, vs.VideoNode) :
		raise vs.Error(f"模块 {func_name} 的子参数 input 的值无效")
	if ref_m not in [1, 2, 3] :
		raise vs.Error(f"模块 {func_name} 的子参数 ref_m 的值无效")
	if not isinstance(tff, bool) :
		raise vs.Error(f"模块 {func_name} 的子参数 tff 的值无效")
	if gpu not in [-1, 0, 1, 2] :
		raise vs.Error(f"模块 {func_name} 的子参数 gpu 的值无效")
	if deint_m not in [1, 2, 3] :
		raise vs.Error(f"模块 {func_name} 的子参数 deint_m 的值无效")
	if not isinstance(vs_t, int) or vs_t > vs_thd_init :
		raise vs.Error(f"模块 {func_name} 的子参数 vs_t 的值无效")

	if ref_m == 1 :
		if not hasattr(core, "znedi3") :
			raise ModuleNotFoundError(f"模块 {func_name} 依赖错误：缺失插件，检查项目 znedi3")
	elif ref_m == 2 :
		if not hasattr(core, "nnedi3cl") :
			raise ModuleNotFoundError(f"模块 {func_name} 依赖错误：缺失插件，检查项目 nnedi3cl")
	elif ref_m == 3 :
		if not hasattr(core, "eedi3m") :
			raise ModuleNotFoundError(f"模块 {func_name} 依赖错误：缺失插件，检查项目 eedi3m")
	if deint_m == 1 :
		if not hasattr(core, "bwdif") :
			raise ModuleNotFoundError(f"模块 {func_name} 依赖错误：缺失插件，检查项目 bwdif")
	elif deint_m == 2 :
		if not hasattr(core, "yadifmod") :
			raise ModuleNotFoundError(f"模块 {func_name} 依赖错误：缺失插件，检查项目 yadifmod")
	elif deint_m == 3 :
		if not hasattr(core, "tdm") :
			raise ModuleNotFoundError(f"模块 {func_name} 依赖错误：缺失插件，检查项目 tdm")

	core.num_threads = vs_t

	if ref_m == 1 :
		ref = core.znedi3.nnedi3(clip=input, field=3 if tff else 2, dh=False)
	elif ref_m == 2 :
		ref = core.nnedi3cl.NNEDI3CL(clip=input, field=3 if tff else 2, dh=False, device=gpu)
	elif ref_m == 3 :
		ref = core.eedi3m.EEDI3CL(clip=input, field=3 if tff else 2, dh=False, device=gpu)

	if deint_m == 1 :
		output = core.bwdif.Bwdif(clip=input, field=3 if tff else 2, edeint=ref)
	elif deint_m == 2 :
		output = core.yadifmod.Yadifmod(clip=input, edeint=ref, order=1 if tff else 0, mode=1)
	elif deint_m == 3 :
		output = core.tdm.TDeintMod(clip=input, order=1 if tff else 0, mode=1, length=6, ttype=0, edeint=ref)

	return output

##################################################
## 终极反交错
##################################################

def DEINT_EX(
	input : vs.VideoNode,
	fps_in : float = 23.976,
	deint_lv : typing.Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11] = 6,
	src_type : typing.Literal[0, 1, 2, 3] = 0,
	deint_den : typing.Literal[1, 2] = 1,
	tff : typing.Literal[0, 1, 2] = 0,
	cpu : bool = True,
	gpu : typing.Literal[-1, 0, 1, 2] = -1,
	vs_t : int = vs_thd_dft,
) -> vs.VideoNode :

	func_name = "DEINT_EX"
	if not isinstance(input, vs.VideoNode) :
		raise vs.Error(f"模块 {func_name} 的子参数 input 的值无效")
	if not isinstance(fps_in, (int, float)) or fps_in <= 0.0 :
		raise vs.Error(f"模块 {func_name} 的子参数 fps_in 的值无效")
	if deint_lv not in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11] :
		raise vs.Error(f"模块 {func_name} 的子参数 deint_lv 的值无效")
	if src_type not in [0, 1, 2, 3] :
		raise vs.Error(f"模块 {func_name} 的子参数 src_type 的值无效")
	if deint_den not in [1, 2] :
		raise vs.Error(f"模块 {func_name} 的子参数 deint_den 的值无效")
	if tff not in [0, 1, 2] :
		raise vs.Error(f"模块 {func_name} 的子参数 tff 的值无效")
	if not isinstance(cpu, bool) :
		raise vs.Error(f"模块 {func_name} 的子参数 cpu 的值无效")
	if gpu not in [-1, 0, 1, 2] :
		raise vs.Error(f"模块 {func_name} 的子参数 gpu 的值无效")
	if not isinstance(vs_t, int) or vs_t > vs_thd_init :
		raise vs.Error(f"模块 {func_name} 的子参数 vs_t 的值无效")

	core.num_threads = vs_t

	global qtgmc
	if qtgmc is None :
		try :
			import qtgmc
		except ImportError :
			raise ImportError(f"模块 {func_name} 依赖错误：缺失脚本 qtgmc")
	if LooseVersion(qtgmc.__version__) < LooseVersion("0.3.0") :
		raise ImportError(f"模块 {func_name} 依赖错误：缺失脚本 qtgmc 的版本号过低，至少 0.3.0")

	output = qtgmc.QTGMCv2(input=input, fps_in=fps_in, deint_lv=deint_lv, src_type=src_type, deint_den=deint_den, tff=tff, cpu=cpu, gpu=gpu)

	return output

##################################################
## NNEDI3抗锯齿
##################################################

def EDI_AA_STD(
	input : vs.VideoNode,
	cpu : bool = True,
	gpu : typing.Literal[-1, 0, 1, 2] = -1,
	vs_t : int = vs_thd_dft,
) -> vs.VideoNode :

	func_name = "EDI_AA_STD"
	if not isinstance(input, vs.VideoNode) :
		raise vs.Error(f"模块 {func_name} 的子参数 input 的值无效")
	if not isinstance(cpu, bool) :
		raise vs.Error(f"模块 {func_name} 的子参数 cpu 的值无效")
	if gpu not in [-1, 0, 1, 2] :
		raise vs.Error(f"模块 {func_name} 的子参数 gpu 的值无效")
	if not isinstance(vs_t, int) or vs_t > vs_thd_init :
		raise vs.Error(f"模块 {func_name} 的子参数 vs_t 的值无效")

	if cpu :
		if not hasattr(core, "znedi3") :
			raise ModuleNotFoundError(f"模块 {func_name} 依赖错误：缺失插件，检查项目 znedi3")
	else :
		if not hasattr(core, "nnedi3cl") :
			raise ModuleNotFoundError(f"模块 {func_name} 依赖错误：缺失插件，检查项目 nnedi3cl")

	core.num_threads = vs_t
	w_in, h_in = input.width, input.height

	if cpu :
		clip = core.znedi3.nnedi3(clip=input, field=1, dh=True)
		clip = core.std.Transpose(clip=clip)
		clip = core.znedi3.nnedi3(clip=clip, field=1, dh=True)
		clip = core.std.Transpose(clip=clip)
	else:
		clip = core.nnedi3cl.NNEDI3CL(clip=input, field=1, dh=True, device=gpu)
		clip = core.std.Transpose(clip=clip)
		clip = core.nnedi3cl.NNEDI3CL(clip=clip, field=1, dh=True, device=gpu)
		clip = core.std.Transpose(clip=clip)

	output = core.resize.Spline36(clip=clip, width=w_in, height=h_in, src_left=-0.5, src_top=-0.5)

	return output

##################################################
## EEID2抗锯齿
##################################################

def EDI_AA_NV(
	input : vs.VideoNode,
#	plane : typing.List[int] = [0],
	gpu : typing.Literal[-1, 0, 1, 2] = -1,
	gpu_t : int = 4,
	vs_t : int = vs_thd_dft,
) -> vs.VideoNode :

	func_name = "EDI_AA_NV"
	if not isinstance(input, vs.VideoNode) :
		raise vs.Error(f"模块 {func_name} 的子参数 input 的值无效")
#	if plane not in ([0], [1], [2], [0, 1], [0, 2], [1, 2], [0, 1, 2]) :
#		raise vs.Error(f"模块 {func_name} 的子参数 plane 的值无效")
	if gpu not in [-1, 0, 1, 2] :
		raise vs.Error(f"模块 {func_name} 的子参数 gpu 的值无效")
	if not isinstance(gpu_t, int) or gpu_t <= 0 :
		raise vs.Error(f"模块 {func_name} 的子参数 gpu_t 的值无效")
	if not isinstance(vs_t, int) or vs_t > vs_thd_init :
		raise vs.Error(f"模块 {func_name} 的子参数 vs_t 的值无效")

	if not hasattr(core, "eedi2cuda") :
		raise ModuleNotFoundError(f"模块 {func_name} 依赖错误：缺失插件，检查项目 eedi2cuda")

	core.num_threads = vs_t

	output = core.eedi2cuda.AA2(clip=input, mthresh=10, lthresh=20, vthresh=20, estr=2, dstr=4, maxd=24, map=0, nt=50, pp=1, num_streams=gpu_t, device_id=gpu)

	return output

##################################################
## 恢复被错误转换的25/30帧的源为24帧
##################################################

def IVTC_STD(
	input : vs.VideoNode,
	fps_in : float = 25,
	ivtc_m : typing.Literal[1, 2] = 1,
	vs_t : int = vs_thd_dft,
) -> vs.VideoNode :

	func_name = "IVTC_STD"
	if not isinstance(input, vs.VideoNode) :
		raise vs.Error(f"模块 {func_name} 的子参数 input 的值无效")
	if not isinstance(fps_in, (int, float)) or fps_in <= 0.0 :
		raise vs.Error(f"模块 {func_name} 的子参数 fps_in 的值无效")
	if ivtc_m not in [1, 2] :
		raise vs.Error(f"模块 {func_name} 的子参数 ivtc_m 的值无效")
	if not isinstance(vs_t, int) or vs_t > vs_thd_init :
		raise vs.Error(f"模块 {func_name} 的子参数 vs_t 的值无效")

	if ivtc_m == 1 :
		if not hasattr(core, "vivtc") :
			raise ModuleNotFoundError(f"模块 {func_name} 依赖错误：缺失插件，检查项目 vivtc")
	elif ivtc_m == 2 :
		if not hasattr(core, "tivtc") :
			raise ModuleNotFoundError(f"模块 {func_name} 依赖错误：缺失插件，检查项目 tivtc")

	core.num_threads = vs_t
	if fps_in <= 24 or fps_in >= 31 or (fps_in >= 26 and fps_in <= 29) :
		raise Exception("源帧率无效，已临时中止。")
	else :

		if ivtc_m == 1 :
			if fps_in > 24 and fps_in < 26 :
				output = core.vivtc.VDecimate(clip=input, cycle=25)
			elif fps_in > 29 and fps_in < 31 :
				output = core.vivtc.VDecimate(clip=input, cycle=5)
		elif ivtc_m == 2 :
			cut0 = core.std.AssumeFPS(clip=input, fpsnum=fps_in * 1e6, fpsden=1e6)
			cut1 = core.tivtc.TDecimate(clip=cut0, mode=7, rate=24 / 1.001)
			output = core.std.AssumeFPS(clip=cut1, fpsnum=24000, fpsden=1001)

	return output

##################################################
## MOD HAvsFunc (2a9a4770b7d014e1f528ef5f462f6e6e22564b7c)
## 抗镜头抖动
##################################################

def STAB_STD(
	input : vs.VideoNode,
	vs_t : int = vs_thd_dft,
) -> vs.VideoNode :

	func_name = "STAB_STD"
	if not isinstance(input, vs.VideoNode) :
		raise vs.Error(f"模块 {func_name} 的子参数 input 的值无效")
	if not isinstance(vs_t, int) or vs_t > vs_thd_init :
		raise vs.Error(f"模块 {func_name} 的子参数 vs_t 的值无效")

	if not hasattr(core, "focus2") :
		raise ModuleNotFoundError(f"模块 {func_name} 依赖错误：缺失插件，检查项目 focus2")
	if not hasattr(core, "mv") :
		raise ModuleNotFoundError(f"模块 {func_name} 依赖错误：缺失插件，检查项目 mv")
	if not hasattr(core, "misc") :
		raise ModuleNotFoundError(f"模块 {func_name} 依赖错误：缺失插件，检查项目 misc")
	if not hasattr(core, "rgvs") :
		raise ModuleNotFoundError(f"模块 {func_name} 依赖错误：缺失插件，检查项目 rgvs")

	core.num_threads = vs_t

	threshold = 255 << (input.format.bits_per_sample - 8)
	temp = input.focus2.TemporalSoften2(7, threshold, threshold, 25, 2)
	inter = core.std.Interleave([core.rgvs.Repair(temp, input.focus2.TemporalSoften2(1, threshold, threshold, 25, 2), mode=[1]), input])
	mdata = inter.mv.DepanEstimate(trust=0, dxmax=4, dymax=4)
	mdata_fin = inter.mv.DepanCompensate(data=mdata, offset=-1, mirror=15)
	output = mdata_fin[::2]

	return output

##################################################
## PORT HAvsFunc (0f6a7d9d9712d59b4e74e1e570fc6e3a526917f9)
## 抗镜头抖动
##################################################

def STAB_HQ(
	input : vs.VideoNode,
	vs_t : int = vs_thd_dft,
) -> vs.VideoNode :

	func_name = "STAB_HQ"
	if not isinstance(input, vs.VideoNode) :
		raise vs.Error(f"模块 {func_name} 的子参数 input 的值无效")
	if not isinstance(vs_t, int) or vs_t > vs_thd_init :
		raise vs.Error(f"模块 {func_name} 的子参数 vs_t 的值无效")

	if not hasattr(core, "mv") :
		raise ModuleNotFoundError(f"模块 {func_name} 依赖错误：缺失插件，检查项目 mv")
	if not hasattr(core, "misc") :
		raise ModuleNotFoundError(f"模块 {func_name} 依赖错误：缺失插件，检查项目 misc")
	if not hasattr(core, "rgvs") :
		raise ModuleNotFoundError(f"模块 {func_name} 依赖错误：缺失插件，检查项目 rgvs")

	core.num_threads = vs_t

	def _scdetect(clip: vs.VideoNode, threshold: float = 0.1) -> vs.VideoNode :
		def _copy_property(n: int, f: list[vs.VideoFrame]) -> vs.VideoFrame :
			fout = f[0].copy()
			fout.props["_SceneChangePrev"] = f[1].props["_SceneChangePrev"]
			fout.props["_SceneChangeNext"] = f[1].props["_SceneChangeNext"]
			return fout
		sc = clip
		if clip.format.color_family == vs.RGB :
			sc = core.resize.Point(clip=clip, format=vs.GRAY8, matrix_s="709")
		sc = sc.misc.SCDetect(threshold=threshold)
		if clip.format.color_family == vs.RGB :
			sc = clip.std.ModifyFrame(clips=[clip, sc], selector=_copy_property)
		return sc

	## PORT HAvsFunc (17b62a0b2695e0950e0899dba466ab42327c32c9)
	def _average_frames(clip: vs.VideoNode, weights: typing.Union[float, typing.Sequence[float]], scenechange: typing.Optional[float] = None, planes: typing.Optional[typing.Union[int, typing.Sequence[int]]] = None) -> vs.VideoNode :
		if scenechange :
			clip = _scdetect(clip, scenechange)
		return clip.std.AverageFrames(weights=weights, scenechange=scenechange, planes=planes)

	def _Stab(clp, dxmax=4, dymax=4, mirror=0) :
		temp = _average_frames(clp, weights=[1] * 15, scenechange=25 / 255)
		inter = core.std.Interleave([core.rgvs.Repair(temp, _average_frames(clp, weights=[1] * 3, scenechange=25 / 255), mode=[1]), clp])
		mdata = inter.mv.DepanEstimate(trust=0, dxmax=dxmax, dymax=dymax)
		last = inter.mv.DepanCompensate(data=mdata, offset=-1, mirror=mirror)
		return last[::2]

	output = _Stab(clp=input, mirror=15)

	return output

##################################################
## 自定义ONNX模型（仅支持放大类）
##################################################

def UAI_DML(
	input : vs.VideoNode,
	clamp : bool = False,
	model_pth : str = "",
	fp16_qnt : bool = True,
	gpu : typing.Literal[0, 1, 2] = 0,
	gpu_t : int = 2,
	vs_t : int = vs_thd_dft,
) -> vs.VideoNode :

	func_name = "UAI_DML"
	if not isinstance(input, vs.VideoNode) :
		raise vs.Error(f"模块 {func_name} 的子参数 input 的值无效")
	if not isinstance(clamp, bool) :
		raise vs.Error(f"模块 {func_name} 的子参数 clamp 的值无效")
	if len(model_pth) <= 5 :
		raise vs.Error(f"模块 {func_name} 的子参数 model_pth 的值无效")
	if not isinstance(fp16_qnt, bool) :
		raise vs.Error(f"模块 {func_name} 的子参数 fp16_qnt 的值无效")
	if gpu not in [0, 1, 2] :
		raise vs.Error(f"模块 {func_name} 的子参数 gpu 的值无效")
	if not isinstance(gpu_t, int) or gpu_t <= 0 :
		raise vs.Error(f"模块 {func_name} 的子参数 gpu_t 的值无效")
	if not isinstance(vs_t, int) or vs_t > vs_thd_init :
		raise vs.Error(f"模块 {func_name} 的子参数 vs_t 的值无效")

	if not hasattr(core, "ort") :
		raise ModuleNotFoundError(f"模块 {func_name} 依赖错误：缺失插件，检查项目 ort")
	if clamp :
		if not hasattr(core, "akarin") :
			raise ModuleNotFoundError(f"模块 {func_name} 依赖错误：缺失插件，检查项目 akarin")

	plg_dir = os.path.dirname(core.ort.Version()["path"]).decode()
	mdl_pth_rel = plg_dir + "/models/" + model_pth
	if not os.path.exists(mdl_pth_rel) and not os.path.exists(model_pth) :
		raise vs.Error(f"模块 {func_name} 所请求的模型缺失")
	mdl_pth = mdl_pth_rel if os.path.exists(mdl_pth_rel) else model_pth

	global vsmlrt
	if vsmlrt is None :
		try :
			import vsmlrt
		except ImportError :
			raise ImportError(f"模块 {func_name} 依赖错误：缺失脚本 vsmlrt")
	if LooseVersion(vsmlrt.__version__) < LooseVersion("3.15.25") :
		raise ImportError(f"模块 {func_name} 依赖错误：缺失脚本 vsmlrt 的版本号过低，至少 3.15.25")

	core.num_threads = vs_t
	fmt_in = input.format.id
	colorlv = getattr(input.get_frame(0).props, "_ColorRange", 0)

	fp16_mdl = None
	check_mdl = ONNX_ANZ(input=mdl_pth)
	if check_mdl == 1 :
		fp16_mdl = False
	elif check_mdl == 10 :
		fp16_mdl = True
	else :
		raise vs.Error(f"模块 {func_name} 的输入模型的输入精度不受支持")
	if fp16_mdl :
		fp16_qnt = False   ### ort对于fp16模型自动使用对应的IO

	clip = core.resize.Bilinear(clip=input, format=vs.RGBH if fp16_mdl else vs.RGBS, matrix_in_s="709")
	if clamp :
		clip = core.akarin.Expr(clips=clip, expr="x 0 1 clamp")
	be_param = vsmlrt.BackendV2.ORT_DML(device_id=gpu, num_streams=gpu_t, fp16=fp16_qnt)
	infer = vsmlrt.inference(clips=clip, network_path=mdl_pth, backend=be_param)
	output = core.resize.Bilinear(clip=infer, format=fmt_in, matrix_s="709", range=1 if colorlv==0 else None)

	return output

##################################################
## 自定义ONNX模型（仅支持放大类）
##################################################

def UAI_MIGX(
	input : vs.VideoNode,
	clamp : bool = False,
	model_pth : str = "",
	fp16_qnt : bool = True,
	exh_tune : bool = False,
	gpu : typing.Literal[0, 1, 2] = 0,
	gpu_t : int = 2,
	vs_t : int = vs_thd_dft,
) -> vs.VideoNode :

	func_name = "UAI_MIGX"
	if not isinstance(input, vs.VideoNode) :
		raise vs.Error(f"模块 {func_name} 的子参数 input 的值无效")
	if not isinstance(clamp, bool) :
		raise vs.Error(f"模块 {func_name} 的子参数 clamp 的值无效")
	if len(model_pth) <= 5 :
		raise vs.Error(f"模块 {func_name} 的子参数 model_pth 的值无效")
	if not isinstance(fp16_qnt, bool) :
		raise vs.Error(f"模块 {func_name} 的子参数 fp16_qnt 的值无效")
	if not isinstance(exh_tune, bool) :
		raise vs.Error(f"模块 {func_name} 的子参数 exh_tune 的值无效")
	if gpu not in [0, 1, 2] :
		raise vs.Error(f"模块 {func_name} 的子参数 gpu 的值无效")
	if not isinstance(gpu_t, int) or gpu_t <= 0 :
		raise vs.Error(f"模块 {func_name} 的子参数 gpu_t 的值无效")
	if not isinstance(vs_t, int) or vs_t > vs_thd_init :
		raise vs.Error(f"模块 {func_name} 的子参数 vs_t 的值无效")

	if not hasattr(core, "migx") :
		raise ModuleNotFoundError(f"模块 {func_name} 依赖错误：缺失插件，检查项目 migx")
	if clamp :
		if not hasattr(core, "akarin") :
			raise ModuleNotFoundError(f"模块 {func_name} 依赖错误：缺失插件，检查项目 akarin")

	plg_dir = os.path.dirname(core.migx.Version()["path"]).decode()
	mdl_pth_rel = plg_dir + "/models/" + model_pth
	if not os.path.exists(mdl_pth_rel) and not os.path.exists(model_pth) :
		raise vs.Error(f"模块 {func_name} 所请求的模型缺失")
	mdl_pth = mdl_pth_rel if os.path.exists(mdl_pth_rel) else model_pth

	global vsmlrt
	if vsmlrt is None :
		try :
			import vsmlrt
		except ImportError :
			raise ImportError(f"模块 {func_name} 依赖错误：缺失脚本 vsmlrt")
	if LooseVersion(vsmlrt.__version__) < LooseVersion("3.15.25") :
		raise ImportError(f"模块 {func_name} 依赖错误：缺失脚本 vsmlrt 的版本号过低，至少 3.15.25")

	core.num_threads = vs_t
	fmt_in = input.format.id
	colorlv = getattr(input.get_frame(0).props, "_ColorRange", 0)

	fp16_mdl = None
	check_mdl = ONNX_ANZ(input=mdl_pth)
	if check_mdl == 1 :
		fp16_mdl = False
	elif check_mdl == 10 :
		fp16_mdl = True
	else :
		raise vs.Error(f"模块 {func_name} 的输入模型的输入精度不受支持")
	if fp16_mdl :
		fp16_qnt = True   ### 量化精度与模型精度匹配

	clip = core.resize.Bilinear(clip=input, format=vs.RGBH if fp16_qnt else vs.RGBS, matrix_in_s="709")
	if clamp :
		clip = core.akarin.Expr(clips=clip, expr="x 0 1 clamp")
	be_param = vsmlrt.BackendV2.MIGX(
		fp16=fp16_qnt, exhaustive_tune=exh_tune, opt_shapes=[clip.width, clip.height],
		device_id=gpu, num_streams=gpu_t, short_path=True)
	infer = vsmlrt.inference(clips=clip, network_path=mdl_pth, backend=be_param)
	output = core.resize.Bilinear(clip=infer, format=fmt_in, matrix_s="709", range=1 if colorlv==0 else None)

	return output

##################################################
## 自定义ONNX模型（仅支持放大类）
##################################################

def UAI_NV_TRT(
	input : vs.VideoNode,
	clamp : bool = False,
	model_pth : str = "",
	opt_lv : typing.Literal[0, 1, 2, 3, 4, 5] = 3,
	cuda_opt : typing.List[int] = [0, 0, 0],
	int8_qnt : bool = False,
	fp16_qnt : bool = True,
	gpu : typing.Literal[0, 1, 2] = 0,
	gpu_t : int = 2,
	st_eng : bool = False,
	res_opt : typing.List[int] = None,
	res_max : typing.List[int] = None,
	ws_size : int = 0,
	vs_t : int = vs_thd_dft,
	is_img : bool = False,	
) -> vs.VideoNode :

	func_name = "UAI_NV_TRT"
	if not isinstance(input, vs.VideoNode) :
		raise vs.Error(f"模块 {func_name} 的子参数 input 的值无效")
	if not isinstance(clamp, bool) :
		raise vs.Error(f"模块 {func_name} 的子参数 clamp 的值无效")
	if len(model_pth) <= 5 :
		raise vs.Error(f"模块 {func_name} 的子参数 model_pth 的值无效")
	if opt_lv not in [0, 1, 2, 3, 4, 5] :
		raise vs.Error(f"模块 {func_name} 的子参数 opt_lv 的值无效")
	if not (len(cuda_opt) == 3 and all(isinstance(num, int) and num in [0, 1] for num in cuda_opt)) :
		raise vs.Error(f"模块 {func_name} 的子参数 cuda_opt 的值无效")
	if not isinstance(int8_qnt, bool) :
		raise vs.Error(f"模块 {func_name} 的子参数 int8_qnt 的值无效")
	if not isinstance(fp16_qnt, bool) :
		raise vs.Error(f"模块 {func_name} 的子参数 fp16_qnt 的值无效")
	if gpu not in [0, 1, 2] :
		raise vs.Error(f"模块 {func_name} 的子参数 gpu 的值无效")
	if not isinstance(gpu_t, int) or gpu_t <= 0 :
		raise vs.Error(f"模块 {func_name} 的子参数 gpu_t 的值无效")
	if not isinstance(st_eng, bool) :
		raise vs.Error(f"模块 {func_name} 的子参数 st_eng 的值无效")
#	if st_eng :
#		if not (res_opt is None and res_max is None) :
#			raise vs.Error(f"模块 {func_name} 的子参数 res_opt 或 res_max 的值无效")
	if not st_eng :
		if not (isinstance(res_opt, list) and len(res_opt) == 2 and all(isinstance(i, int) for i in res_opt)) :
			raise vs.Error(f"模块 {func_name} 的子参数 res_opt 的值无效")
		if not (isinstance(res_max, list) and len(res_max) == 2 and all(isinstance(i, int) for i in res_max)) :
			raise vs.Error(f"模块 {func_name} 的子参数 res_max 的值无效")
	if not isinstance(ws_size, int) or ws_size < 0 :
		raise vs.Error(f"模块 {func_name} 的子参数 ws_size 的值无效")
	if not isinstance(vs_t, int) or vs_t > vs_thd_init :
		raise vs.Error(f"模块 {func_name} 的子参数 vs_t 的值无效")

	if not hasattr(core, "trt") :
		raise ModuleNotFoundError(f"模块 {func_name} 依赖错误：缺失插件，检查项目 trt")
	if clamp :
		if not hasattr(core, "akarin") :
			raise ModuleNotFoundError(f"模块 {func_name} 依赖错误：缺失插件，检查项目 akarin")

	plg_dir = os.path.dirname(core.trt.Version()["path"]).decode()
	mdl_pth_rel = plg_dir + "/models/" + model_pth
	if not os.path.exists(mdl_pth_rel) and not os.path.exists(model_pth) :
		raise vs.Error(f"模块 {func_name} 所请求的模型缺失")
	mdl_pth = mdl_pth_rel if os.path.exists(mdl_pth_rel) else model_pth

	global vsmlrt
	if vsmlrt is None :
		try :
			import vsmlrt
		except ImportError :
			raise ImportError(f"模块 {func_name} 依赖错误：缺失脚本 vsmlrt")
	if LooseVersion(vsmlrt.__version__) < LooseVersion("3.18.1") :
		raise ImportError(f"模块 {func_name} 依赖错误：缺失脚本 vsmlrt 的版本号过低，至少 3.18.1")

	core.num_threads = vs_t
	fmt_in = input.format.id if input.format.id != vs.GRAY8 else vs.RGB24
	colorlv = getattr(input.get_frame(0).props, "_ColorRange", 0) if not is_img else None

	fp16_mdl = None
	check_mdl = ONNX_ANZ(input=mdl_pth)
	if check_mdl == 1 :
		fp16_mdl = False
	elif check_mdl == 10 :
		fp16_mdl = True
	else :
		raise vs.Error(f"模块 {func_name} 的输入模型的输入精度不受支持")
	if fp16_mdl :
		fp16_qnt = True   ### 量化精度与模型精度匹配

	nv1, nv2, nv3 = [bool(num) for num in cuda_opt]
	if int8_qnt :
		fp16_qnt = True

	clip = core.resize.Bilinear(clip=input, format=vs.RGBH if fp16_qnt else vs.RGBS, matrix_in_s="709" if not is_img else None)
	if clamp :
		clip = core.akarin.Expr(clips=clip, expr="x 0 1 clamp")
	be_param = vsmlrt.BackendV2.TRT(
		builder_optimization_level=opt_lv, short_path=True, device_id=gpu,
		num_streams=gpu_t, use_cuda_graph=nv1, use_cublas=nv2, use_cudnn=nv3,
		int8=int8_qnt, fp16=fp16_qnt, tf32=False if fp16_qnt else True, output_format=1 if fp16_qnt else 0, workspace=None if ws_size < 128 else (ws_size if st_eng else ws_size * 2),
		static_shape=st_eng, min_shapes=[0, 0] if st_eng else [384, 384], opt_shapes=None if st_eng else res_opt, max_shapes=None if st_eng else res_max)
	infer = vsmlrt.inference(clips=clip, network_path=mdl_pth, backend=be_param)
	output = core.resize.Bilinear(clip=infer, format=fmt_in, matrix_s="709" if not is_img else None, range=1 if colorlv==0 else None)

	return output

##################################################
## 自定义MadVR渲染 # TODO
##################################################

def UVR_MAD(
	input : vs.VideoNode,
	ngu : typing.Literal[0, 1, 2, 3, 4] = 0,
	ngu_q : typing.Literal[1, 2, 3, 4] = 1,
	rca_lv : typing.Literal[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] = 0,
	rca_q : typing.Literal[1, 2, 3, 4] = 1,
#	uopts : typing.Optional[str] = None, # TODO
	vs_t : int = vs_thd_dft,
) -> vs.VideoNode :

	func_name = "UVR_MAD"
	if not isinstance(input, vs.VideoNode) :
		raise vs.Error(f"模块 {func_name} 的子参数 input 的值无效")
	if ngu not in [0, 1, 2, 3, 4] :
		raise vs.Error(f"模块 {func_name} 的子参数 ngu 的值无效")
	if ngu_q not in [1, 2, 3, 4] :
		raise vs.Error(f"模块 {func_name} 的子参数 ngu_q 的值无效")
	if rca_lv not in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] :
		raise vs.Error(f"模块 {func_name} 的子参数 rca_lv 的值无效")
	if rca_q not in [1, 2, 3, 4] :
		raise vs.Error(f"模块 {func_name} 的子参数 rca_q 的值无效")
	if not isinstance(vs_t, int) or vs_t > vs_thd_init :
		raise vs.Error(f"模块 {func_name} 的子参数 vs_t 的值无效")

	if not hasattr(core, "madvr") :
		raise ModuleNotFoundError(f"模块 {func_name} 依赖错误：缺失插件，检查项目 madvr")

	core.num_threads = vs_t
	w_in, h_in = input.width, input.height
	colorlv = getattr(input.get_frame(0).props, "_ColorRange", 0)
	fmt_in = input.format.id
	fmt_mad = [vs.YUV420P8, vs.YUV420P10, vs.YUV420P16, vs.YUV422P8, vs.YUV422P10, vs.YUV422P16, vs.YUV440P8, vs.YUV444P8, vs.YUV444P10, vs.YUV444P16]
	algo = (["nguAa", "nguSoft", "nguStandard", "nguSharp"][ngu - 1] + ["Low", "Medium", "High", "VeryHigh"][ngu_q - 1]) if ngu > 0 else None
	w_rs, h_rs = w_in * 2, h_in * 2
	quality = ["low", "medium", "high", "veryHigh"][rca_q - 1]

	param_size1 = ("upscale(newWidth=%d,newHeight=%d,algo=%s,sigmoidal=on)" % (w_rs, h_rs, algo)) if algo is not None else None
	param_other2 = ("rca(strength=%d,quality=%s)" % (rca_lv, quality)) if rca_lv > 0 else None
	param_format3 = "setOutputFormat(format=yuv444,bitdepth=10)"
	mad_param = []
	for var in [param_size1, param_other2, param_format3] :
		if var is not None :
			mad_param.append(var)

	if fmt_in not in fmt_mad :
		cut0 = core.resize.Bilinear(clip=input, format=vs.YUV444P10)
	else :
		cut0 = input
	output = core.madvr.Process(clip=cut0, commands=mad_param, adapter=False)
	if colorlv == 0 :
		output = core.resize.Bilinear(clip=output, range=1)

	return output

##################################################
##################################################
