import { Job, Worker } from 'bullmq'
import { redis } from '../configs/redis.ts'
import { KokoroTTS } from "kokoro-js";
import { marked } from 'marked'
import { htmlToText } from 'html-to-text'
import { addAudioLink, addMessageAudioLink, getAnswerById, getDocsByChatId } from 'src/db/queries.js';
import { tryCatch } from 'src/utils/tryCatch.js';
import path from 'node:path';
import fs from 'fs'
import { randomUUID } from 'node:crypto';

const createCleanText = async (text: string): Promise<string> => {
    const html = await marked.parse(text)
    const cleanText = htmlToText(html, {
        wordwrap: false
    })

    return cleanText
}

let TTS: KokoroTTS | null = null

const getTTS = async () => {
    if (!TTS) {
        const model_id = "onnx-community/Kokoro-82M-ONNX";
        TTS = await KokoroTTS.from_pretrained(model_id, {
            dtype: "q8", // Options: "fp32", "fp16", "q8", "q4", "q4f16"
        });
        console.log("TTS init")
    }
    return TTS
}

const AudioFunc = async (job: Job<{ id: string, type: "chat" | "message" }>) => {
    const { id, type } = job.data
    if (!id.trim() || !type.trim()) {
        console.log("No id or type found")
        return null
    }

    const tts = await getTTS()
    let text = ''

    const uploadDir = path.join(process.cwd(), 'public', 'audio')
    if (!fs.existsSync(uploadDir)) {
        fs.mkdirSync(uploadDir, { recursive: true })
    }

    //Generate unique filename to prevent overwrite
    const uniqueName = `${Date.now()}-${randomUUID()}-${id}-${type}.wav`
    const filePath = path.join(uploadDir, uniqueName)

    if (type == "chat") {
        const { data, error } = await tryCatch(getDocsByChatId(id))
        if (error || !data?.summary_text?.trim()) {
            throw new Error("Failed to fetch summary for the audio generation")
        }
        text = await createCleanText(data.summary_text)
    } else if (type === "message") {
        const { data, error } = await tryCatch(getAnswerById(id))

        if (error || !data?.content.trim()) {
            throw new Error("Failed to fetch the content of the message for the audio generation")
        }

        text = await createCleanText(data.content)
    }

    if (!text.trim()) {
        console.log("No text found for the audio generation")
    }

    const audio = await tts.generate(text, {
        voice: "af_bella",
    })

    const { error } = await tryCatch(audio.save(filePath))

    if (error) {
        console.log(`Failed to save the audio with filepath ${filePath}`)
        try {
            await fs.promises.unlink(filePath)
        } catch (unlinkErr) {
            console.log(`Failed to clean up file: ${unlinkErr}`)
        }
        throw new Error("Failed to save the audio")
    }

    //add the logic of the supabase store or r2 store here
    
    if (type === "chat") {
        const { error } = await tryCatch(addAudioLink(id, filePath))
        if (error) {
            console.log("Failed to add the audio link for the summary")
        }
    } else if (type == "message") {
        const { error } = await tryCatch(addMessageAudioLink(id, filePath))
        if (error) {
            console.log("Failed to add the audio link for the answer")
        }
    }
    //then unlink the file from the temporary audio storage

    return null
}

export const AudioWorker = new Worker('audio', AudioFunc, { connection: redis })

AudioWorker.on("ready", () => {
    console.log("Started the worker for audio")
})

AudioWorker.on("error", (error) => {
    console.log("Error detected in audio worker" + error.message)
})