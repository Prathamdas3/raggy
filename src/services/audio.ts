import { Job, Worker } from 'bullmq'
import { redis } from '../configs/redis.ts'
import { KokoroTTS } from "kokoro-js";

(async () => {
    const model_id = "onnx-community/Kokoro-82M-ONNX";
    const tts = await KokoroTTS.from_pretrained(model_id, {
        dtype: "q8", // Options: "fp32", "fp16", "q8", "q4", "q4f16"
    });

    const text = "Hello world";
    
    const audio = await tts.generate(text, {
        // Use `tts.list_voices()` to list all available voices
        voice: "af_bella",
    });

    await audio.save("audio.wav");
})()

const AudioFunc = async (job: Job) => {
    // const model = await audioModel
    // const data = await model("Hello how are you", {})
}

export const AudioWorker = new Worker('audio', AudioFunc, { connection: redis })

AudioWorker.on("ready", () => {
    console.log("Started the worker for audio")
})

AudioWorker.on("error", (error) => {
    console.log("Error detected in audio worker" + error.message)
})