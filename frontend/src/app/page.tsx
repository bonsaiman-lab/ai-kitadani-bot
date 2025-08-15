"use client";
import React, { useState } from "react";

interface KnowledgeChunk {
  rank: number;
  title: string;
  category: string;
  summary: string;
  content: string;
  score: number;
}

export default function Home() {
  const examples = [
    "例）盆栽の水やり頻度を教えて",
    "例）葉が黄色くなった原因は？",
    "例）植え替えはいつすればいい？"
  ];
  const [placeholder, setPlaceholder] = useState(examples[Math.floor(Math.random() * examples.length)]);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [knowledge, setKnowledge] = useState<KnowledgeChunk[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setAnswer("");
    setKnowledge([]);
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
    try {
      const res = await fetch(`${apiUrl}/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question })
      });
      if (!res.ok) throw new Error("APIエラー: " + res.statusText);
      const data = await res.json();
      setAnswer(data.answer);
      setKnowledge(Array.isArray(data.matched_chunks) ? data.matched_chunks : []);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-green-50 flex flex-col items-center p-4">
      <img src="/ai-kitadani.png" alt="AI北谷くん" className="w-28 h-28 rounded-full shadow-lg mt-10 mb-6 border-4 border-green-300 bg-white object-cover" style={{objectFit:'cover', width:'112px', height:'112px'}} />
      <h1 className="text-4xl font-extrabold mb-4 text-green-900 drop-shadow-sm">AI北谷くん α版</h1>
      <div className="mb-8 text-green-800 text-lg text-center leading-relaxed px-2 max-w-xl">北谷養盛園4代目 北谷隆一の知見が答える、松盆栽専門AIチャットボット！</div>
      <form onSubmit={handleSubmit} className="w-full max-w-xl flex gap-2 mb-6">
        <input
          type="text"
          className="flex-1 rounded border px-4 py-2 text-lg text-green-900 placeholder-green-400"
          placeholder={placeholder}
          value={question}
          onChange={e => setQuestion(e.target.value)}
          disabled={loading}
          required
        />
        <button
          type="submit"
          className="bg-green-700 text-white px-6 py-2 rounded font-semibold hover:bg-green-800 disabled:opacity-50"
          disabled={loading}
        >
          送信
        </button>
      </form>
      {loading && <div className="text-green-700 mb-4">AIが回答中です...</div>}
      {error && <div className="text-red-600 mb-4">{error}</div>}
      {answer && (
        <div className="w-full max-w-xl bg-white rounded shadow p-4 mb-6 border-2 border-green-200">
          <div className="font-bold text-green-800 mb-2 flex items-center gap-2">
            <img src="/ai-kitadani.png" alt="AI北谷くん" className="w-8 h-8 rounded-full border border-green-300 object-cover" style={{objectFit:'cover', width:'32px', height:'32px'}} />
            AI北谷くんの回答
          </div>
          <div className="whitespace-pre-line mb-2 text-green-900 font-medium">{answer}</div>
        </div>
      )}
      {knowledge.length > 0 && (
        <div className="w-full max-w-xl bg-white rounded shadow p-4">
          <div className="font-bold text-green-800 mb-2">根拠ナレッジ（上位{knowledge.length}件）</div>
          {knowledge.map(chunk => (
            <div key={chunk.rank} className="mb-4 border-b pb-2 last:border-b-0 last:pb-0">
              <div className="font-semibold">[{chunk.rank}] {chunk.title} &lt;{chunk.category}&gt; (score: {typeof chunk.score === 'number' ? chunk.score.toFixed(4) : 'N/A'})</div>
              <div className="text-sm text-gray-700 mb-1">要約: {chunk.summary}</div>
              <div className="text-sm text-gray-600">本文: {chunk.content}</div>
            </div>
          ))}
        </div>
      )}
      <footer className="mt-10 text-green-400 text-sm font-bold">{new Date().getFullYear()} © AI北谷くん</footer>
    </main>
  );
}
