property embed_device : Text
property max_batch : Integer
property name : Text
property path : Text
property ip : Text
property port : Integer
property quant_type : Text
property precision : Text

property _configFile : 4D:C1709.File
property _configTemplate : Text

Class constructor
	
	This:C1470.embed_device:="cpu"
	This:C1470.max_batch:=8
	This:C1470.name:="RWKV-x070-World-0.4B-v2.9-20250107-ctx4096"
	var $modelsFolder : 4D:C1709.Folder
	$modelsFolder:=Folder:C1567(fk home folder:K87:24).folder(".Ai00")
	This:C1470.path:=$modelsFolder.file(This:C1470.name).path
	This:C1470.ip:="0.0.0.0"
	This:C1470.port:=8080
	This:C1470.quant_type:="Int8"
	This:C1470.precision:="Fp16"
	
	This:C1470._configFile:=File:C1566("/RESOURCES/Config.toml")
	This:C1470._configTemplate:=This:C1470._configFile.getText()
	
Function getText() : Text
	
	var $template : Text
	$template:=This:C1470._configTemplate
	PROCESS 4D TAGS:C816($template; $toml; This:C1470)
	
	return $toml