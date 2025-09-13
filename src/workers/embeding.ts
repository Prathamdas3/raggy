import { Job, Worker } from "bullmq"
import { redis } from "../libs/redis.js"

const embedingFunc = async (job: Job) => {

}


export const EmbedingWorker = new Worker('text-spliter', embedingFunc, { connection: redis })

EmbedingWorker.on("ready", () => {
    console.log("Started the worker embeding")
})

EmbedingWorker.on("error", (error) => {
    console.log("Error detected in embeding" + error.message)
})