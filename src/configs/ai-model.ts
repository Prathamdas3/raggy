import { HuggingFaceTransformersEmbeddings } from "@langchain/community/embeddings/huggingface_transformers";
import { ChatMistralAI } from "@langchain/mistralai";
// import { HuggingFaceInference } from "@langchain/community/llms/hf";
// import { MistralAIEmbeddings } from "@langchain/mistralai";



//if you are going to change the embeding model then also change the name of the collection otherwise it will corrupt the data in the db
// export const embeddingsModel = new MistralAIEmbeddings({
//   model: "mistral-embed",
//   apiKey:""
// });


export const model = new HuggingFaceTransformersEmbeddings({
  model: "Xenova/all-MiniLM-L6-v2",
});

export const summaryModel = new ChatMistralAI({
  model: "mistral-large-latest",
  temperature: 0.4,
  apiKey: ""
});


// new HuggingFaceInference({
//   model: "facebook/bart-large-cnn",
//   apiKey: huggingface_api_key from the env,
//   maxRetries: 3,
// })


