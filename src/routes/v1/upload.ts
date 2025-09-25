import { bodyLimit } from "hono/body-limit";
import { validator } from 'hono/validator'
import path from "node:path";
import z from 'zod'
import fs from 'fs'
import { tryCatch } from "src/utils/tryCatch.js";
import { randomUUID } from "node:crypto";
import { AddToTextSplitingQueue } from "src/queues/text-spliter.js";
import { createRouter } from "../../configs/app.ts";
import { error, success } from "../../utils/response.ts";
import { getDocsByChatId } from "src/db/queries.js";

const schema = z.object({
    file: z.custom<File>((val) => val instanceof File, {
        message: 'File is required',
    }),
    chat_id: z.string().min(1, "chat_id must be more than 1 character")
})

const router = createRouter()
// This route handles uploading of documents
router
    .use(
        async (c, next) => {
            //this is to only allow data from the multipart content not anyother
            const contentType = c.req.header('content-type') || ''
            if (!contentType.startsWith('multipart/form-data')) {
                return c.json(error('Only multipart/form-data is allowed', "Invalid Input"), 400)
            }
            await next()
        }
    )
    .post(

        bodyLimit({
            //this is to fix the size of my content
            maxSize: 5 * 1024 * 1024,//5mb,
            onError: (c) => {
                return c.json(error("FileSize should be below 5mb", "Invalid Input"), 400)
            }
        }),

        validator('form',
            (value, c) => {
                //this is validating the content of my req and also checking the file type 
                const parsed = schema.safeParse(value)
                const allowedTypes = ['image/jpeg', 'image/png', 'application/pdf']
                if (!parsed.success) {
                    return c.json(error(parsed.error.message, "Invalid Input"), 400)
                }

                if (!allowedTypes.includes(parsed.data.file.type)) {
                    return c.json(error(`Invalid file type, file must be one of these types ${allowedTypes.join(',')}`, "Invalid Input"), 400)
                }
                return parsed.data
            }),

        async (c) => {
            const logger = c.get('logger')
            const { file, chat_id } = c.req.valid('form')
            const user = c.get('user')

            if (!user) {
                return c.json(error("No user found", "Unauthorized"), 401)
            }

            const {data:oldDoc,error:oldDocError}=await tryCatch(getDocsByChatId(chat_id))

            if(oldDocError||!oldDoc){
                return c.json(error("This chat already has a docs attach to it, every chat can have only one doc attach to it"))
            }


            const fileName = file.name
            const userId = user.id

            //temporary file upload
            // Ensure uploads directory exists inside public/
            const uploadDir = path.join(process.cwd(), 'public', 'temp')
            if (!fs.existsSync(uploadDir)) {
                fs.mkdirSync(uploadDir, { recursive: true })
            }

            // Sanitize filename (remove dangerous chars)
            const safeName = fileName.replace(/[^a-zA-Z0-9._-]/g, '')

            //Generate unique filename to prevent overwrite
            const uniqueName = `${Date.now()}-${randomUUID()}-${safeName}`
            const filePath = path.join(uploadDir, uniqueName)

            //Write file asynchronously
            const arrayBuffer = await file.arrayBuffer()
            const { error: SaveFileError } = await tryCatch(fs.promises.writeFile(filePath, Buffer.from(arrayBuffer)))
            if (SaveFileError) {
                if (filePath) {
                    try {
                        await fs.promises.unlink(filePath)
                    } catch (unlinkErr) {
                        logger.error(`Failed to clean up file: ${unlinkErr}`)
                    }
                }

                return c.json(error("Upload Failed, please try again later", "Internal Server Error"), 500)
            }

            //adding the filepath to the queue
            const { data } = await tryCatch(AddToTextSplitingQueue({ filepath: filePath, fileName, chatId: chat_id, userId }))

            if (!data?.id.trim()) {
                logger.error("Failed to load the file to the queue")
            }

            return c.json(success("successfully uploaded the file"), 200)
        }
    )

export default router