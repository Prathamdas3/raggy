import { Job, Worker } from "bullmq"
import { redis } from "../configs/redis.ts"
import { PDFLoader } from "@langchain/community/document_loaders/fs/pdf";
import { RecursiveCharacterTextSplitter } from '@langchain/textsplitters'
import { tryCatch } from "src/utils/tryCatch.js";
import fs from 'fs'
import { AddToEmbedingQueue } from "src/queues/embeding.js";
import { AddToSummaryQueue } from "src/queues/summary.js";
import { createDocs } from "../db/queries.ts";
import { createLogger } from "src/configs/pino.js";

const logger=createLogger()

const splitter = new RecursiveCharacterTextSplitter({
    chunkSize: 1000,
    chunkOverlap: 200,
});


const SplitingFunc = async (job: Job) => {
    if (!job.data?.filepath.trim()) {
        logger.error("No filepath present")
        return null
    }

    const filePath = job.data?.filepath
    const chatId = job.data?.chatId
    const userId = job.data?.userId
    const title = job.data?.fileName

    //loading the pdf content
    const loader = new PDFLoader(filePath)
    const { data: docs, error: docsError } = await tryCatch(loader.load())

    if (docsError) {
        logger.error("Failed to load the pdf content")
        throw new Error("Failed to load the pdf content")
    }

    //spliting the pdf content to text for embadding
    const { data: texts, error: textsError } = await tryCatch(splitter.splitDocuments(docs))

    if (textsError) {
        logger.error("Failed to split the texts content")
        throw new Error("Failed to split the texts content")
    }

    const { data, error: SaveDocsError } = await tryCatch(createDocs({ title, user_id: userId, chat_id: chatId, original_text: texts }))

    if (SaveDocsError) {
        logger.error("Failed to save the original text")
        throw new Error("Failed to save the original text")
    }


    const newTexts = texts.map(text => {
        const metadata = text.metadata
        const newMetadata = {
            ...metadata,
            chatId: chatId,
            userId,
            docId: data[0].id
        }
        text.metadata = newMetadata
        return text
    })


    const { error: SummaryQueueError } = await tryCatch(AddToSummaryQueue({ content: newTexts, docId: data[0].id }))

    if (SummaryQueueError) {
        logger.error("Failed to add the data to summary queue ")
    }

    const { error: EmbeddingQueueError } = await tryCatch(AddToEmbedingQueue(newTexts))

    if (EmbeddingQueueError) {
        logger.error("Failed to add the data to embeding queue")
    }

    if (filePath && texts.length > 0) {
        try {
            //before removing the file just store the texts inthe db so that it can be used later on
            await fs.promises.unlink(filePath)
        } catch (unlinkErr) {
            logger.error(`Failed to clean up file: ${unlinkErr}`)
        }
    }

    return null
}

export const TextSplitingWorker = new Worker('text-spliter', SplitingFunc, { connection: redis })

TextSplitingWorker.on("ready", () => {
    logger.info("Started the worker text-spliter")
})

TextSplitingWorker.on("error", (error) => {
    logger.error("Error detected in text-spliter" + error.message)
})