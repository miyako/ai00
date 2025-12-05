property embed_device : Text
property max_batch : Integer
property name : Text
property path : Text
property ip : Text
property port : Integer
property quant_type : Text
property precision : Text
property web_path : Text
property adapter : Integer

property _configFile : 4D:C1709.File
property _configTemplate : Text
property _modelFile : 4D:C1709.File

Class constructor
	
	This:C1470.embed_device:="Cpu"
	This:C1470.max_batch:=8
	This:C1470.ip:="0.0.0.0"
	This:C1470.port:=8080
	This:C1470.quant_type:="Int8"
	This:C1470.precision:="Fp16"
	
	This:C1470._configFile:=File:C1566("/RESOURCES/Config.toml")
	This:C1470._configTemplate:=This:C1470._configFile.getText()
	
Function setModel($model : 4D:C1709.File)
	
	This:C1470._modelFile:=$model
	
Function get name() : Text
	
	If (Value type:C1509(This:C1470._modelFile)=Is object:K8:27) && (OB Instance of:C1731(This:C1470._modelFile; 4D:C1709.File)) && (This:C1470._modelFile.exists)
		return This:C1470._modelFile.fullName
	End if 
	
Function get path() : Text
	
	If (Value type:C1509(This:C1470._modelFile)=Is object:K8:27) && (OB Instance of:C1731(This:C1470._modelFile; 4D:C1709.File)) && (This:C1470._modelFile.exists)
		return File:C1566(This:C1470._modelFile.platformPath; fk platform path:K87:2).parent.path
	End if 
	
Function get web_path() : Text
	
	return "assets/www/index.zip"
	
Function get force_pass() : Text
	
	return "false"
	
Function get slot() : Text
	
	return ""  //the Bearer token if force_pass=true
	
Function get manual() : Integer
	
	return 0
	
Function get quant() : Integer
	
	return 0
	
Function getText() : Text
	
	var $template : Text
	$template:=This:C1470._configTemplate
	PROCESS 4D TAGS:C816($template; $toml; This:C1470)
	
	return $toml