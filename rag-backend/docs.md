#### Endpoints

```js
// server input
PORT: 8000
-> for checking input server: {
    type: "GET",
    route: "/api" 
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
// db interface
PORT: 9000
-> for checking the db server: {
    type:"GET",
    route:"/api"
}

-> for getting original docs text: {
    type:"GET",
    route:"/api/v1/docs/:chatId/original-text",
    response:{
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
}
}

-> for getting summary text:{
    type:"GET",
    route:"/api/v1/docs/:chatId/summary-text",
    response:{
        status: "Success";
        message: string;
        data: {
            summary_text: string;
            doc_id: string;
            chat_id: string;
        };
};
}

-> for getting audio url:{
    type:"GET",
    route:"/api/v1/docs/:chatId/audio-url",
    response:{
        status: "Success",
        message: string;
        data: {
            id: string;
            chat_id: string;
            audio_url: string;
        };
};
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
    }
}

-> for updating summary text: {
    type:"PATCH",
    route:"/api/v1/docs",
    request-body:{
        chat_id:string,
        summary_text:string
    },
    response:{
        status:"Success",
        message:string,
        data:string
    }
}

-> for updating the audio url: {
    type:"PATCH",
    route:"/api/v1/docs",
    request-body:{
        chat_id:string,
        audio_url:url
    },
    response:{
        status:"Success",
        message:string,
        data:string
    }
}
```