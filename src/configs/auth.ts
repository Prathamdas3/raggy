import { betterAuth, } from 'better-auth'
import { drizzleAdapter } from "better-auth/adapters/drizzle";
import { database } from '../db/index.ts';

export const auth = betterAuth({
    database: drizzleAdapter(database, {
        provider: "pg"
    }),
    trustedOrigins: ["http://locahost:5173"],
    emailAndPassword: {
        enabled: true,
        requireEmailVerification: true
    },
    user: {
        fields: {
            name: {
                // Auto-populate name from first_name + last_name
                transform: (user) => `${user.first_name} ${user.last_name || ''}`.trim()
            }
        }
    }
})

export type AuthType = {
    user: typeof auth.$Infer.Session.user | null
    session: typeof auth.$Infer.Session.session | null
}