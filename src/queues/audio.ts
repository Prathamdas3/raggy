import { Queue } from "bullmq";
import { tryCatch } from "src/utils/tryCatch.js";
import { redis } from 'src/configs/redis.js'

export const QueryQueue = new Queue('audio', {
    connection: redis,
    defaultJobOptions: {
        removeOnComplete: {
            age: 10 * 60,
            count: 100
        },
        removeOnFail: {
            age: 20 * 60,
            count: 500
        },
    }
})

export async function AddToAudioQueue(payload: { answerId: string, content: string }): Promise<{ id: string }> {
    const { data, error } = await tryCatch(QueryQueue.add('audio', payload))

    if (error || !data?.id) {
        return { id: '' }
    }

    return { id: data.id }
}