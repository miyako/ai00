Class constructor($port : Integer; $file : 4D:C1709.File; $URL : Text; $options : Object; $formula : 4D:C1709.Function)
	
	var $Ai00 : cs:C1710._worker
	$Ai00:=cs:C1710._worker.new()
	
	If (Not:C34($Ai00.isRunning()))
		
		If (Value type:C1509($file)#Is object:K8:27) || (Not:C34(OB Instance of:C1731($file; 4D:C1709.File))) || ($URL="")
			$modelsFolder:=Folder:C1567(fk home folder:K87:24).folder(".Ai00")
			var $file : 4D:C1709.File
			$file:=$modelsFolder.file("RWKV-x070-World-0.4B-v2.9-20250107-ctx4096.st")
			$URL:="https://modelscope.cn/models/shoumenchougou/RWKV-7-World-ST/resolve/master/RWKV-x070-World-0.4B-v2.9-20250107-ctx4096.st"
			//$file:=$modelsFolder.file("rwkv7-g1a-0.4b-20250905-ctx4096.st")
			//$URL:="https://github.com/miyako/ai00/releases/download/models/rwkv7-g1a-0.4b-20250905-ctx4096.st"
		End if 
		
		If ($port=0) || ($port<0) || ($port>65535)
			$port:=8080
		End if 
		
		CALL WORKER:C1389("Ai00_Start"; This:C1470._Start; $port; $file; $URL; $options; $formula)
		
	End if 
	
Function _Start($port : Integer; $file : 4D:C1709.File; $URL : Text; $options : Object; $formula : 4D:C1709.Function)
	
	var $model : cs:C1710.Model
	$model:=cs:C1710.Model.new($port; $file; $URL; $options; $formula)
	
Function terminate()
	
	var $Ai00 : cs:C1710._worker
	$Ai00:=cs:C1710._worker.new()
	$Ai00.terminate()