import { Job, Worker } from "bullmq"
import { redis } from "../configs/redis.js"
import { model } from '../configs/ai-model.js'
import { tryCatch } from "src/utils/tryCatch.js"

const embedingFunc = async (job: Job) => {
    if (job.data?.content.length === 0) {
        console.log("No text content found")
        return null
    }

    const content = job.data.content.map((details: any) => details.pageContent)

    const {data,error}= await tryCatch(model.embedDocuments(content))
    if (error) {
        console.log(error)
    }

    return null
}


export const EmbedingWorker = new Worker('embeding', embedingFunc, { connection: redis })

EmbedingWorker.on("ready", () => {
    console.log("Started the worker embeding")
})

EmbedingWorker.on("error", (error) => {
    console.log("Error detected in embeding" + error.message)
})