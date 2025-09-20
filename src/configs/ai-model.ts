import { HuggingFaceTransformersEmbeddings } from "@langchain/community/embeddings/huggingface_transformers";
import { ChatMistralAI } from "@langchain/mistralai";
import { env } from "./env.js";
import { pipeline } from '@huggingface/transformers'
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

export const mistralModel = new ChatMistralAI({
  model: "mistral-large-latest",
  temperature: 0.4,
  apiKey: env.MISTRALAI_API_KEY!,
  maxTokens: 100
});

// export const audioModel = pipeline(
//   "text-to-speech",
//   "onnx-community/Kokoro-82M-v1.0-ONNX",
//   {
//     device: "auto"
//   },
// )



