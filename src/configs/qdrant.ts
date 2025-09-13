import type { EmbeddingsInterface } from "@langchain/core/embeddings";
import { QdrantVectorStore } from "@langchain/qdrant";
import { env } from "./env.js";

let vectorStore: QdrantVectorStore | null = null;

export async function getVectorStore() {
    if (!vectorStore) {
        vectorStore = await QdrantVectorStore.fromExistingCollection([] as unknown as EmbeddingsInterface, {
            // url: env.QDRANT_URL!,
            url:"http://localhost:6333",
            collectionName: "rag",
        });
        console.log("Qdrant VectorStore initialized ✅");
    }
    return vectorStore;
}