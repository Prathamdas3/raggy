import { Queue } from "bullmq";
import { redis } from "src/configs/redis.js";
import { tryCatch } from "src/utils/tryCatch.js";

export const QueryQueue = new Queue("querying", {
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

export async function AddToQueryQueue(payload: {
	chatId: string;
	userId: string;
	question: string;
	questionId: string | null;
}): Promise<{ id: string }> {
	const { data, error } = await tryCatch(QueryQueue.add("querying", payload));

	if (error || !data?.id) {
		return { id: "" };
	}

	return { id: data.id };
}
