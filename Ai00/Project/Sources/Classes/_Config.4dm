property embed_device : Text
property max_batch : Integer
property name : Text
property path : Text
property ip : Text
property port : Integer
property quant_type : Text
property precision : Text
property web_path : Text

property _configFile : 4D:C1709.File
property _configTemplate : Text

Class constructor
	
	This:C1470.embed_device:="Cpu"
	This:C1470.max_batch:=1
	var $modelsFolder : 4D:C1709.Folder
	$modelsFolder:=Folder:C1567(fk home folder:K87:24).folder(".Ai00")
	This:C1470.name:="RWKV-x070-World-0.1B-v2.8-20241210-ctx4096.st"
	This:C1470.path:=$modelsFolder.file(This:C1470.name).path
	This:C1470.ip:="0.0.0.0"
	This:C1470.port:=8080
	This:C1470.quant_type:="Int8"
	This:C1470.precision:="Fp16"
	
	This:C1470._configFile:=File:C1566("/RESOURCES/Config.toml")
	This:C1470._configTemplate:=This:C1470._configFile.getText()
	
Function get web_path() : Text
	
	return "assets/www/index.zip"
	
Function get quant() : Integer
	
	Case of 
		: (This:C1470.quant_type="NF4")
			return 2
		: (This:C1470.quant_type="Int8")
			return 1
		Else 
			return 0
	End case 
	
Function getText() : Text
	
	var $template : Text
	$template:=This:C1470._configTemplate
	PROCESS 4D TAGS:C816($template; $toml; This:C1470)
	
	return $toml