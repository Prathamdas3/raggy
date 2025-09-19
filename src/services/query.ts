import { Job, Worker } from 'bullmq'
import { redis } from '../configs/redis.ts'
import { getVectorStore } from 'src/configs/qdrant.js'
import { mistralModel } from 'src/configs/ai-model.js'
import { pull } from "langchain/hub";
import { ChatPromptTemplate } from "@langchain/core/prompts";
import { tryCatch } from 'src/utils/tryCatch.js';

let prompt: ChatPromptTemplate<any, any> | null = null

const getPrompt = async () => {
    if (!prompt) {
        prompt = await pull<ChatPromptTemplate>("rlm/rag-prompt");
    }
    return prompt
}

const QueryFunc = async (job: Job) => {
    const { userId, chatId, question } = job?.data

    if (!userId.trim() || !chatId.trim() || !question.trim()) {
        console.log("chatId, userId, question any of them is empty")
        return null
    }

    const filter = {
        must: [
            { key: "metadata.chatId", match: { value: chatId } },
            { key: "metadata.userId", match: { value: userId } }
        ],
    }

    const vectorStore = await getVectorStore()
    const retrievedDocs = await vectorStore.similaritySearch(question, 2, filter)
    const docsContent = retrievedDocs.map((doc) => doc.pageContent).join("\n");
    const promptTemplate = await getPrompt()

    const samplePrompt = await promptTemplate.invoke({
        context: docsContent,
        question: question,
        instruction: `
You are a helpful teacher who explains things in a simple, clear, and supportive way. 
The reader is a child with dyslexia, so please follow these rules:
- Use short, simple sentences.
- Avoid difficult words when possible.
- Break ideas into small steps.
- Use examples from everyday life.
- Be kind, encouraging, and positive.
- Highlight the most important words clearly.

Now, using the given context, answer the question in a way that makes it easy for a child with dyslexia to understand.
`
    });

    const { data, error } = await tryCatch(mistralModel.invoke(samplePrompt))

    if (error) {
        console.log("Failed to generate the answer for the question")
    }

    console.log(data?.content)
    return null
}



export const QueryWorker = new Worker('querying', QueryFunc, { connection: redis })

QueryWorker.on("ready", () => {
    console.log("Started the worker for query")
})

QueryWorker.on("error", (error) => {
    console.log("Error detected in query" + error.message)
})