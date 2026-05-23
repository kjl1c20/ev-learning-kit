"use client";

import { useState } from "react";
import {
  askQuestion,
  AskResponse,
  generateCurve,
  GenerateCurveRequest,
  GenerateCurveResponse,
} from "@/lib/api";
import AnswerCard from "@/components/AnswerCard";
import ChatInput from "@/components/ChatInput";
import CurveChart from "@/components/CurveChart";
import CurveForm from "@/components/CurveForm";
import MetricsPanel from "@/components/MetricsPanel";
import ReasoningPanel from "@/components/ReasoningPanel";

export default function Home() {
  const [curve, setCurve] = useState<GenerateCurveResponse | null>(null);
  const [curveRequest, setCurveRequest] = useState<GenerateCurveRequest | null>(null);
  const [curveLoading, setCurveLoading] = useState(false);
  const [curveError, setCurveError] = useState<string | null>(null);

  const [answer, setAnswer] = useState<AskResponse | null>(null);
  const [answerLoading, setAnswerLoading] = useState(false);
  const [answerError, setAnswerError] = useState<string | null>(null);

  async function handleGenerate(request: GenerateCurveRequest) {
    setCurveLoading(true);
    setCurveError(null);
    try {
      setCurveRequest(request);
      setCurve(await generateCurve(request));
    } catch {
      setCurveError("Failed to generate curve. Make sure the API is running.");
    } finally {
      setCurveLoading(false);
    }
  }

  function handleExport() {
    if (!curve || !curveRequest) return;
    const payload = {
      generated_at: new Date().toISOString(),
      request: curveRequest,
      metrics: curve.metrics,
      native_curve: curve.native_curve,
      delivered_curve: curve.delivered_curve,
    };
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `ev_curve_${curveRequest.vehicle_class}_${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }

  async function handleAsk(query: string) {
    setAnswerLoading(true);
    setAnswerError(null);
    try {
      setAnswer(await askQuestion(query));
    } catch {
      setAnswerError("Failed to get answer.");
    } finally {
      setAnswerLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-gray-50 px-4 py-10">
      <div className="mx-auto max-w-4xl space-y-8">
        <header>
          <h1 className="text-3xl font-bold text-gray-900">⚡ EV Charge Curve Generator</h1>
          <p className="mt-2 text-gray-500">
            Generate a charging profile for any vehicle class and explore why the curve looks the way it does.
          </p>
        </header>

        <section>
          <CurveForm onSubmit={handleGenerate} loading={curveLoading} />
        </section>

        {curveError && <p className="text-sm text-red-500">{curveError}</p>}

        {curveLoading && (
          <p className="text-center text-sm text-gray-400">Generating curve...</p>
        )}

        {curve && !curveLoading && (
          <section className="space-y-4">
            <CurveChart nativeCurve={curve.native_curve} deliveredCurve={curve.delivered_curve} onExport={handleExport} />
            <MetricsPanel metrics={curve.metrics} />
            <ReasoningPanel parameters={curve.parameters} />
          </section>
        )}

        <section className="space-y-3 border-t border-gray-200 pt-8">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Learn more</h2>
            <p className="text-sm text-gray-500">
              Have a question about charging behavior, chemistry, or BMS? Ask away.
            </p>
          </div>
          <ChatInput onSubmit={handleAsk} loading={answerLoading} />

          {answerError && <p className="text-sm text-red-500">{answerError}</p>}
          {answerLoading && (
            <p className="text-center text-sm text-gray-400">Searching knowledge base...</p>
          )}
          {answer && !answerLoading && <AnswerCard result={answer} />}
        </section>
      </div>
    </main>
  );
}
