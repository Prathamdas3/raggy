#### Endpoints

```js
// server input
PORT: 8200
-> for checking input server: {
    type: "GET",
    route: "/api" 
    code:200
}

-> for handling files: {
type:"POST", 
route:"/api/v1/file",
request-body:{
    chat_id:string,
    user_id:string,
    file:File
    } 
}

-> for handling yt link: {
type:"POST",
route:"/api/v1/yt",
request-body:{
    chat_id:string,
    user_id:string,
    link:string
}}
```

```js
PORT:8400
-> for checking the db server:{
    type: "GET",
    route:"/api"
}

-> for initiation for the summary:{
    type: "POST",
    route:"/api/v1/summary",
    request-body:{
        chat_id:string,
        user_id:string,
        original_text:string
    },
    response-body:{
        status:"accepted",
        message:string,
        data:{
            task_id:string
        }
    },
    code:200
}

-> for saving data in vector store:{
    type: "POST",
    route: "/api/v1/save",
    request-body:{
       
    }
}
```



```js
// db interface
PORT: 8800
-> for checking the db server: {
    type:"GET",
    route:"/api"
}

-> for getting original docs text: {
    type:"GET",
    route:"/api/v1/docs/:chatId/original-text",
    response-body:{
    status: "Success";
    message: string;
    data: {
        original_text: Array<{
        content: string;
        metadata: {
            chat_id: string;
            user_id: string;
            chunk_index: number;
        };
        }>;
        doc_id: string;
        chat_id: string;
        };
    },
    code:200
}

-> for getting summary text:{
    type:"GET",
    route:"/api/v1/docs/:chatId/summary-text",
    response-body:{
        status: "Success";
        message: string;
        data: {
            summary_text: string;
            doc_id: string;
            chat_id: string;
        };
    };
    code:200
}

-> for getting audio url:{
    type:"GET",
    route:"/api/v1/docs/:chatId/audio-url",
    response-body:{
        status: "Success",
        message: string;
        data: {
            id: string;
            chat_id: string;
            audio_url: string;
        };
    };
    code:200
}

-> for uploading original docs text: {
    type:"POST",
    route:"/api/v1/docs",
    request-body:{
        chat_id:string,
        user_id:string,
        original_text:{
            content:string,
            metadata:{
                user_id:string,
                chat_id:string,
                chunk_index:number
            }
        }[]
    },
    code:201
}

-> for updating summary text: {
    type:"PATCH",
    route:"/api/v1/docs",
    request-body:{
        chat_id:string,
        summary_text:string
    },
    response-body:{
        status:"Success",
        message:string,
        data:string
    },
    code:200
}

-> for updating the audio url: {
    type:"PATCH",
    route:"/api/v1/docs",
    request-body:{
        chat_id:string,
        audio_url:url
    },
    response-body:{
        status:"Success",
        message:string,
        data:string
    },
    code:200
}
```