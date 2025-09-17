import { betterAuth, } from 'better-auth'
import { drizzleAdapter } from "better-auth/adapters/drizzle";
import { database } from '../db/index.ts';
import { env } from './env.ts';
import { account, session, user, verification } from '../db/schema.ts';

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
        requireEmailVerification: true
    },
    session: {
        cookieCache: {
            enabled: true,
            maxAge: 5 * 60
        }
    },
    emailVerification: {
        sendOnSignUp: true,
    },
    logger: {
        level: 'debug',
        disabled: false
    },
    baseURL: env.BETTER_AUTH_URL,
    secret: env.BETTER_AUTH_SECRET,
})

export type AuthType = {
    user: typeof auth.$Infer.Session.user | null
    session: typeof auth.$Infer.Session.session | null
}