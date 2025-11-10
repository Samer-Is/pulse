export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      <header className="container mx-auto px-4 py-6">
        <nav className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-blue-600">Pulse AI Studio</h1>
          <div className="space-x-4">
            <a href="/app/chat" className="text-gray-700 hover:text-blue-600">
              تسجيل الدخول
            </a>
          </div>
        </nav>
      </header>

      <main className="container mx-auto px-4 py-20">
        <div className="text-center max-w-4xl mx-auto">
          <h2 className="text-5xl font-bold text-gray-900 mb-6">
            استوديو الذكاء الاصطناعي الشامل
          </h2>
          <p className="text-xl text-gray-600 mb-8">
            محادثة، صور، فيديو، سير ذاتية، وعروض تقديمية – كل شيء في منصة واحدة
          </p>
          <p className="text-lg text-gray-500 mb-12">
            مصمم خصيصًا للمستخدم العربي 🇯🇴
          </p>
          
          <div className="flex justify-center gap-4">
            <a
              href="/app/chat"
              className="px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
            >
              ابدأ مجانًا
            </a>
            <a
              href="#features"
              className="px-8 py-3 border border-blue-600 text-blue-600 rounded-lg hover:bg-blue-50 transition"
            >
              اعرف المزيد
            </a>
          </div>
        </div>

        {/* Features Section */}
        <div id="features" className="mt-32 grid md:grid-cols-3 gap-8">
          <div className="p-6 bg-white rounded-lg shadow-sm">
            <h3 className="text-xl font-bold mb-2">🤖 محادثة ذكية</h3>
            <p className="text-gray-600">
              GPT-4, Claude 4.5, Gemini Pro – اختر الأفضل لمهمتك
            </p>
          </div>
          <div className="p-6 bg-white rounded-lg shadow-sm">
            <h3 className="text-xl font-bold mb-2">📄 صانع السيرة الذاتية</h3>
            <p className="text-gray-600">
              سير ATS-friendly بالعربية والإنجليزية في دقائق
            </p>
          </div>
          <div className="p-6 bg-white rounded-lg shadow-sm">
            <h3 className="text-xl font-bold mb-2">🎨 صور وفيديو</h3>
            <p className="text-gray-600">
              توليد وتعديل بأحدث نماذج الذكاء الاصطناعي
            </p>
          </div>
        </div>

        {/* Pricing Section */}
        <div className="mt-32">
          <h2 className="text-3xl font-bold text-center mb-12">الخطط والأسعار</h2>
          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            <div className="p-6 bg-white rounded-lg shadow-sm border-2 border-gray-200">
              <h3 className="text-2xl font-bold mb-2">Starter</h3>
              <p className="text-4xl font-bold text-blue-600 mb-4">3 دينار/شهر</p>
              <ul className="space-y-2 text-gray-600">
                <li>✅ 150 ألف كلمة</li>
                <li>✅ 10 صور</li>
                <li>✅ 2 فيديو</li>
                <li>✅ صانع السيرة الذاتية</li>
              </ul>
            </div>
            <div className="p-6 bg-blue-50 rounded-lg shadow-md border-2 border-blue-600">
              <div className="bg-blue-600 text-white px-3 py-1 rounded-full text-sm inline-block mb-2">
                الأكثر شعبية
              </div>
              <h3 className="text-2xl font-bold mb-2">Pro</h3>
              <p className="text-4xl font-bold text-blue-600 mb-4">5 دنانير/شهر</p>
              <ul className="space-y-2 text-gray-600">
                <li>✅ 400 ألف كلمة</li>
                <li>✅ 30 صورة</li>
                <li>✅ 5 فيديوهات</li>
                <li>✅ السيرة + العروض التقديمية</li>
              </ul>
            </div>
            <div className="p-6 bg-white rounded-lg shadow-sm border-2 border-gray-200">
              <h3 className="text-2xl font-bold mb-2">Creator</h3>
              <p className="text-4xl font-bold text-blue-600 mb-4">7 دنانير/شهر</p>
              <ul className="space-y-2 text-gray-600">
                <li>✅ مليون كلمة</li>
                <li>✅ 60 صورة</li>
                <li>✅ 10 فيديوهات</li>
                <li>✅ أدوات متقدمة</li>
              </ul>
            </div>
          </div>
        </div>
      </main>

      <footer className="bg-gray-50 mt-32 py-12">
        <div className="container mx-auto px-4 text-center text-gray-600">
          <p>© 2025 Pulse AI Studio. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}

