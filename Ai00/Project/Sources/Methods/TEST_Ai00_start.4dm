//%attributes = {"invisible":true}
var $Ai00 : cs:C1710.Ai00

If (True:C214)
	$Ai00:=cs:C1710.Ai00.new()  //default
Else 
	var $modelsFolder : 4D:C1709.Folder
	$modelsFolder:=Folder:C1567(fk home folder:K87:24).folder(".Ai00")
	var $file : 4D:C1709.File
	$file:=$modelsFolder.file("RWKV-x070-World-0.4B-v2.9-20250107-ctx4096.st")
	$URL:="https://modelscope.cn/models/shoumenchougou/RWKV-7-World-ST/resolve/master/RWKV-x070-World-0.4B-v2.9-20250107-ctx4096.st"
	var $port : Integer
	$port:=8080
	$Ai00:=cs:C1710.Ai00.new($port; $file; $URL; {\
		quant_type: "Int8"; \
		precision: "Fp16"}; Formula:C1597(ALERT:C41(This:C1470.file.name+($1.success ? " started!" : " did not start..."))))
End if 