
VLBI pipeline tutorial
Step 1:
生成listr，找possm scan / fring scan — 
fringe finder中段2min
检查：每个天线的观测时间，fringe finder 的天线覆盖
Step 1.5 (for L-band RFI) （step 1,2,3 = 0）
inspect_flag生成possm图，检查图像找需要flag的区域 — 
互相关图，找有问题的天线和if
自相关叠加/不叠加天线，找有问题的channel
写入 fgantennas; fgbif; fgeif; fgbchan; fgechan,设置 man_uvflg_flag=1
*clip_flag = 1自动去掉过高rfi
Step 2:
*目标源可自校准时尝试step=2
step 2.5 manual difmap imaging
生成phase calibrator的图像和模型 — 
1.flag坏数据
select i,if 找有问题的if
radplot n 找有问题的天线
vplot 看具体细节，如果amp差phase好可暂时保留
2.selfcal模型拟合
radplot看短基线模型与流量接近了即可开始selfcal
selfcal—mapplot—clean 多次phase-selfcal，还可通过改变 weighting看残差图成分是否剩余
gscale 仅此一次，如果差别很大可以记下来用在matxi中
selfcal true, true, interval (从大到小，单位-分钟) — 多次amp-selfcal。如果数据质量好，可以用最小interval（不设置）
Step 3:
每个源单独做，config信息需要注意修改对应 — 
fr_path fr_file 是difmap产出的结果
fr_name 是对应phase-cal的名字
dwin, rwin 是解的范围，对应delay(time)和rate(freq)，可以去除跳变，跑完后结合snplot结果看，可修改调整
