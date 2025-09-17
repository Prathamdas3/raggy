import { bodyLimit } from "hono/body-limit";
import { validator } from 'hono/validator'
import path from "node:path";
import z from 'zod'
import fs from 'fs'
import { tryCatch } from "src/utils/tryCatch.js";
import { randomUUID } from "node:crypto";
import { AddToTextSplitingQueue } from "src/queues/text-spliter.js";
import { createRouter } from "../../configs/app.ts";

const schema = z.object({
    file: z.custom<File>((val) => val instanceof File, {
        message: 'File is required',
    })
})

const router = createRouter()

router
    .use(
        async (c, next) => {
            //this is to only allow data from the multipart content not anyother
            const contentType = c.req.header('content-type') || ''
            if (!contentType.startsWith('multipart/form-data')) {
                return c.text('Only multipart/form-data is allowed', 415)
            }
            await next()
        }
    )
    .post( 

        bodyLimit({
            //this is to fix the size of my content
            maxSize: 5 * 1024 * 1024,//5mb,
            onError: (c) => {
                c.status(400)
                return c.json({ body: "FileSize should be below 5mb" })
            }
        }),

        validator('form',
            (value, c) => {
                //this is validating the content of my req and also checking the file type 
                const parsed = schema.safeParse(value)
                const allowedTypes = ['image/jpeg', 'image/png', 'application/pdf']
                if (!parsed.success) {
                    c.status(400)
                    return c.json({ body: "No files uploaded" })
                }

                if (!allowedTypes.includes(parsed.data.file.type)) {
                    c.status(415)
                    return c.json({ body: 'Invalid file type' })
                }
                return parsed.data
            }),

        async (c) => {
            const { file } = c.req.valid('form')

            //temporary file upload
            // Ensure uploads directory exists inside public/
            const uploadDir = path.join(process.cwd(), 'public', 'temp')
            if (!fs.existsSync(uploadDir)) {
                fs.mkdirSync(uploadDir, { recursive: true })
            }

            // Sanitize filename (remove dangerous chars)
            const safeName = file.name.replace(/[^a-zA-Z0-9._-]/g, '')

            //Generate unique filename to prevent overwrite
            const uniqueName = `${Date.now()}-${randomUUID()}-${safeName}`
            const filePath = path.join(uploadDir, uniqueName)

            //Write file asynchronously
            const arrayBuffer = await file.arrayBuffer()
            const { error } = await tryCatch(fs.promises.writeFile(filePath, Buffer.from(arrayBuffer)))
            if (error) {
                if (filePath) {
                    try {
                        await fs.promises.unlink(filePath)
                    } catch (unlinkErr) {
                        console.error('Failed to clean up file:', unlinkErr)
                    }
                }

                c.status(500)
                return c.json({ body: "Upload Failed, please try again later" })
            }

            //adding the filepath to the queue
            const { data } = await tryCatch(AddToTextSplitingQueue({ filepath: filePath }))

            if (!data?.id.trim()) {
                console.log("failed to load the file to the queue")
            }

            c.status(200)
            return c.json({ body: "successfully uploaded the file" })
        }
    )

export default router