import type { EmbeddingsInterface } from "@langchain/core/embeddings";
import { QdrantVectorStore } from "@langchain/qdrant";
import { embedingModel as model } from "./ai-model.js";
import { env } from "./env.js";

class CustomEmbeddings implements EmbeddingsInterface {
	async embedDocuments(texts: string[]): Promise<number[][]> {
		return model.embedDocuments(texts);
	}

	async embedQuery(text: string): Promise<number[]> {
		return (await model.embedDocuments([text]))[0];
	}
}

let vectorStore: QdrantVectorStore | null = null;

export async function getVectorStore() {
	if (!vectorStore) {
		const embeddings = new CustomEmbeddings();
		vectorStore = await QdrantVectorStore.fromExistingCollection(embeddings, {
			url: env.QDRANT_URL,
			collectionName: "rag",
		});
		console.log("Qdrant VectorStore initialized ✅");
	}
	return vectorStore;
}
