import { HuggingFaceTransformersEmbeddings } from "@langchain/community/embeddings/huggingface_transformers";
import { ChatGroq } from "@langchain/groq";
import { env } from "./env.js";

export const embedingModel = new HuggingFaceTransformersEmbeddings({
  model: "Xenova/all-MiniLM-L6-v2",
});


export const model = new ChatGroq({
  temperature: 0.4,
  model: "llama-3.3-70b-versatile",
  apiKey: env.GROQ_API_KEY!
})


// import { ChatMistralAI, MistralAIEmbeddings } from "@langchain/mistralai";


// export const mistralModel = new ChatMistralAI({
  //   model: "mistral-large-latest",
//   temperature: 0.4,
//   apiKey: env.MISTRALAI_API_KEY!,
//   // maxTokens: 100
// });


//if you are going to change the embeding model then also change the name of the collection otherwise it will corrupt the data in the db
// export const embeddingsModel = new MistralAIEmbeddings({
//   model: "mistral-embed",
//   apiKey:""
// });
