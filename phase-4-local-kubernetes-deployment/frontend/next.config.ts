import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /*
   * Emit a traced, self-contained server tree in .next/standalone so the
   * frontend container can run without shipping node_modules or the build
   * toolchain. Required by frontend/Dockerfile (Phase IV, D1).
   *
   * NOTE: standalone does NOT copy public/ or .next/static/ — the Dockerfile
   * copies those explicitly in the runner stage.
   */
  output: "standalone",
};

export default nextConfig;
