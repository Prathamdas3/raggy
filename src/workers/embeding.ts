import { Job, Worker } from "bullmq"
import { redis } from "../configs/redis.js"
import { model } from '../configs/ai-model.js'
import { tryCatch } from "src/utils/tryCatch.js"
import { getVectorStore } from "src/configs/qdrant.js"
import type { EmbeddingsInterface } from "@langchain/core/embeddings";
import { QdrantVectorStore } from "@langchain/qdrant";


const embedingFunc = async (job: Job) => {
    if (job.data?.content.length === 0) {
        console.log("No text content found")
        return null
    }

    const oldContent = job.data.content
    const content = job.data.content.map((details: any) => details.pageContent)

    const { data, error } = await tryCatch(model.embedDocuments(content))
    if (error) {
        console.log(error)
        throw new Error("Failed to get the embedings")
    }
    const vectorStore = await QdrantVectorStore.fromExistingCollection(data, {
        // url: env.QDRANT_URL!,
        url: "http://localhost:6333",
        collectionName: "rag",
    });
    console.log("Qdrant VectorStore initialized ✅");



    // const store = await getVectorStore()
    // console.log(store)
    // const { data: storeRes, error: storeError } = await tryCatch(store.addVectors(data, oldContent))
    // if (storeError) {
    //     console.log(storeError)
    // }
    // console.log(storeRes)

    return null
}


export const EmbedingWorker = new Worker('embeding', embedingFunc, { connection: redis })

EmbedingWorker.on("ready", () => {
    console.log("Started the worker embeding")
})

EmbedingWorker.on("error", (error) => {
    console.log("Error detected in embeding" + error.message)
})