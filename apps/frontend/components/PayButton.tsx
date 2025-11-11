"use client";

import { useState } from "react";
import { payments } from "@/lib/api";

interface PayButtonProps {
  planId: string;
  planName: string;
  locale?: "ar" | "en";
}

export function PayButton({ planId, planName, locale = "ar" }: PayButtonProps) {
  const [loading, setLoading] = useState(false);
  const isArabic = locale === "ar";

  const handleCheckout = async () => {
    setLoading(true);
    try {
      const session = await payments.createCheckout(planId, "hyperpay");
      // Redirect to payment page
      window.location.href = session.redirect_url;
    } catch (error: any) {
      alert(error.message || "Payment failed");
      setLoading(false);
    }
  };

  return (
    <button
      onClick={handleCheckout}
      disabled={loading}
      className="w-full py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
    >
      {loading
        ? (isArabic ? "جارٍ التحميل..." : "Loading...")
        : (isArabic ? "اشترك الآن" : "Subscribe Now")}
    </button>
  );
}

