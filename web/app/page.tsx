'use client';

import { useState, type FormEvent } from 'react';
import type { CheckStatus, PageAudit } from '@/lib/types';

const statusStyles: Record<CheckStatus, string> = {
  pass: 'bg-green-100 text-green-800',
  warn: 'bg-amber-100 text-amber-800',
  fail: 'bg-red-100 text-red-800',
};

export default function Home() {
  const [url, setUrl] = useState('');
  const [audit, setAudit] = useState<PageAudit | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setAudit(null);

    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/audit/page?url=${encodeURIComponent(url)}`,
      );
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail ?? 'Audit failed');
      setAudit(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Audit failed');
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="mx-auto max-w-2xl px-4 py-16">
      <h1 className="text-2xl font-semibold">SEO Audit</h1>

      <form onSubmit={handleSubmit} className="mt-6 flex gap-2">
        <input
          type="text"
          value={url}
          onChange={e => setUrl(e.target.value)}
          placeholder="example.com"
          required
          className="flex-1 rounded-md border px-3 py-2"
        />
        <button
          type="submit"
          disabled={loading}
          className="rounded-md bg-black px-4 py-2 text-white disabled:opacity-50"
        >
          {loading ? 'Checking…' : 'Audit'}
        </button>
      </form>

      {error && <p className="mt-4 text-red-600">{error}</p>}

      {audit && (
        <section className="mt-8">
          <p className="text-sm text-gray-500">
            {audit.url} · HTTP {audit.status_code}
          </p>
          <ul className="mt-4 space-y-3">
            {audit.checks.map(check => (
              <li key={check.id} className="rounded-md border p-4">
                <div className="flex items-center justify-between">
                  <span className="font-medium">{check.label}</span>
                  <span
                    className={`rounded-full px-2 py-0.5 text-xs font-medium ${statusStyles[check.status]}`}
                  >
                    {check.status}
                  </span>
                </div>
                <p className="mt-1 text-sm">{check.message}</p>
                {check.value && (
                  <p className="mt-2 text-sm text-gray-500">“{check.value}”</p>
                )}
              </li>
            ))}
          </ul>
        </section>
      )}
    </main>
  );
}
