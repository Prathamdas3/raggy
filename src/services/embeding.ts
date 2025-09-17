import { Job, Worker } from "bullmq";
import { redis } from "../configs/redis.ts";
import { tryCatch } from "src/utils/tryCatch.js";
import { getVectorStore } from "src/configs/qdrant.js";


const embedingFunc = async (job: Job) => {
    if (!job.data?.content || job.data.content.length === 0) {
        console.log("No text content found");
        return null;
    }

    const content = job.data.content.map((details: any) => ({
        pageContent: details.pageContent,
        metadata: details.metadata || {},
    }));

    const vectorStore = await getVectorStore()

    // store documents directly → Qdrant will call embeddings internally
    const { error } = await tryCatch(
        vectorStore.addDocuments(content)
    );

    if (error) {
        console.error("❌ Failed to store embeddings:", error);
        throw new Error("Failed to add documents to Qdrant");
    }

    return null;
};

export const EmbedingWorker = new Worker("embeding", embedingFunc, {
    connection: redis,
});

EmbedingWorker.on("ready", () => {
    console.log("Started the worker embeding");
});

EmbedingWorker.on("error", (error) => {
    console.error("Error detected in embeding:", error.message);
});
