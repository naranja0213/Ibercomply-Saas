"use client";

import * as Sentry from "@sentry/nextjs";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  Sentry.captureException(error);

  return (
    <html lang="zh-CN">
      <body className="bg-slate-900 text-gray-100">
        <div className="min-h-screen flex items-center justify-center px-4 py-20">
          <div className="max-w-md w-full bg-slate-800/50 rounded-xl p-8 border border-slate-700 text-center">
            <div className="mb-4 text-4xl">⚠️</div>
            <h2 className="text-lg font-semibold mb-2">页面出现错误</h2>
            <p className="text-sm text-gray-400 mb-6">
              我们已记录该问题，请稍后重试。
            </p>
            <button
              onClick={() => reset()}
              className="inline-flex items-center justify-center bg-gradient-to-r from-purple-600 to-cyan-600 text-white font-semibold px-6 py-3 rounded-xl hover:from-purple-700 hover:to-cyan-700 transition-all"
            >
              重新加载
            </button>
          </div>
        </div>
      </body>
    </html>
  );
}
