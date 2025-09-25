import { Job, Worker } from "bullmq"
import { redis } from "../configs/redis.ts"
import { createStuffDocumentsChain } from "langchain/chains/combine_documents"
import { StringOutputParser } from "@langchain/core/output_parsers";
import { PromptTemplate } from "@langchain/core/prompts";
import { tryCatch } from "src/utils/tryCatch.js";
import { model as summaryModel } from "src/configs/ai-model.js";
import type { RunnableSequence } from "@langchain/core/runnables";
import { updateDocs } from "../db/queries.ts";
import { AddToAudioQueue } from "src/queues/audio.js";
import { createLogger } from "src/configs/pino.js";

const logger = createLogger()

let stuffChain: RunnableSequence<Record<string, unknown>, string> | null = null

async function getStuff() {
    if (!stuffChain) {
        const prompt = PromptTemplate.fromTemplate(`
Read the following text carefully. Then create a simple summary. The summary should be very clear and easy for a dyslexic child to understand. Please use:

- Short sentences (no more than 10 words).
- Simple, everyday words (avoid hard or complex terms).
- Repetition of important ideas so they are remembered.
- Line breaks or bullet points to separate ideas.
- Explain in a friendly, calm, and supportive tone.

Text to summarize:
{context}

Now, write the summary as if you are explaining to a dyslexic child. End with a quick “big idea” sentence that reminds them what everything means in the simplest way possible.
`)

        const outputParser = new StringOutputParser()

        stuffChain = await createStuffDocumentsChain({
            llm: summaryModel, outputParser, prompt,
        })
        logger.info("stuff chain initialized ✅");
    }
    return stuffChain
}


const SummaryFunc = async (job: Job) => {
    const content = job.data?.content
    if (content.length === 0) {
        logger.error("No content found")
        return null
    }
    const docId = job.data?.docId

    const chain = await getStuff()
    const { data, error: SummaryError } = await tryCatch(chain.invoke({ context: content }))

    if (SummaryError) {
        logger.error(`Failed to generate the summarized docs:${SummaryError.message}`)
        throw new Error("Failed to generate the summarized docs")
    }

    const { data:updatedSummaryList,error: SummarySaveError } = await tryCatch(updateDocs(docId, data))
    if (SummarySaveError) {
        logger.error("Failed to save the summary data")
        throw new Error("Failed to save the summary data")
    }

    if(updatedSummaryList.length===0){
        logger.error("Chat does not exists")
        throw new Error("No chat exists")
    }

    const { error: AudioQueueError } = await tryCatch(AddToAudioQueue({ answerId: docId, type: "chat" }))

    if (AudioQueueError) {
        logger.error("Failed to add the summary id in the audio queue for further processing")
        throw new Error("Failed to add the id in the audio queue")
    }

    return null
}

export const SummaryWorker = new Worker('summary', SummaryFunc, { connection: redis })

SummaryWorker.on("ready", () => {
    logger.info("Started the worker summary")
})

SummaryWorker.on("error", (error) => {
    logger.error("Error detected in summary" + error.message)
})



//prompt for map and reduce

//         const mapPrompt = ChatPromptTemplate.fromMessages([
//             ["user", "Write a concise summary of the following: \n\n{context}"],
//         ]);

//         let reduceTemplate = `
// The following is a set of summaries:
// {docs}
// Take these and distill it into a final, consolidated summary
// of the main themes.
// `;

//         const reducePrompt = ChatPromptTemplate.fromMessages([
//             ["user", reduceTemplate],
//         ]);
