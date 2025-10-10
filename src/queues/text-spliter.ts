import { Queue } from "bullmq";
import { redis } from "src/configs/redis.js";
import { tryCatch } from "../utils/tryCatch.js";

export const TextSplitingQueue = new Queue("text-spliter", {
	connection: redis,
	defaultJobOptions: {
		removeOnComplete: {
			age: 10 * 60,
			count: 100,
		},
		removeOnFail: {
			age: 20 * 60,
			count: 500,
		},
	},
});

export async function AddToTextSplitingQueue(payload: {
	filepath: string;
	fileName: string;
	chatId: string;
	userId: string;
}): Promise<{ id: string }> {
	const { data, error } = await tryCatch(
		TextSplitingQueue.add("text-spliter", payload),
	);
	if (error || !data?.id) {
		return { id: "" };
	}

	return { id: data.id };
}
