import { betterAuth, } from 'better-auth'
import { drizzleAdapter } from "better-auth/adapters/drizzle";
import { database } from '../db/index.ts';
import { env } from './env.ts';
import { account, session, user, verification } from '../db/schema.ts';
// import { transport } from 'src/configs/mail.js'

export const auth = betterAuth({
    database: drizzleAdapter(database, {
        provider: "pg",
        schema: {
            user, account, verification, session
        }
    }),
    trustedOrigins: ["http://locahost:5173"],
    emailAndPassword: {
        enabled: true,
        autoSignIn: true
        // requireEmailVerification: true
    },
    session: {
        cookieCache: {
            enabled: true,
            maxAge: 5 * 60
        },
        expiresIn: 60 * 60 * 24 * 7, // 7 days
        updateAge: 60 * 60 * 24
    },
    // emailVerification: {
    //     sendOnSignUp: true,
    //     sendVerificationEmail: async ({ user, url, token }, request) => {
    //         await transport.sendMail({
    //             to: user.email,
    //             subject: 'Verify your email address',
    //             text: `Click the link to verify your email: ${url}`,
    //         });
    //     },

    // },
    logger: {
        level: 'debug',
        disabled: false
    },
    baseURL: env.BETTER_AUTH_URL,
    secret: env.BETTER_AUTH_SECRET,
})