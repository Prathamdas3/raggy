import { Queue } from 'bullmq'
import { tryCatch } from '../libs/tryCatch.js'
import { redis } from 'src/libs/redis.js'

export const TextSplitingQueue = new Queue('text-spliter', {
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
    },
})

export async function AddToTextSplitingQueue(payload: { filepath: string }): Promise<{ id: string }> {
    const { data, error } = await tryCatch(TextSplitingQueue.add('text-spliter', payload))
    if (error || !data?.id) {
        return { id: '' }
    }

    return { id: data.id }
}
