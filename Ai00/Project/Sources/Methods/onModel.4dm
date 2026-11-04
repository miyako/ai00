//%attributes = {}
#DECLARE($status : Object; $options : Object)

If ($status.success)
	
Else 
	
	var $message : Text
	$message:="failed to load model!"
	If (Value type:C1509($status.message)=Is text:K8:3) && ($status.message#"")
		$message:=$status.message
	End if 
	
	var $error : cs:C1710.event.error
	$error:=cs:C1710.event.error.new(2; $message; This:C1470.models())
	
	//_Model passes its options, which do not carry the event; fall back to the receiver's
	var $event : Object
	$event:=$options.event
	If ($event=Null:C1517) && (This:C1470#Null:C1517)
		$event:=This:C1470.event
	End if 
	
	If ($event#Null:C1517) && (OB Instance of:C1731($event; cs:C1710.event.event))
		$event.onError.call(This:C1470; $options; $error)
	End if 
	
	var $workers : cs:C1710.workers.workers
	$workers:=cs:C1710.workers.workers.new()
	$workers.remove($options.port)
	
End if 