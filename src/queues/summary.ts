import { Queue } from 'bullmq'
import { tryCatch } from '../utils/tryCatch.js'
import { redis } from 'src/configs/redis.js'

export const SummaryQueue = new Queue('summary', {
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

export async function AddToSummaryQueue(payload: { content: any,docId:string}): Promise<{ id: string }> {
    const { data, error } = await tryCatch(SummaryQueue.add('summary', payload))
    if (error || !data?.id) {
        return { id: '' }
    }

    return { id: data.id }
}