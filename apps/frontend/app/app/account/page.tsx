"use client";

import { useState, useEffect } from "react";
import { Sidebar } from "@/components/Sidebar";
import { PlanCard } from "@/components/PlanCard";
import { UsageBadge } from "@/components/UsageBadge";

export default function AccountPage() {
  const [user, setUser] = useState<any>(null);
  const [usage, setUsage] = useState<any>(null);
  const [payments, setPayments] = useState<any[]>([]);

  useEffect(() => {
    // TODO: Fetch user data, usage, and payment history
    // const userData = await auth.me();
    // const usageData = await usage.me();
    // const paymentData = await payments.history();
    
    // Mock data
    setUser({ email: "user@example.com", locale: "ar" });
    setUsage({
      tokens_used: 50000,
      token_limit: 150000,
      images_used: 5,
      image_limit: 10,
      videos_used: 1,
      video_limit: 2,
      plan_name: "Starter",
    });
    setPayments([]);
  }, []);

  if (!user) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="flex h-screen">
      <Sidebar locale="ar" />
      <div className="flex-1 overflow-y-auto p-8 bg-gray-50">
        <div className="max-w-6xl mx-auto">
          <h1 className="text-3xl font-bold mb-8">إعدادات الحساب</h1>

          {/* Account Info */}
          <div className="bg-white rounded-lg shadow p-6 mb-8">
            <h2 className="text-xl font-bold mb-4">معلومات الحساب</h2>
            <div className="space-y-2">
              <div>
                <span className="font-medium">البريد الإلكتروني:</span>{" "}
                {user.email}
              </div>
              <div>
                <span className="font-medium">الخطة الحالية:</span>{" "}
                {usage?.plan_name}
              </div>
            </div>
          </div>

          {/* Usage Summary */}
          {usage && (
            <div className="bg-white rounded-lg shadow p-6 mb-8">
              <h2 className="text-xl font-bold mb-4">الاستخدام الشهري</h2>
              <div className="grid md:grid-cols-3 gap-4">
                <UsageBadge
                  used={usage.tokens_used}
                  limit={usage.token_limit}
                  label="الرموز"
                  locale="ar"
                />
                <UsageBadge
                  used={usage.images_used}
                  limit={usage.image_limit}
                  label="الصور"
                  locale="ar"
                />
                <UsageBadge
                  used={usage.videos_used}
                  limit={usage.video_limit}
                  label="الفيديوهات"
                  locale="ar"
                />
              </div>
            </div>
          )}

          {/* Upgrade Plans */}
          <div className="bg-white rounded-lg shadow p-6 mb-8">
            <h2 className="text-xl font-bold mb-4">ترقية الخطة</h2>
            <div className="grid md:grid-cols-3 gap-6">
              <PlanCard
                planId="starter"
                name="Starter"
                nameAr="المبتدئ"
                price={3}
                tokenLimit={150000}
                imageLimit={10}
                videoLimit={2}
                features={["AI Chat", "CV Maker"]}
                featuresAr={["الدردشة الذكية", "صانع السيرة"]}
                locale="ar"
              />
              <PlanCard
                planId="pro"
                name="Pro"
                nameAr="المحترف"
                price={5}
                tokenLimit={400000}
                imageLimit={30}
                videoLimit={5}
                features={["All Starter features", "Slides Maker", "Video Editor"]}
                featuresAr={["جميع مزايا المبتدئ", "صانع العروض", "محرر الفيديو"]}
                popular
                locale="ar"
              />
              <PlanCard
                planId="creator"
                name="Creator"
                nameAr="المبدع"
                price={7}
                tokenLimit={1000000}
                imageLimit={60}
                videoLimit={10}
                features={["All Pro features", "Priority Support"]}
                featuresAr={["جميع مزايا المحترف", "دعم أولوية"]}
                locale="ar"
              />
            </div>
          </div>

          {/* Payment History */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold mb-4">سجل المدفوعات</h2>
            {payments.length === 0 ? (
              <p className="text-gray-500">لا توجد مدفوعات بعد</p>
            ) : (
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-right py-2">التاريخ</th>
                    <th className="text-right py-2">الخطة</th>
                    <th className="text-right py-2">المبلغ</th>
                    <th className="text-right py-2">الحالة</th>
                  </tr>
                </thead>
                <tbody>
                  {payments.map((payment, index) => (
                    <tr key={index} className="border-b">
                      <td className="py-2">{payment.date}</td>
                      <td className="py-2">{payment.plan}</td>
                      <td className="py-2">{payment.amount} د.أ</td>
                      <td className="py-2">{payment.status}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

