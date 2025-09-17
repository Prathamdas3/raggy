import { betterAuth, } from 'better-auth'
import { drizzleAdapter } from "better-auth/adapters/drizzle";
import { database } from '../db/index.ts';
import { user } from '../db/schema.ts';

export const auth = betterAuth({
    database: drizzleAdapter(database, {
        provider: "pg",
    },),
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
    user: {
        fields: {
            name: 'first_name',
        },
        additionalFields: {
            last_name: {
                type: "string",
                required: false,
                defaultValue: null,
                input: true
            }

        }
    }
})

export type AuthType = {
    user: typeof auth.$Infer.Session.user | null
    session: typeof auth.$Infer.Session.session | null
}