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
body:{
    chat_id:string,
    user_id:string,
    file:File
    } 
}

-> for handling yt link: {
type:"POST",
route:"/api/v1/yt",
body:{
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

-> for geting original docs text: {
        type:"GET",
        route:"/api/v1/docs/:chatId",
        }

-> for uploading original docs text: {
    type:"POST",
    route:"/api/v1/docs",
    body:{
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
    body:{
        chat_id:string,
        summary_text:string
    }
}

-> for updating the audio url: {
    type:"PATCH",
    route:"/api/v1/docs",
    body:{
        chat_id:string,
        audio_url:url
    }
}
```