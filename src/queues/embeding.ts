import { Queue } from 'bullmq'
import { tryCatch } from '../libs/tryCatch.js'
import { redis } from 'src/libs/redis.js'

export const EmbedingQueue = new Queue('embeding', {
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

export async function AddToEmbedingQueue(payload: { filepath: string }): Promise<{ id: string }> {
    const { data, error } = await tryCatch(EmbedingQueue.add('embeding', payload))
    if (error || !data?.id) {
        return { id: '' }
    }

    return { id: data.id }
}