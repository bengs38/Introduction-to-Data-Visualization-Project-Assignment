import { Bot, Send, UserRound } from "lucide-react";
import { useState } from "react";

export default function ChatBox({ messages, onAsk, loading }) {
  const [question, setQuestion] = useState("");

  const submit = (event) => {
    event.preventDefault();
    const trimmed = question.trim();
    if (!trimmed) return;
    onAsk(trimmed);
    setQuestion("");
  };

  return (
    <section className="rounded-lg border border-line bg-panel p-5 shadow-soft">
      <h2 className="text-lg font-semibold text-ink">Veri Sohbeti</h2>
      <div className="scrollbar-thin mt-4 flex max-h-[380px] min-h-[260px] flex-col gap-3 overflow-auto rounded-md border border-line bg-slate-50 p-3">
        {messages.length ? (
          messages.map((message, index) => (
            <div key={index} className={`flex gap-2 ${message.role === "user" ? "justify-end" : "justify-start"}`}>
              {message.role === "assistant" ? <Bot size={18} className="mt-2 shrink-0 text-brand" /> : null}
              <div
                className={`max-w-[88%] whitespace-pre-wrap rounded-lg px-3 py-2 text-sm leading-6 ${
                  message.role === "user" ? "bg-brand text-white" : "border border-line bg-white text-slate-700"
                }`}
              >
                {message.content}
              </div>
              {message.role === "user" ? <UserRound size={18} className="mt-2 shrink-0 text-slate-500" /> : null}
            </div>
          ))
        ) : (
          <div className="flex h-full items-center justify-center text-center text-sm text-slate-500">
            “Bu veride en önemli trend ne?” gibi bir soru sorabilirsiniz.
          </div>
        )}
      </div>
      <form onSubmit={submit} className="mt-4 flex gap-2">
        <input
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          className="min-w-0 flex-1 rounded-md border border-line px-3 py-2 text-sm outline-none transition focus:border-brand focus:ring-2 focus:ring-teal-100"
          placeholder="Veri hakkında soru yazın"
        />
        <button
          type="submit"
          disabled={loading}
          className="inline-flex h-10 w-10 items-center justify-center rounded-md bg-brand text-white transition hover:bg-teal-800 disabled:opacity-60"
          title="Gönder"
        >
          <Send size={18} />
        </button>
      </form>
    </section>
  );
}
