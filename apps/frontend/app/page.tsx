export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      <header className="container mx-auto px-4 py-6">
        <nav className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-blue-600">Pulse AI Studio</h1>
          <div className="space-x-4">
            <a href="/chat" className="text-gray-700 hover:text-blue-600">
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
          
          <div className="flex justify-center gap-4">
            <a
              href="/chat"
              className="px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
            >
              ابدأ مجانًا
            </a>
          </div>
        </div>

        <div className="mt-32 grid md:grid-cols-3 gap-8">
          <div className="p-6 bg-white rounded-lg shadow-sm">
            <h3 className="text-xl font-bold mb-2">🤖 محادثة ذكية</h3>
            <p className="text-gray-600">
              GPT-4, Claude, Gemini – اختر الأفضل لمهمتك
            </p>
          </div>
          <div className="p-6 bg-white rounded-lg shadow-sm">
            <h3 className="text-xl font-bold mb-2">📄 صانع السيرة الذاتية</h3>
            <p className="text-gray-600">
              سير ذاتية احترافية بالعربية والإنجليزية
            </p>
          </div>
          <div className="p-6 bg-white rounded-lg shadow-sm">
            <h3 className="text-xl font-bold mb-2">🎨 صور وفيديو</h3>
            <p className="text-gray-600">
              توليد وتعديل بأحدث نماذج الذكاء الاصطناعي
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}

