import { Job, Worker } from "bullmq";
import { redis } from "../configs/redis.js";
import { model } from "../configs/ai-model.js";
import { tryCatch } from "src/utils/tryCatch.js";
import type { EmbeddingsInterface } from "@langchain/core/embeddings";
import { QdrantVectorStore } from "@langchain/qdrant";

class CustomEmbeddings implements EmbeddingsInterface {
    async embedDocuments(texts: string[]): Promise<number[][]> {
        return model.embedDocuments(texts);
    }

    async embedQuery(text: string): Promise<number[]> {
        return (await model.embedDocuments([text]))[0];
    }
}

let vectorStore: QdrantVectorStore | null = null;

async function getVectorStore() {
    if (!vectorStore) {
        const embeddings = new CustomEmbeddings();
        vectorStore = await QdrantVectorStore.fromExistingCollection(embeddings, {
            url: "http://localhost:6333",
            collectionName: "rag",
        });
        console.log("Qdrant VectorStore initialized ✅");
    }
    return vectorStore;
}


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
