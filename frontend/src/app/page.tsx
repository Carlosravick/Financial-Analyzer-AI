"use client";

import { useState } from "react";
import { Upload, MessageSquare, DollarSign, Percent, BarChart3, Send, AlertTriangle } from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";

export default function FinancialDashboard() {
  const [metrics, setMetrics] = useState<any>(null);
  const [insights, setInsights] = useState<string[]>([]);
  const [question, setQuestion] = useState("");
  const [chat, setChat] = useState<{ q: string; a: string }[]>([]);
  const [loading, setLoading] = useState(false);

  // Função para fazer Upload do CSV ou XLSX
  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files?.[0]) return;
    const file = e.target.files[0];
    const formData = new FormData();
    formData.append("file", file);

    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/upload", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      setMetrics(data.metrics);
      setInsights(data.insights || []);
      alert("Arquivo processado com sucesso!");
    } catch (err) {
      alert("Erro ao subir arquivo. Verifique o console.");
    } finally {
      setLoading(false);
    }
  };

  // Função para fazer Perguntas à IA (RAG ou Pandas)
  const handleAsk = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question) return;

    const userQ = question;
    setQuestion(""); // Limpa o input imediatamente
    setChat((prev) => [...prev, { q: userQ, a: "..." }]); // Exibe a pergunta na hora
    setLoading(true);

    try {
      const res = await fetch("http://localhost:8000/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: userQ }),
      });
      const data = await res.json();
      
      setChat((prev) => {
        const newChat = [...prev];
        newChat[newChat.length - 1].a = data.answer; // Substitui o "..." pela resposta real
        return newChat;
      });
    } catch (err) {
      setChat((prev) => {
        const newChat = [...prev];
        newChat[newChat.length - 1].a = "⚠️ Erro ao se comunicar com a IA.";
        return newChat;
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 text-white p-8 font-sans">
      {/* Header */}
      <header className="mb-12 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-emerald-400">Financial Analyzer AI</h1>
          <p className="text-slate-400">IA Inteligente com RAG & Agent Pandas</p>
        </div>
        
        <label className="flex items-center gap-2 bg-emerald-600 hover:bg-emerald-700 px-5 py-2.5 rounded-lg cursor-pointer transition font-medium shadow-lg">
          <Upload size={20} />
          <span>Carregar Dados (CSV/XLSX)</span>
          <input type="file" className="hidden" onChange={handleUpload} accept=".csv,.xlsx" />
        </label>
      </header>

      {/* Dashboard Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <Card title="Receita Total (Paga)" value={`R$ ${metrics?.receita_total?.toLocaleString() || "0"}`} icon={<DollarSign className="text-green-400" />} />
        <Card title="Ticket Médio" value={`R$ ${metrics?.ticket_medio?.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2}) || "0,00"}`} icon={<BarChart3 className="text-blue-400" />} />
        <Card title="Inadimplência" value={`${metrics?.taxa_inadimplencia?.toFixed(2) || "0,00"}%`} icon={<Percent className="text-red-400" />} />
        <Card title="Volume de Transações" value={metrics?.total_transacoes || "0"} icon={<MessageSquare className="text-purple-400" />} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12 items-stretch">
        {/* Insights Proativos (IA) */}
        <div className="bg-slate-800 p-6 rounded-xl border border-slate-700 shadow-xl flex flex-col h-full">
          <h2 className="text-xl font-bold mb-4 flex items-center gap-2 text-yellow-400">
            <AlertTriangle size={24} /> Insights Proativos 
          </h2>
          <div className="flex-1 flex flex-col justify-center">
            {insights.length > 0 ? (
              <ul className="space-y-4">
                {insights.map((insight, idx) => (
                  <li key={idx} className="bg-slate-700/50 p-4 rounded-lg flex items-start gap-3 border-l-4 border-yellow-400">
                     <span className="text-slate-200">{insight}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-slate-500 italic">Carregue um arquivo para gerar os insights automatizados.</p>
            )}
          </div>
        </div>

        {/* Evolução Temporal Chart (Requirement) */}
        <div className="bg-slate-800 p-6 rounded-xl border border-slate-700 shadow-xl flex flex-col h-full min-h-[380px]">
          <h2 className="text-xl font-bold mb-6 text-slate-100">Evolução Faturamento (Mensal)</h2>
          <div className="flex-1 w-full min-h-0">
            {metrics && metrics.evolucao_temporal ? (
              <ResponsiveContainer width="100%" height="100%">
        
              <BarChart data={metrics.evolucao_temporal} margin={{ top: 20, right: 30, left: 40, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                <XAxis dataKey="periodo" stroke="#94a3b8" tickMargin={10} axisLine={false} tickLine={false} />
                <YAxis 
                  stroke="#94a3b8" 
                  width={90} 
                  axisLine={false}
                  tickLine={false}
                  tickFormatter={(val) => `R$ ${(val / 1000).toFixed(0)} mil`} 
                />
                <Tooltip 
                  cursor={{fill: '#334155'}} 
                  contentStyle={{backgroundColor: '#1e293b', border: 'none', borderRadius: '8px', color: '#f8fafc', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'}}
                  formatter={(value: number) => [`R$ ${value.toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`, 'Receita']}
                  labelStyle={{ color: '#94a3b8', marginBottom: '4px', fontWeight: 'bold' }}
                />
                <Bar dataKey="receita" fill="#34d399" radius={[4, 4, 0, 0]} maxBarSize={45} />
              </BarChart>
            </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-slate-500 italic">
                 Nenhum dado temporal processado
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Chat Section RAG */}
      <div className="bg-slate-800 rounded-xl p-6 shadow-2xl border border-slate-700 max-w-5xl mx-auto">
        <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
          <MessageSquare size={24} className="text-blue-400" /> Analista de IA Interativo (RAG & Pandas)
        </h2>
        <p className="mb-6 text-sm text-slate-400">A IA escolhe automaticamente ler a Tabela (Pandas) ou o Vetor Textual (FAISS) dependendo da sua pergunta.</p>
        
        <div className="h-80 overflow-y-auto mb-6 space-y-4 pr-2 custom-scrollbar p-4 bg-slate-900/50 rounded-lg">
          {chat.length === 0 && <p className="text-slate-500 text-center mt-10">Ex: "Qual foi nossa maior transação?" ou "Quais itens são referentes à contratação da Empresa X?"</p>}
          {chat.map((item, i) => (
            <div key={i} className="space-y-4">
              <div className="bg-slate-700 p-4 rounded-xl w-fit max-w-[80%] text-slate-100 ml-auto shadow-md">
                <strong className="text-emerald-400 block text-xs mb-1">Você</strong> {item.q}
              </div>
              <div className="bg-slate-900 border border-slate-700 p-4 rounded-xl w-fit max-w-[80%] shadow-md">
                <strong className="text-blue-400 block text-xs mb-1">Assistente IA</strong> 
                <span className="text-slate-300 leading-relaxed whitespace-pre-wrap">
                  {item.a === "..." ? <span className="animate-pulse animate-infinite">Pensando...</span> : item.a}
                </span>
              </div>
            </div>
          ))}
        </div>

        <form onSubmit={handleAsk} className="flex gap-3">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Digite algo para pesquisar com RAG..."
            className="flex-1 bg-slate-900 border border-slate-600 focus:border-emerald-500 rounded-lg px-5 py-3 focus:outline-none transition shadow-inner"
          />
          <button 
            disabled={loading}
            className="bg-emerald-600 px-6 py-3 rounded-lg hover:bg-emerald-700 transition disabled:opacity-50 font-bold flex items-center gap-2"
          >
             {loading ? "Pensando..." : <><Send size={20} /> Perguntar</>}
          </button>
        </form>
      </div>
    </div>
  );
}

function Card({ title, value, icon }: any) {
  return (
    <div className="bg-slate-800 p-6 rounded-xl border border-slate-700 shadow-xl flex flex-col justify-between h-full">
      <div className="flex justify-between items-start mb-4">
        <span className="text-slate-400 font-medium text-sm">{title}</span>
        <div className="p-2 bg-slate-900 rounded-lg">{icon}</div>
      </div>
      <div className="text-3xl font-bold text-slate-100 mt-auto">{value}</div>
    </div>
  );
}