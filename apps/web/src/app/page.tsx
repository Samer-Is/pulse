export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="z-10 w-full max-w-5xl items-center justify-between font-mono text-sm">
        <h1 className="text-4xl font-bold text-center mb-8">Pulse AI Studio</h1>
        <p className="text-center text-muted-foreground mb-12">
          Multi-feature AI platform with Chat, Images, Videos, CV Maker, and Slide Maker
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div className="p-6 border rounded-lg">
            <h2 className="text-xl font-semibold mb-2">Chat</h2>
            <p className="text-sm text-muted-foreground">
              Multi-provider LLM chat with OpenAI, Anthropic, and Google Gemini
            </p>
          </div>
          <div className="p-6 border rounded-lg">
            <h2 className="text-xl font-semibold mb-2">Images</h2>
            <p className="text-sm text-muted-foreground">
              Text-to-image generation via Google Vertex AI Imagen
            </p>
          </div>
          <div className="p-6 border rounded-lg">
            <h2 className="text-xl font-semibold mb-2">Videos</h2>
            <p className="text-sm text-muted-foreground">
              Async video generation with Runway and Pika
            </p>
          </div>
          <div className="p-6 border rounded-lg">
            <h2 className="text-xl font-semibold mb-2">CV Maker</h2>
            <p className="text-sm text-muted-foreground">
              Create professional CVs and export as DOCX/PDF
            </p>
          </div>
          <div className="p-6 border rounded-lg">
            <h2 className="text-xl font-semibold mb-2">Slide Maker</h2>
            <p className="text-sm text-muted-foreground">
              Generate presentation slides and export as PPTX/PDF
            </p>
          </div>
          <div className="p-6 border rounded-lg">
            <h2 className="text-xl font-semibold mb-2">Admin</h2>
            <p className="text-sm text-muted-foreground">
              Manage users, subscriptions, and monitor usage
            </p>
          </div>
        </div>
      </div>
    </main>
  );
}

