      

    function initSocket()
    {
        ws = new WebSocket('ws://localhost:8881/websocket')     // ws is a global variable (my_page_ws.html)
        ws.onopen = onSocketOpen
        ws.onmessage = onSocketMessage
        ws.onclose = onSocketClose
    }
    
    function onBodyLoad() {
        initSocket();
        
        const interval = setInterval(function() {
            checkSocket(); 
        }, 5000);
    }
    
    function onSocketOpen() {
        console.log("WS client: Websocket opened.")
    }
            
    function onSocketMessage(message) {
        var data
        try {
            if (message != false)
            {    
                data = JSON.parse(message.data);          
                $.each(data, function(k, v){                                                     
                    console.log(k);
                    console.log('#'+k+'.actT');
                    console.log(v);
                                        
                    if(validNames.indexOf(k) == -1)
                    {
                        return;
                    }
                    
                    $('#'+k+' .actT').html(v['akt']);
                    $('#'+k+' .avgT').html(v['avg']);
                    $('#'+k+' .maxT').html(v['max']);
                    $('#'+k+' .minT').html(v['min']);                                  
                                            
                    console.log("Data updated");                          
                });
            }    
            else
            {
                console.log("No new data recieved");
            }
        } catch(e) {
            data = message.data
        }
        
    }
    
    function onSocketClose() {
        console.log("WS client: Websocket closed.") 
    }    
    
    function checkSocket()
    {
        if (ws.readyState === WebSocket.CLOSED)
        {
            initSocket();
        }
        
        if (ws.readyState === WebSocket.OPEN)
        {
            ws.send("JS_PROMPT");   
        }  
        else
        {
            setTimeout(function(){checkSocket()}, 1000);    
        }      
    }
    
    $('document').ready(function(){
        onBodyLoad();
    });
