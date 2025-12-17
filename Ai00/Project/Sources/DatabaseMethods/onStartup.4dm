var $Ai00 : cs:C1710.Ai00

If (False:C215)
	$Ai00:=cs:C1710.Ai00.new()  //default
Else 
	var $homeFolder : 4D:C1709.Folder
	$homeFolder:=Folder:C1567(fk home folder:K87:24).folder(".Ai00")
	var $file : 4D:C1709.File
	$file:=$homeFolder.file("rwkv7-g1a-0.4b-20250905-ctx4096.st")
	$URL:="https://github.com/miyako/ai00/releases/download/models/rwkv7-g1a-0.4b-20250905-ctx4096.st"
	var $port : Integer
	$port:=8080
	
	var $event : cs:C1710.event.event
	$event:=cs:C1710.event.event.new()
/*
Function onError($params : Object; $error : cs.event.error)
Function onSuccess($params : Object; $models : cs.event.models)
*/
	$event.onError:=Formula:C1597(ALERT:C41($2.message))
	$event.onSuccess:=Formula:C1597(ALERT:C41($2.models.extract("name").join(",")+" loaded!"))
	$event.onData:=Formula:C1597(MESSAGE:C88(String:C10((This:C1470.range.end/This:C1470.range.length)*100; "###.00%")))  //onData@4D.HTTPRequest
	$event.onResponse:=Formula:C1597(ERASE WINDOW:C160)  //onResponse@4D.HTTPRequest
	
	$Ai00:=cs:C1710.Ai00.new($port; $file; $URL; {\
		max_batch: 1; \
		quant_type: "Int8"; \
		precision: "Fp32"}; $event)
End if 