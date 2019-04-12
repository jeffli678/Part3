# encoding: utf-8
import wx
import os
import sys
import os.path
import json
import subprocess
import threading, time
import datetime
import platform
import re

version = 'v2.1'
oldFilePath=u''
nfileCount=1
stype='file'
convertProc=None
originalVideoWidth=0
originalVideoHeight=0
changeValueProgramatically=False
res_path = {}
reload(sys)
sys.setdefaultencoding( "utf-8" )


class MyFrame(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self, None, -1, u"Part3 " + version, size = (550, 700))
		panel = wx.Panel(self, -1)

		self.staticFileList=wx.StaticText(panel, -1, u"文件/文件夹：")
		self.fileCount=wx.StaticText(panel,-1,u"n个")
		self.fileText = wx.TextCtrl(panel, -1, "")

		self.staticVideo=wx.StaticText(panel,-1,u"视频：")
		self.videoEnabled=wx.CheckBox(panel,-1,u"启用")
		self.videoInfo=wx.StaticText(panel,-1,u"Video Info:")

		self.staticVideoEncoder=wx.StaticText(panel,-1,u"输出编码：")
		self.videoEncoderList=[u'copy',u'h264',u'libx265',u'prores',u'prores_ks',u'自动']
		self.videoEncoder=wx.ComboBox(panel,-1,choices=self.videoEncoderList)

		self.staticWidth=wx.StaticText(panel,-1,u"宽度：")
		self.videoWidthList=[u'自动','2048','1920','1280','720','480','320']
		self.videoWidth=wx.ComboBox(panel,-1,choices=self.videoWidthList,name='videoWidth')
		self.staticHeight=wx.StaticText(panel,-1,u"高度：")
		self.videoHeightList=[u'自动','1080','858','720','450','360','270']
		self.videoHeight=wx.ComboBox(panel,-1,choices=self.videoHeightList,name='videoHeight')
		self.constarinRatio=wx.CheckBox(panel,-1,u'保持宽高比')

		self.firstFramePlay=wx.CheckBox(panel,-1,u'首帧播放')

		self.staticProresQuality=wx.StaticText(panel,-1,u"质量：")
		self.proresQualityList=[u'0: Proxy',u'1: LT',u'2: Normal',u'3: HQ']
		self.proresQuality=wx.ComboBox(panel,-1,choices=self.proresQualityList)

		self.staticVideoCRF=wx.StaticText(panel,-1,u"质量：")
		self.videoCRF=wx.SpinCtrl(panel,-1,"18",min=0,max=51,size=(50,25))
		self.videoCRF.SetToolTip(u'建议取值18-28之间，数字越大，质量越差')
		self.staticVideoPreset=wx.StaticText(panel,-1,u"编码速度：")
		self.videoPresetList=[u'veryfast',u'faster',u'fast',u'medium']
		self.videoPreset=wx.ComboBox(panel,-1,choices=self.videoPresetList)
		self.staticVideoMaxRate=wx.StaticText(panel,-1,u"最大码率：")
		self.videoMaxRate = wx.TextCtrl(panel, -1, u"0",size=(50,25))
		self.staticVideoRateUnit=wx.StaticText(panel,-1,u"Mb/s")

		self.staticVideoExtra=wx.StaticText(panel,-1,u"额外参数：")
		self.videoExtra=wx.TextCtrl(panel,-1,"")
		self.videoExtra.SetToolTip(u'-r rate 帧率\n-vframes number 要转换的帧数量\n-movflags +faststart 首帧播放')



		self.staticAudio=wx.StaticText(panel,-1,u"音频：")
		self.audioEnabled=wx.CheckBox(panel,-1,u"启用")
		self.audioReplace=wx.CheckBox(panel,-1,u"替换")
		self.audioInfo=wx.StaticText(panel,-1,u"Audio Info:")

		self.staticAudioEncoder=wx.StaticText(panel,-1,u"输出编码：")
		self.audioEncoderList=[u'copy',u'aac',u'pcm_s16le',u'flac',u'自动']
		self.audioEncoder=wx.ComboBox(panel,-1,choices=self.audioEncoderList)
		self.staticAudioBitrate=wx.StaticText(panel,-1,u'码率：')
		self.audioBitrate = wx.TextCtrl(panel, -1, u"0",size=(50,25))
		self.staticAudioRateUnit=wx.StaticText(panel,-1,u"Mb/s")

		self.staticAudioExtra=wx.StaticText(panel,-1,u"额外参数：")
		self.audioExtra=wx.TextCtrl(panel,-1,"")

		self.staticContainer=wx.StaticText(panel,-1,u"封装格式：")
		self.containerList=[u'MP4',u'MOV',u'AAC',u'WAV',u'FLAC', u'MP3']
		self.container=wx.ComboBox(panel,-1,choices=self.containerList,name='container')

		self.overWrite=wx.CheckBox(panel,-1,u'覆盖重名文件')

		self.staticCMD=wx.StaticText(panel,-1,u"命令行：")
		self.progressBar = wx.Gauge(panel, -1, size = (150, 20), range = 100 )
		self.remainTime = wx.StaticText(panel, -1, u"剩余时间:")
		self.cmdText=wx.TextCtrl(panel,-1,"ffmpeg -i",style=wx.TE_MULTILINE)


		self.btn=wx.Button(panel,label="Go!")


		# file related
		filehBox=wx.BoxSizer()
		filehBox.Add(self.staticFileList,0,wx.LEFT|wx.ALIGN_CENTER,5)
		filehBox.Add(self.fileCount,1,wx.LEFT|wx.ALIGN_CENTER,10)

		filevBox=wx.BoxSizer(wx.VERTICAL)
		filevBox.Add(filehBox,0,wx.ALL,10)
		filevBox.Add(self.fileText,1,wx.EXPAND|wx.LEFT|wx.RIGHT,15)

		# video related
		vhBoxEnable=wx.BoxSizer()
		vhBoxEnable.Add(self.staticVideo,0,wx.LEFT|wx.ALIGN_CENTER,10)
		vhBoxEnable.Add(self.videoEnabled,0,wx.LEFT|wx.ALIGN_CENTER,10)
		vhBoxEnable.Add(self.videoInfo,0,wx.LEFT|wx.ALIGN_CENTER,10)

		vhBoxEncoder=wx.BoxSizer()
		vhBoxEncoder.Add(self.staticVideoEncoder,0,wx.LEFT|wx.ALIGN_CENTER,10)
		vhBoxEncoder.Add(self.videoEncoder,0,wx.LEFT|wx.ALIGN_CENTER,10)
		vhBoxEncoder.Add(self.staticProresQuality,0,wx.LEFT|wx.ALIGN_CENTER,20)
		vhBoxEncoder.Add(self.proresQuality,0,wx.LEFT|wx.ALIGN_CENTER,10)

		vhBoxSize=wx.BoxSizer()
		vhBoxSize.Add(self.staticWidth,0,wx.LEFT|wx.ALIGN_CENTER,10)
		vhBoxSize.Add(self.videoWidth,0,wx.LEFT|wx.ALIGN_CENTER,10)
		vhBoxSize.Add(self.staticHeight,0,wx.LEFT|wx.ALIGN_CENTER,10)
		vhBoxSize.Add(self.videoHeight,0,wx.LEFT|wx.ALIGN_CENTER,10)
		vhBoxSize.Add(self.constarinRatio,0,wx.LEFT|wx.ALIGN_CENTER,10)
		vhBoxSize.Add(self.firstFramePlay,0,wx.LEFT|wx.ALIGN_CENTER,10)

		vhBoxPreset=wx.BoxSizer()
		vhBoxPreset.Add(self.staticVideoCRF,0,wx.LEFT|wx.ALIGN_CENTER,10)
		vhBoxPreset.Add(self.videoCRF,0,wx.LEFT|wx.ALIGN_CENTER,10)
		vhBoxPreset.Add(self.staticVideoPreset,0,wx.LEFT|wx.ALIGN_CENTER,10)
		vhBoxPreset.Add(self.videoPreset,0,wx.LEFT|wx.ALIGN_CENTER,10)
		vhBoxPreset.Add(self.staticVideoMaxRate,0,wx.LEFT|wx.ALIGN_CENTER,10)
		vhBoxPreset.Add(self.videoMaxRate,0,wx.LEFT|wx.ALIGN_CENTER,10)
		vhBoxPreset.Add(self.staticVideoRateUnit,0,wx.LEFT|wx.ALIGN_CENTER,10)

		vhBoxExtra=wx.BoxSizer()
		vhBoxExtra.Add(self.staticVideoExtra,0,wx.LEFT|wx.ALIGN_CENTER,10)
		vhBoxExtra.Add(self.videoExtra,1,wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER,10)

		vvBox=wx.BoxSizer(wx.VERTICAL)
		vvBox.Add(vhBoxEnable,0,wx.EXPAND|wx.ALL,10)
		vvBox.Add(vhBoxEncoder,0,wx.EXPAND|wx.BOTTOM|wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER,10)
		vvBox.Add(vhBoxSize,0,wx.EXPAND|wx.BOTTOM|wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER,10)
		vvBox.Add(vhBoxPreset,0,wx.EXPAND|wx.BOTTOM|wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER,10)
		vvBox.Add(vhBoxExtra,0,wx.EXPAND|wx.BOTTOM|wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER,10)

		# audio related
		ahBoxEnable=wx.BoxSizer()
		ahBoxEnable.Add(self.staticAudio,0,wx.LEFT|wx.ALIGN_CENTER,10)
		ahBoxEnable.Add(self.audioEnabled,0,wx.LEFT|wx.ALIGN_CENTER,10)
		ahBoxEnable.Add(self.audioReplace,0,wx.LEFT|wx.ALIGN_CENTER,10)
		ahBoxEnable.Add(self.audioInfo,0,wx.LEFT|wx.ALIGN_CENTER,10)

		ahBoxEncoder=wx.BoxSizer()
		ahBoxEncoder.Add(self.staticAudioEncoder,0,wx.LEFT|wx.ALIGN_CENTER,10)
		ahBoxEncoder.Add(self.audioEncoder,0,wx.LEFT|wx.ALIGN_CENTER,10)
		ahBoxEncoder.Add(self.staticAudioBitrate,0,wx.LEFT|wx.ALIGN_CENTER,20)
		ahBoxEncoder.Add(self.audioBitrate,0,wx.LEFT|wx.ALIGN_CENTER,10)
		ahBoxEncoder.Add(self.staticAudioRateUnit,0,wx.LEFT|wx.ALIGN_CENTER,10)

		ahBoxExtra=wx.BoxSizer()
		ahBoxExtra.Add(self.staticAudioExtra,0,wx.LEFT|wx.ALIGN_CENTER,10)
		ahBoxExtra.Add(self.audioExtra,1,wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER,10)

		avBox=wx.BoxSizer(wx.VERTICAL)
		avBox.Add(ahBoxEnable,0,wx.EXPAND|wx.ALL,border=10)
		avBox.Add(ahBoxEncoder,0,wx.EXPAND|wx.BOTTOM|wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER,border=10)
		avBox.Add(ahBoxExtra,0,wx.EXPAND|wx.BOTTOM|wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER,border=10)

		chBox=wx.BoxSizer()
		chBox.Add(self.staticContainer,0,wx.LEFT|wx.ALIGN_CENTER,20)
		chBox.Add(self.container,0,wx.ALL|wx.ALIGN_CENTER,5)
		chBox.Add(self.overWrite,0,wx.LEFT|wx.ALIGN_CENTER,30)

		cmdBox=wx.BoxSizer()
		cmdBox.Add(self.staticCMD,0,wx.LEFT|wx.ALIGN_CENTER,5)
		cmdBox.Add(self.progressBar,0,wx.LEFT|wx.ALIGN_CENTER,80)
		cmdBox.Add(self.remainTime,0,wx.LEFT|wx.ALIGN_CENTER,20)

		# global
		globalBox=wx.BoxSizer(wx.VERTICAL)
		globalBox.Add(filevBox,0,wx.EXPAND|wx.ALL,10)
		globalBox.Add(vvBox,0,wx.EXPAND|wx.ALL,5)
		globalBox.Add(avBox,0,wx.EXPAND|wx.ALL,5)
		globalBox.Add(chBox,0,wx.EXPAND|wx.ALL,5)
		globalBox.Add(cmdBox,0,wx.EXPAND|wx.ALL,5)
		globalBox.Add(self.cmdText,1,wx.EXPAND|wx.ALL,10)
		globalBox.Add(self.btn,0,wx.EXPAND|wx.ALL,10)

		panel.SetSizer(globalBox)
		panel.Layout()

		try:
			icon = wx.Icon(res_path['lollipop'], wx.BITMAP_TYPE_ICO)
			self.SetIcon(icon)
		except Exception as e:
			pass


def platformEncode(cmd):
	sys_str = platform.system()
	if sys_str == 'Windows':
		return cmd.encode('gbk')
	else:
		return cmd.encode('utf-8')

def updateInfo(filePath):

	global originalVideoWidth,originalVideoHeight
	originalVideoWidth=0
	originalVideoHeight=0

	# cmd='ffprobe -v quiet -print_format json -show_format -show_streams "%s" > mediaInfo.json' % filePath
	cmd=('"%s" -v quiet -print_format json -show_format -show_streams "%s"') % (res_path['ffprobe'], filePath)
	cmd = platformEncode(cmd)
	ffprobe_proc = subprocess.Popen(cmd, shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
	(stdoutdata, stderrdata) = ffprobe_proc.communicate()
	mediaInfo = json.loads(stdoutdata)

	frame.videoInfo.SetLabel("")
	frame.audioInfo.SetLabel("")

	for s in mediaInfo['streams']:
		if s['codec_type'] == 'video':
			videoInfoStr=s['codec_name']
			if 'pix_fmt' in s and s['pix_fmt']=='bgra':
				videoInfoStr+='(alpha)'

			if s['codec_name'] == 'prores':
				if 'pix_fmt' in s:
					videoInfoStr +='(%s)' % s['pix_fmt']

			originalVideoWidth=int(s['width'])
			originalVideoHeight=int(s['height'])
			videoInfoStr+=', '+str(originalVideoWidth)+'*'+str(originalVideoHeight)+', '+s['display_aspect_ratio']
			
			if 'avg_frame_rate' in s:
				fr=s['avg_frame_rate']
				(a,b)=fr.split('/')
				if int(b)==0:
					b=1

				fps=float(a)/float(b)
				if int(fps)==fps:
					fps=int(fps)
				else:
					fps=round(fps,3)
				videoInfoStr+=', '+str(fps)+'fps'

			if 'bit_rate' in s:
				br=s['bit_rate']
				br=float(br)/1000
				if(br>1000):
					br=str(round(br/1000,2))+'Mb/s'
				else:
					br=str(round(br,2))+'Kb/s'
				videoInfoStr+=', '+br

			if 'duration' in s:
				sDuration=float(s['duration'])
				second=int(sDuration)
				miliSecond=sDuration-second
				hour=minute=0
				if(second>60):
					minute=int(second/60)
					second=second-minute*60
					if minute>60:
						hour=int(minute/60)
						minute=minute-hour*60

				videoInfoStr+=' ,'
				if hour>0:
					if hour<10 :	videoInfoStr+='0'
					videoInfoStr+=str(hour)+':'
				else:
					videoInfoStr+='00:'
				if minute>0:
					if minute<10 :	videoInfoStr+='0'
					videoInfoStr+=str(minute)+':'
				else:
					videoInfoStr+='00:'
				if second>0:
					if second<10 :	videoInfoStr+='0'
					videoInfoStr+=str(second)+'.'
				else:
					videoInfoStr+='00.'
				videoInfoStr+=str(round(miliSecond,3))[2:]	


			frame.videoInfo.SetLabel(videoInfoStr)

		elif s['codec_type'] == 'audio':
			audioInfoStr=s['codec_name']+', '+str(float(s['sample_rate'])/1000)+'kHz'

			if 'channel_layout' in s:
				audioInfoStr+=', '+s['channel_layout']
			else:
				if 'channels' in s and s['channels']==1:
					audioInfoStr+=', '+'mono'

			if 'bit_rate' in s:
				# audioInfoStr+=', '+str(float(s['bit_rate'])/1000)+'kb/s'
				br=s['bit_rate']
				br=float(br)/1000
				if(br>1000):
					br=str(round(br/1000,2))+'Mb/s'
				else:
					br=str(round(br,2))+'Kb/s'
				audioInfoStr+=', '+br

			frame.audioInfo.SetLabel(audioInfoStr)

			# checkFormatCompat()


def getFileList(fileStr):

	fileList=[]

	fileStr=frame.fileText.GetValue()

	stype="N/A"
	if not os.path.exists(fileStr):
		nfileCount=0
	else:
		if os.path.isfile(fileStr):
			nfileCount=1
			fileList=[fileStr]
			stype='file'
			updateInfo(fileStr)
		else:
			fileList=[os.path.join(fileStr,file) for file in os.listdir(fileStr) \
					if (os.path.isfile(os.path.join(fileStr,file)) and not file.startswith('.'))]
			nfileCount=len(fileList)
			stype='folder'
			# print(fileList[0])
			updateInfo(fileList[0])
	
	frame.fileCount.SetLabel(str(nfileCount)+u'个')
	return (nfileCount,stype)

def findNextUsable(boverWrite,part1,part2):
	if boverWrite or (not os.path.exists(part1+part2)):
		return part1+part2
	else:
		iter=1
		while  True:
			testPath=part1+'-'+str(iter)+part2
			if not os.path.exists(testPath):
				return testPath
			iter+=1

def updateVideoSize(event):

	global changeValueProgramatically
	if changeValueProgramatically: return

	if originalVideoWidth==0 or originalVideoHeight==0:
		return

	evtObjName=event.GetEventObject().GetName()
	widthStr=frame.videoWidth.GetValue()
	heightStr=frame.videoHeight.GetValue()

	if evtObjName=='videoHeight' and heightStr==u'自动':
		changeValueProgramatically=True
		frame.videoWidth.SetValue(u'自动')
		changeValueProgramatically=False
		updateCmd(event)
		return
	if evtObjName=='videoWidth' and widthStr==u'自动':
		changeValueProgramatically=True
		frame.videoHeight.SetValue(u'自动')
		changeValueProgramatically=False
		updateCmd(event)
		return

	constarinRatio=frame.constarinRatio.GetValue()	

	try:
		newWidth=int(widthStr)
	except:
		newWidth=0

	try:
		newHeight=int(heightStr)
	except:
		newHeight=0

	if newWidth==0 and newHeight==0:
		return

	# not already correct
	if constarinRatio and newWidth*originalVideoHeight!=newHeight*originalVideoWidth:
		if evtObjName=='videoHeight':
			newWidth=int(newHeight*originalVideoWidth/originalVideoHeight)
			if newWidth%2 != 0:
				newWidth+=1
			changeValueProgramatically=True
			frame.videoWidth.SetValue(str(newWidth))
			frame.videoHeight.SetValue(str(newHeight))
			changeValueProgramatically=False
		# elif evtObjName=='videoWidth':
		else:
			newHeight=int(newWidth*originalVideoHeight/originalVideoWidth)
			if newHeight%2 != 0:
				newHeight+=1
			changeValueProgramatically=True
			frame.videoHeight.SetValue(str(newHeight))
			frame.videoWidth.SetValue(str(newWidth))
			changeValueProgramatically=False
			


	updateCmd(event)

def checkDivideBy2(event):

	print('checkDivideBy2')

	global changeValueProgramatically
	if changeValueProgramatically==True: 
		return

	newWidth=frame.videoWidth.GetValue()
	try:
		newWidth=int(newWidth)
	except:
		newWidth=0
	if newWidth%2==1:
		changeValueProgramatically=True
		# frame.videoWidth.SetFocus()
		frame.videoWidth.SetValue(str(newWidth+1))
		changeValueProgramatically=False
	
	newHeight=frame.videoHeight.GetValue()
	try:
		newHeight=int(newHeight)
	except:
		newHeight=0
	if newHeight%2==1:
		changeValueProgramatically=True
		# frame.videoHeight.SetFocus()
		frame.videoHeight.SetValue(str(newHeight+1))

		changeValueProgramatically=False


def updateCmd(event):

	# call getFileList, which calls updateInfo, before checkFormatCompat
	# Otherwise, it will still check the old-of-date info
	inputPathStr=frame.fileText.GetValue()
	newInputPathStr=inputPathStr.replace('"','')
	if newInputPathStr != inputPathStr:
		inputPathStr = newInputPathStr
		frame.fileText.SetValue(inputPathStr)
	
	# file path actually changes
	global oldFilePath,nfileCount,stype
	if oldFilePath != inputPathStr:
		oldFilePath = inputPathStr
		(nfileCount,stype)=getFileList(inputPathStr)

	checkFormatCompat(event)

	cmd='%s' + '"' + res_path['ffmpeg'] +'"' + ' -hide_banner -i "%s"'

	if frame.audioReplace.GetValue() == wx.CHK_CHECKED:
		audioReplaceFile=frame.audioExtra.GetValue()
		newAudioReplaceFile=audioReplaceFile.replace('"','')
		if newAudioReplaceFile != audioReplaceFile:
			audioReplaceFile=newAudioReplaceFile
			frame.audioExtra.SetValue(audioReplaceFile)

		if audioReplaceFile != "":
			cmd+=' -i "'+audioReplaceFile+'"'
		pass

	# overwrite
	boverWrite= False
	if frame.overWrite.GetValue() == wx.CHK_CHECKED:
		cmd+=' -y'
		boverWrite=True

	# video enabled
	if frame.videoEnabled.GetValue() == wx.CHK_CHECKED:
		vcodecStr=frame.videoEncoder.GetValue()
		if vcodecStr != u'自动':
			cmd+=' -vcodec '+vcodecStr

		# h264/h265 related
		if vcodecStr == u'h264' or vcodecStr == u'libx265':
			cmd+=' -crf '+ str(frame.videoCRF.GetValue())
			cmd+=' -preset '+ frame.videoPreset.GetValue()

			maxRateStr=frame.videoMaxRate.GetValue()
			if maxRateStr!="":
				maxRate=float(maxRateStr)
				if maxRate > 0:
					cmd+=' -maxrate '+ str(maxRate) + 'M -bufsize '+str(2*maxRate) +'M'

			cmd+=' -pix_fmt yuv420p'

		# prores related
		if vcodecStr == u'prores':
			cmd += ' -profile:v '+frame.proresQuality.GetValue()[0]

		if vcodecStr == u'prores_ks':
			# cmd += ' -pix_fmt yuva444p10le'
			cmd+= ' -profile:v 4444'

		# video frame size
		if vcodecStr!=u'copy':
			videoWidth=frame.videoWidth.GetValue()
			videoHeight=frame.videoHeight.GetValue()
			if videoWidth!=u'自动' and videoHeight!=u'自动':
				cmd+=' -s '+videoWidth+'*'+frame.videoHeight.GetValue()

		extra=frame.videoExtra.GetValue()
		if extra != "":
			cmd+=' '+ extra
	else:
		cmd+=' -vn'

	if frame.firstFramePlay.GetValue() == wx.CHK_CHECKED:
		cmd += ' -movflags +faststart'

	# audio enabled
	if frame.audioEnabled.GetValue() == wx.CHK_CHECKED:
		acodecStr=frame.audioEncoder.GetValue()
		if acodecStr != u'自动':
			cmd+=' -acodec '+acodecStr

		audioBitrateStr=frame.audioBitrate.GetValue()
		if audioBitrateStr!="":
			audioBitrate=float(audioBitrateStr)
			if audioBitrate > 0:
				cmd+=' -b:a '+ str(audioBitrate) + 'M'

		# if replace audio file is enabled
		# then audioExtra contains the path of the new audio file
		# no more extra parameters here
		if frame.audioReplace.GetValue() != wx.CHK_CHECKED:
			extra=frame.audioExtra.GetValue()
			if extra != "":
				cmd+=' '+ extra
	else:
		cmd+=' -an'

	#container
	outputExt=frame.container.GetValue()

	cmd+=' "%s"'

	if stype == 'N/A':
		frame.fileCount.SetLabel(u'无效路径')
		return

	if stype == 'file':		
		(inputPath,inputExt)=os.path.splitext(inputPathStr)
		outFileName=findNextUsable(boverWrite,inputPath+'-converted','.'+outputExt)
		cmd= cmd % ('',inputPathStr,outFileName)
	else:
		outDir=os.path.join(inputPathStr,'converted')
		outDir=findNextUsable(boverWrite,outDir,'')
		# if not os.path.exists(outDir):
		# 	os.mkdir(outDir)

		sys_str = platform.system()
		if sys_str == 'Windows':

			# cmd /c mkdir "/Users/zhangrui/Desktop/test 123/converted" & for %i in 
			# ("/Users/zhangrui/Desktop/test 123/*.*") do "/Users/zhangrui/Desktop/Part3-Mac/Part3-Src/res-mac/ffmpeg" 
			# -hide_banner -i "%i" -vcodec copy -acodec copy "/Users/zhangrui/Desktop/test 123/converted/%~ni.MP4"
			inputFiles='"'+os.path.join(inputPathStr,'*.*')+'"'	
			outFileName=os.path.join(outDir,'%~ni.'+outputExt)
			cmd= cmd % ('for %i in ('+inputFiles+') do ','%i',outFileName)
			cmd='cmd /c mkdir "%s" & ' % outDir+cmd

		# folder support on Mac
		else:
			# mkdir "/Users/zhangrui/Desktop/test 123/converted-1"; 
			# input_dir="/Users/zhangrui/Desktop/test 123"; 
			# output_dir="/Users/zhangrui/Desktop/test 123/converted-1"; 
			# output_ext="MP4"; 
			# for file in "$input_dir"/*; 
			# do 
			# 	# echo $file;
			# 	basename=`(basename "$file")`;
			# 	file_no_ext="${basename%.*}"; 
			# 	if ! [ -f "$file" ];
			#  	then 
			#  		continue;
			#  	fi; 
			# 	echo $file_no_ext;
			# 	echo $output_dir/$file_no_ext.$output_ext;
			# done

			cmd_prepare = 'input_dir="%s"; output_dir="%s"; output_ext="%s"; ' % (inputPathStr, outDir, outputExt)
			cmd_prepare += 'for file in "$input_dir"/*; do basename=`(basename "$file")`; file_no_ext="${basename%.*}"; '
			# cmd_prepare += 'if ! [ -f "$file" ] \n then \n continue \n fi; '
			cmd_prepare += 'if ! [ -f "$file" ]; then continue; fi; '
	
			cmd = cmd % (cmd_prepare, '$file', '$output_dir/$file_no_ext.$output_ext')
			cmd += '; done'
			cmd = 'mkdir "%s"; ' % outDir + cmd



	frame.cmdText.SetValue(cmd)
	# print('updated cmd: '+ cmd)

def threadProc():

	startTime=datetime.datetime.now()
	
	# frame.btn.SetLabel(u'Stop!')

	# wait for ffmpeg to finish
	global convertProc

	convertProc.wait()
	endTime=datetime.datetime.now()

	ret=convertProc.poll()
	try:
		if ret==0:
			print(u'转换成功！')
			# wx.MessageBox(u'转换成功！用时%s' % str(endTime-startTime),caption='Part3',style=wx.OK)
			wx.CallAfter(wx.MessageBox, u'转换成功！用时%s' % str(endTime-startTime), caption='Part3', style = wx.OK)
			
		else:
			print(u'错误代码:'+str(ret))
			# wx.MessageBox(u'错误代码:'+str(ret),u'转换失败',style=wx.OK)
			wx.CallAfter(wx.MessageBox, u'错误代码:'+str(ret), u'转换失败', style = wx.OK)
	except Exception as e:
		pass


	# frame.progressBar.Hide()
	# frame.remainTime.Hide()
	wx.CallAfter(frame.progressBar.SetValue, 0)
	wx.CallAfter(frame.remainTime.SetLabel, u"剩余时间:")
	
	frame.btn.SetLabel(u'Go!')
	updateCmd(None)

def re2seconds(re_time_matched):

	hour = int(re_time_matched.group(1))
	minute = int(re_time_matched.group(2))
	second = int(re_time_matched.group(3))
	milisecond = int(re_time_matched.group(4))
	seconds = 3600 * hour + minute * 60 + second + float(milisecond) / 100
	return seconds

def seconds2time(seconds):
	hour = minute = second = 0
	seconds = int(seconds)

	if seconds > 3600:
		hour = seconds / 3600
	seconds -= 3600 * hour

	if seconds > 60:
		minute = seconds / 60
	seconds -= 60 * minute

	second = seconds

	time_str = '%02d:%02d:%02d' % (hour, minute, second)
	return time_str
	# return (hour, minute, second)


def progressProc():

	# Sample output from ffmpeg
	#  Duration: 01:50:33.21, start: 0.000000, bitrate: 2233 kb/s
	# ..... omitted ...... 
	# Press [q] to stop, [?] for help
	# frame=   89 fps=0.0 q=23.0 size=     358kB time=00:00:04.31 bitrate= 678.5kbits/s dup=2 drop=0 speed=8.56x
	# frame=  178 fps=176 q=23.0 size=     766kB time=00:00:07.84 bitrate= 800.3kbits/s dup=4 drop=0 speed=7.74x

	global convertProc
	seconds = 0
	second_progress = 0
	speed = 1

	for line in command_output(convertProc):
		line = line.strip()
		if line.startswith('Duration: '):
			duration = re.match(r'.*Duration: (\d+):(\d+):(\d+)\.(\d+)', line)
			if duration:
				seconds = re2seconds(duration)

		if line.strip().startswith('frame'):
			progress = re.match(r'.*time=(\d+):(\d+):(\d+)\.(\d+)', line)
			if progress:
				second_progress = re2seconds(progress)		

			speed = re.match(r'.*speed=(.*)x', line)
			if speed:
				speed = float(speed.group(1))

			# print(second_progress, speed)
			if not seconds:
				print('fail to get input duration. Unable to calculate progress percentage.')
			else:
				rate = second_progress / seconds * 100
				rate_str = '%.2f%%' % rate
				seconds_remain = (seconds - second_progress) / speed 
				time_remain = seconds2time(seconds_remain)
				print(rate_str + '\t' + time_remain)
				# should not update UI from background
				# frame.progressBar.SetValue(int(rate))
				# frame.remainTime.SetLabel(rate_str + '   ' + u'剩余时间： ' + time_remain)
				wx.CallAfter(frame.remainTime.SetLabel, rate_str + '   ' + u'剩余时间： ' + time_remain)
				wx.CallAfter(frame.progressBar.SetValue, int(rate))


def command_output(convertProc):

	line = ''
	while convertProc.poll() == None:

		char = convertProc.stdout.read(1)
		if char == '\n':
			yield line
			line = ''
			continue
		else:
			line += char

def RunCmd(event): 

	global convertProc
	status=frame.btn.GetLabel()

	if status == u'Go!':

		cmd=frame.cmdText.GetValue()
		# MacOS will replace " to “ with smart quote
		# I did not find a easy way to disable it, so just replace it here
		cmd = cmd.replace(u'“', u'"')
		cmd = cmd.replace(u'”', u'"')

		cmd = platformEncode(cmd)

		sys_str = platform.system()
		shell = True
		if sys_str == 'Windows':
			shell = False

		convertProc = subprocess.Popen(cmd, shell = shell, stderr = subprocess.STDOUT, stdout = subprocess.PIPE, universal_newlines = True)

		waitThread=threading.Thread(target=threadProc)
		waitThread.start()
		frame.btn.SetLabel(u'Stop!')

		progressThread=threading.Thread(target=progressProc)
		progressThread.start()

		wx.CallAfter(frame.progressBar.SetValue, 0)
		wx.CallAfter(frame.remainTime.SetLabel, u"剩余时间:")

		# frame.progressBar.Show()
		# frame.remainTime.Show()

	else:
		frame.btn.SetLabel(u'Go!')
		wx.CallAfter(frame.progressBar.SetValue, 0)
		wx.CallAfter(frame.remainTime.SetLabel, u"剩余时间:")

		updateCmd(None)

		# kill the converter thread
		convertProc.kill()
	

def checkFormatCompat(event):

	if not event: return

	videoEncoder=frame.videoEncoder.GetValue()
	videoInfo=frame.videoInfo.GetLabel()
	videoEnabled=(frame.videoEnabled.GetValue() == wx.CHK_CHECKED)

	audioEncoder=frame.audioEncoder.GetValue()
	audioInfo=frame.audioInfo.GetLabel()
	container=frame.container.GetValue()
	audioEnabled=(frame.audioEnabled.GetValue() == wx.CHK_CHECKED)

	# allows user to force a container format
	if event.GetEventObject().GetName()!='container':
		# pcm only works with mov or wav
		if audioEncoder.startswith('pcm') or (audioEncoder=='copy' and audioInfo.startswith('pcm')):
			if videoEnabled and container != 'MOV':
				frame.container.SetValue('MOV')
			elif not videoEnabled and container != 'WAV':
				frame.container.SetValue('WAV')

		# flac only works with mov or flac
		if audioEncoder=='flac' or (audioEncoder=='copy' and audioInfo=='flac'):
			if videoEnabled and container != 'MOV':
				frame.container.SetValue('MOV')
			elif not videoEnabled and container != 'FLAC':
				frame.container.SetValue('FLAC')

		# prores only works with mov
		if videoEncoder.startswith('prores') and container != 'MOV':
			frame.container.SetValue('MOV')
			
		if videoEncoder=='copy' and audioInfo.startswith('prores') and container != 'MOV':
			frame.container.SetValue('MOV')


	# disable h264/265 only options for other formats
	h264_Widgets=[frame.staticVideoCRF,frame.staticVideoPreset,frame.staticVideoMaxRate,\
				frame.staticVideoRateUnit,frame.videoCRF,frame.videoPreset,frame.videoMaxRate]
	if videoEncoder not in ['h264','libx265']:
		for widget in h264_Widgets:
			widget.Disable()
	else:
		for widget in h264_Widgets:
			widget.Enable()

	# hide prores options when selected other codecs
	prores_Widgets=[frame.staticProresQuality,frame.proresQuality]
	if not videoEncoder == 'prores':
		for widget in prores_Widgets:
			widget.Hide()
	else:
		for widget in prores_Widgets:
			widget.Show()

	# disable video size related controls when copying video stream
	size_Widgets=[frame.staticWidth,frame.staticHeight,frame.videoWidth,frame.videoHeight,frame.constarinRatio]
	if videoEncoder==u'copy':
		for widget in size_Widgets:
			widget.Disable()
	else:
		for widget in size_Widgets:
			widget.Enable()

	# disable audio bitrate settings when copy/pcm/flac format is selected
	noAudioBitrateFormat=[u'copy',u'pcm_s16le','flac']
	audioBit_Widgets=[frame.staticAudioBitrate,frame.audioBitrate,frame.staticAudioRateUnit]
	if audioEncoder in noAudioBitrateFormat:
		for w in audioBit_Widgets:
			w.Hide()
	else:
		for w in audioBit_Widgets:
			w.Show()


def replaceAudio(event):
	if frame.audioReplace.GetValue() == wx.CHK_CHECKED:
		if frame.audioInfo.GetLabel() != "":
			frame.audioExtra.SetValue(u'视频自带音频，无法合并音频。请选择一个没有音频的视频，或者用本工具生成一个。')
			frame.audioEnabled.SetValue(wx.CHK_CHECKED)
			frame.staticAudioExtra.SetLabel(u'合并音频：')
	else:
		frame.staticAudioExtra.SetLabel(u'额外参数：')
		# changeValueProgramatically=True
		frame.audioExtra.SetValue('')
		# changeValueProgramatically=False

	updateCmd(event)



class MyFileDropTarget(wx.FileDropTarget):
	def __init__(self, window):
		wx.FileDropTarget.__init__(self)
		self.window = window
	def OnDropFiles(self, x, y, filenames):
		self.window.fileText.SetValue(filenames[0])
		return False

		# for file in filenames:
		# 	self.window.AppendText("\t%s\n" % file)

def loadResources():

	resources = [['ffmpeg', 'binary'],
				 ['ffprobe', 'binary'],
				 ['lollipop', 'icon']]
	for res in resources:
		res_path_str = locateResource(res[0], res[1])
		if not os.path.exists(res_path_str):
			print(ur'找不到%s' % res)
			res_path[res[0]] = res[0]
		else:
			res_path[res[0]] = res_path_str

def locateResource(resourceName, resType = 'binary'):

	sys_str = platform.system()

	bundle_dir = '.'
	if getattr(sys, 'frozen', False) :
		# running from a bundle
		bundle_dir = sys._MEIPASS
		if sys_str == 'Windows':
			import win32api
			bundle_dir = win32api.GetLongPathName(bundle_dir)
	else :
		# running python Part3.py directly
		bundle_dir = os.path.dirname(os.path.abspath(__file__))
		if sys_str == 'Windows':
			bundle_dir = os.path.join(bundle_dir, 'res-win')
		elif sys_str == 'Darwin':
			bundle_dir = os.path.join(bundle_dir, 'res-mac')
		else:
			bundle_dir = os.path.join(bundle_dir, 'res-linux')

	if sys_str == 'Windows':
		if resType == 'binary' and not resourceName.endswith('.exe'):
			resourceName += '.exe'
		if resType == 'icon' and not resourceName.endswith('.ico'):
			resourceName += '.ico'

	if sys_str.startswith('Darwin') or sys_str.startswith('Linux'):
		if resType == 'icon' and not resourceName.endswith('.icns'):
			resourceName += '.ico'

	resPath = os.path.join(bundle_dir, resourceName)
	return resPath



if __name__ == '__main__':

	loadResources()

	app = wx.App()
	frame = MyFrame()
	frame.Show(True)

	# otherwise, it will not show up on Mac
	frame.videoCRF.SetToolTip(u'建议取值18-28之间，数字越大，质量越差')
	frame.videoExtra.SetToolTip(u'-r rate 帧率\n-vframes number 要转换的帧数量\n-movflags +faststart 首帧播放')

	frame.videoEnabled.SetValue(wx.CHK_CHECKED)
	frame.audioEnabled.SetValue(wx.CHK_CHECKED)
	frame.constarinRatio.SetValue(wx.CHK_CHECKED)
	frame.videoEncoder.SetSelection(0)
	frame.proresQuality.SetSelection(0)
	frame.videoWidth.SetSelection(0)
	frame.videoHeight.SetSelection(0)
	frame.videoPreset.SetSelection(1)
	frame.audioEncoder.SetSelection(0)
	frame.container.SetSelection(0)

	frame.btn.Bind(wx.EVT_BUTTON,RunCmd)
	frame.fileText.Bind(wx.EVT_TEXT,updateCmd)
	
	frame.videoEnabled.Bind(wx.EVT_CHECKBOX,updateCmd)
	frame.audioEnabled.Bind(wx.EVT_CHECKBOX,updateCmd)
	frame.audioReplace.Bind(wx.EVT_CHECKBOX,replaceAudio)
	frame.overWrite.Bind(wx.EVT_CHECKBOX,updateCmd)
	frame.constarinRatio.Bind(wx.EVT_CHECKBOX,updateVideoSize)
	frame.firstFramePlay.Bind(wx.EVT_CHECKBOX,updateCmd)

	frame.videoEncoder.Bind(wx.EVT_TEXT,updateCmd)
	frame.videoEncoder.Bind(wx.EVT_COMBOBOX,updateCmd)
	frame.proresQuality.Bind(wx.EVT_TEXT,updateCmd)
	frame.proresQuality.Bind(wx.EVT_COMBOBOX,updateCmd)
	frame.videoWidth.Bind(wx.EVT_TEXT,updateVideoSize)
	frame.videoWidth.Bind(wx.EVT_COMBOBOX,updateVideoSize)
	# frame.videoWidth.Bind(wx.EVT_KILL_FOCUS,checkDivideBy2)
	frame.videoHeight.Bind(wx.EVT_TEXT,updateVideoSize)
	frame.videoHeight.Bind(wx.EVT_COMBOBOX,updateVideoSize)
	# frame.videoHeight.Bind(wx.EVT_KILL_FOCUS,checkDivideBy2)
	frame.videoPreset.Bind(wx.EVT_TEXT,updateCmd)
	frame.videoPreset.Bind(wx.EVT_COMBOBOX,updateCmd)
	frame.videoCRF.Bind(wx.EVT_SPINCTRL,updateCmd)
	frame.videoMaxRate.Bind(wx.EVT_TEXT,updateCmd)
	frame.videoMaxRate.Bind(wx.EVT_COMBOBOX,updateCmd)
	frame.audioBitrate.Bind(wx.EVT_TEXT,updateCmd)	
	frame.audioBitrate.Bind(wx.EVT_COMBOBOX,updateCmd)	
	frame.audioEncoder.Bind(wx.EVT_TEXT,updateCmd)
	frame.audioEncoder.Bind(wx.EVT_COMBOBOX,updateCmd)
	frame.container.Bind(wx.EVT_TEXT,updateCmd)
	frame.container.Bind(wx.EVT_COMBOBOX,updateCmd)

	frame.videoExtra.Bind(wx.EVT_TEXT,updateCmd)
	frame.videoExtra.Bind(wx.EVT_COMBOBOX,updateCmd)
	frame.audioExtra.Bind(wx.EVT_TEXT,updateCmd)
	frame.audioExtra.Bind(wx.EVT_COMBOBOX,updateCmd)

	# frame.progressBar.Hide()
	# frame.remainTime.Hide()
	
	dt = MyFileDropTarget(frame)
	frame.SetDropTarget(dt)

	app.MainLoop()
