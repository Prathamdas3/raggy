import { Job, Worker } from "bullmq"
import { redis } from "../libs/redis.js"
import { PDFLoader } from "@langchain/community/document_loaders/fs/pdf";
import { RecursiveCharacterTextSplitter } from '@langchain/textsplitters'
import { tryCatch } from "src/libs/tryCatch.js";
import fs from 'fs'

const splitter = new RecursiveCharacterTextSplitter({
    chunkSize: 1000,
    chunkOverlap: 200,
});


const SplitingFunc = async (job: Job) => {
    if (!job.data?.filepath.trim()) {
        console.log("No filepath present")
        return null
    }

    const filePath = job.data?.filepath

    //loading the pdf content
    const loader = new PDFLoader(filePath)
    const { data: docs, error: docsError } = await tryCatch(loader.load())

    if (docsError) {
        console.log("Failed to load the pdf content")
        throw new Error("Failed to load the pdf content")
    }

    //spliting the pdf content to text for embadding
    const { data: texts, error: textsError } = await tryCatch(splitter.splitDocuments(docs))

    if (textsError) {
        console.log("Failed to split the texts content")
        throw new Error("Failed to split the texts content")
    }


    if (filePath && texts.length > 0) {
        try {

            await fs.promises.unlink(filePath)
        } catch (unlinkErr) {
            console.error('Failed to clean up file:', unlinkErr)
        }
    }

    return null
}

export const TextSplitingWorker = new Worker('text-spliter', SplitingFunc, { connection: redis })

TextSplitingWorker.on("ready", () => {
    console.log("Started the worker text-spliter")
})

TextSplitingWorker.on("error", (error) => {
    console.log("Error detected in text-spliter" + error.message)
})