"use client";

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { auth } from "@/lib/api";

export default function VerifyPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [status, setStatus] = useState<"loading" | "success" | "error">("loading");
  const [error, setError] = useState("");

  useEffect(() => {
    const token = searchParams.get("token");
    
    if (!token) {
      setStatus("error");
      setError("Invalid verification link");
      return;
    }

    const verify = async () => {
      try {
        await auth.verifyMagicLink(token);
        setStatus("success");
        // Redirect to chat after 2 seconds
        setTimeout(() => {
          router.push("/app/chat");
        }, 2000);
      } catch (err: any) {
        setStatus("error");
        setError(err.message || "Verification failed");
      }
    };

    verify();
  }, [searchParams, router]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8 text-center">
        {status === "loading" && (
          <>
            <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Verifying...</h2>
            <p className="text-gray-600">Please wait while we verify your magic link</p>
          </>
        )}

        {status === "success" && (
          <>
            <div className="text-6xl mb-4">✅</div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Success!</h2>
            <p className="text-gray-600">You're being redirected to the chat...</p>
          </>
        )}

        {status === "error" && (
          <>
            <div className="text-6xl mb-4">❌</div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Verification Failed</h2>
            <p className="text-red-600 mb-4">{error}</p>
            <button
              onClick={() => router.push("/")}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
            >
              Go Back Home
            </button>
          </>
        )}
      </div>
    </div>
  );
}

