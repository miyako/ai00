Class extends _CLI

Class constructor($controller : 4D:C1709.Class)
	
	If (Not:C34(OB Instance of:C1731($controller; cs:C1710._Ai00_Controller)))
		$controller:=cs:C1710._Ai00_Controller
	End if 
	
	var $command : Text
	
	Case of 
		: (Is macOS:C1572) && (Get system info:C1571.processor#"@Apple@")
			$command:="ai00-server-x86_64"
		Else 
			$command:="ai00-server"
	End case 
	
	Super:C1705($command; $controller)
	
Function get worker() : 4D:C1709.SystemWorker
	
	return This:C1470.controller.worker
	
Function terminate()
	
	This:C1470.controller.terminate()