import { betterAuth } from "better-auth";
import { jwt } from "better-auth/plugins";
import { Pool } from "pg";

// Create Neon connection pool with explicit SSL config
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: {
    rejectUnauthorized: false,
  },
});

export const auth = betterAuth({
  // Database configuration for Neon Serverless
  database: pool,

  // Email and password authentication
  emailAndPassword: {
    enabled: true,
    requireEmailVerification: false, // Set to true for production
  },

  // JWT plugin for token generation
  plugins: [
    jwt(),
  ],

  // Session configuration
  session: {
    expiresIn: 60 * 60 * 24 * 7, // 7 days
    updateAge: 60 * 60 * 24, // Update session every 24 hours
    cookieCache: {
      enabled: true,
      maxAge: 60 * 5, // Cache for 5 minutes
    },
  },

  // Base URL for authentication endpoints
  baseURL: process.env.BETTER_AUTH_URL || "http://localhost:3000",

  // Advanced security options
  advanced: {
    cookiePrefix: "better-auth",
    // Phase IV (K2): the container runs NODE_ENV=production but is served over
    // plain http://localhost:30080. Rather than rely on browsers treating
    // localhost as a secure context, the Secure attribute is overridable.
    // Default preserves the previous production-derived behaviour exactly, so
    // Phase III is unaffected.
    useSecureCookies:
      process.env.BETTER_AUTH_SECURE_COOKIES !== undefined
        ? process.env.BETTER_AUTH_SECURE_COOKIES === "true"
        : process.env.NODE_ENV === "production",
    crossSubDomainCookies: {
      enabled: false,
    },
  },

  // Trust host for deployment.
  // Phase IV (K1, FR-007): allowed origins are deploy-time configuration and
  // must not be embedded in the repository. Derived from ALLOWED_ORIGINS —
  // the same variable the backend uses for CORS — parsed as a comma-separated
  // list to match backend-api/src/config/settings.py:normalize_allowed_origins.
  // The previous hardcoded values remain the default so Phase III is unchanged.
  trustedOrigins: [
    ...(process.env.ALLOWED_ORIGINS
      ? process.env.ALLOWED_ORIGINS.split(",")
          .map((origin) => origin.trim())
          .filter(Boolean)
      : ["http://localhost:3000", "https://q4-hackathon-2.vercel.app"]),
    ...(process.env.VERCEL_URL ? [`https://${process.env.VERCEL_URL}`] : []),
  ],
});

// Export types for use in other files
export type Session = typeof auth.$Infer.Session;
export type User = typeof auth.$Infer.Session.user;
