Class constructor($port : Integer; $file : 4D:C1709.File; $URL : Text; $options : Object; $event : cs:C1710._event)
	
	var $Ai00 : cs:C1710.workers.worker
	$Ai00:=cs:C1710.workers.worker.new(cs:C1710._server)
	
	If (Not:C34($Ai00.isRunning($port)))
		
		If (Value type:C1509($file)#Is object:K8:27) || (Not:C34(OB Instance of:C1731($file; 4D:C1709.File))) || ($URL="")
			$modelsFolder:=Folder:C1567(fk home folder:K87:24).folder(".Ai00")
			$file:=$modelsFolder.file("RWKV-x070-World-0.4B-v2.9-20250107-ctx4096.st")
			$URL:="https://modelscope.cn/models/shoumenchougou/RWKV-7-World-ST/resolve/master/RWKV-x070-World-0.4B-v2.9-20250107-ctx4096.st"
			//$file:=$modelsFolder.file("rwkv7-g1a-0.4b-20250905-ctx4096.st")
			//$URL:="https://github.com/miyako/ai00/releases/download/models/rwkv7-g1a-0.4b-20250905-ctx4096.st"
		End if 
		
		If ($port=0) || ($port<0) || ($port>65535)
			$port:=8080
		End if 
		
		This:C1470.main($port; $file; $URL; $options; $event)
		
	End if 
	
Function onTCP($status : Object; $options : Object)
	
	If ($status.success)
		
		var $className : Text
		$className:=Split string:C1554(Current method name:C684; "."; sk trim spaces:K86:2).first()
		
		CALL WORKER:C1389($className; Formula:C1597(start); $options; Formula:C1597(onModel))
		
	Else 
		
		var $statuses : Text
		$statuses:="TCP port "+String:C10($status.port)+" is aready used by process "+$status.PID.join(",")
		var $error : cs:C1710._error
		$error:=cs:C1710._error.new(1; $statuses)
		
		If ($options.event#Null:C1517) && (OB Instance of:C1731($options.event; cs:C1710._event))
			$options.event.onError.call(This:C1470; $options; $error)
		End if 
		
		This:C1470.terminate()
		
	End if 
	
Function main($port : Integer; $file : 4D:C1709.File; $URL : Text; $options : Object; $event : cs:C1710._event)
	
	main({port: $port; file: $file; URL: $URL; options: $options; event: $event}; This:C1470.onTCP)
	
Function terminate()
	
	var $Ai00 : cs:C1710.workers.worker
	$Ai00:=cs:C1710.workers.worker.new(cs:C1710._server)
	$Ai00.terminate()