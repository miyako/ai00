Class extends _Ai00

Class constructor($controller : 4D:C1709.Class)
	
	Super:C1705($controller)
	
Function start($option : Object) : 4D:C1709.SystemWorker
	
	var $command : Text
	$command:=This:C1470.escape(This:C1470.executablePath)
	
	var $config : cs:C1710._Config
	$config:=cs:C1710._Config.new()
	
	Case of 
		: (Value type:C1509($option.model)=Is object:K8:27) && (OB Instance of:C1731($option.model; 4D:C1709.File)) && ($option.model.exists)
			$config.setModel($option.model)
	End case 
	
	If (Value type:C1509($option.ip)=Is text:K8:3)
		$config.ip:=$option.ip
	End if 
	
	If (Value type:C1509($option.port)=Is real:K8:4)
		$config.port:=$option.port
	End if 
	
	If (Value type:C1509($option.precision)=Is text:K8:3)
		$config.precision:=$option.precision
	End if 
	
	If (Value type:C1509($option.quant_type)=Is text:K8:3)
		$config.quant_type:=$option.quant_type
	End if 
	
	If (Value type:C1509($option.embed_device)=Is text:K8:3)
		$config.embed_device:=$option.embed_device
	End if 
	
	If (Value type:C1509($option.max_batch)=Is real:K8:4)
		$config.max_batch:=$option.max_batch
	End if 
	
	//setup home directory
	var $currentDirectory : 4D:C1709.Folder
	$currentDirectory:=Folder:C1567(fk home folder:K87:24).folder(".Ai00")
	$currentDirectory.create()
	var $assetsFolder : 4D:C1709.Folder
	$assetsFolder:=$currentDirectory.folder("assets")
	$assetsFolder.create()
	var $wwwFolder : 4D:C1709.Folder
	$wwwFolder:=$assetsFolder.folder("www")
	$wwwFolder.create()
	var $indexZipFile : 4D:C1709.File
	$indexZipFile:=File:C1566("/RESOURCES/www/index.zip")
	If (Not:C34($wwwFolder.file($indexZipFile.fullName).exists))
		$indexZipFile.copyTo($wwwFolder)
	End if 
	
	var $configFile : 4D:C1709.File
	$configFile:=$assetsFolder.file("config.toml")
	$configFile.setText($config.getText())
	
	$command+=(" --config "+This:C1470.escape($configFile.path)+" ")
	
	var $arg : Object
	var $valueType : Integer
	var $key : Text
	
	For each ($arg; OB Entries:C1720($option))
		Case of 
			: (["config"; "ip"; "port"; \
				"max_batch"; "embed_device"; \
				"quant"; "quant_type"; "precision"; "path"; "name"].includes($arg.key))
				continue
		End case 
		$valueType:=Value type:C1509($arg.value)
		$key:=Replace string:C233($arg.key; "_"; "-"; *)
		Case of 
			: ($valueType=Is real:K8:4)
				$command+=(" --"+$key+" "+String:C10($arg.value)+" ")
			: ($valueType=Is text:K8:3)
				$command+=(" --"+$key+" "+This:C1470.escape($arg.value)+" ")
			: ($valueType=Is boolean:K8:9) && ($arg.value)
				$command+=(" --"+$key+" ")
			Else 
				//
		End case 
	End for each 
	
	This:C1470.controller.currentDirectory:=$currentDirectory
	
	SET TEXT TO PASTEBOARD:C523($command)
	
	return This:C1470.controller.execute($command; $isStream ? $option.model : Null:C1517; $option.data).worker
	