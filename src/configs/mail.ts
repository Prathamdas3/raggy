import nodemailer from 'nodemailer'
import { env } from './env.ts'

export const transport = nodemailer.createTransport({
    service: 'gmail',
    host: env.MAILTRAP_HOST!,
    port: env.MAILTRAP_PORT!,
    auth: {
        user: env.MAILTRAP_AUTH_USER!,
        pass: env.MAILTRAP_AUTH_PASS!,
    },
} as nodemailer.TransportOptions)