'use client';

import { useState, type FormEvent } from 'react';
import type {
  AuditReport,
  CheckResult,
  CheckStatus,
  CrawlReport,
} from '@/lib/types';

const API_URL = process.env.NEXT_PUBLIC_API_URL;

const statusStyles: Record<CheckStatus, string> = {
  pass: 'bg-green-100 text-green-800',
  warn: 'bg-amber-100 text-amber-800',
  fail: 'bg-red-100 text-red-800',
};

async function getJson<T>(path: string): Promise<T> {
  const res = await fetch(`${API_URL}${path}`);
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail ?? 'Request failed');
  return data;
}

function CheckList({
  title,
  checks,
}: {
  title: string;
  checks: CheckResult[];
}) {
  return (
    <section className="mt-8">
      <h2 className="text-lg font-semibold">{title}</h2>
      <ul className="mt-3 space-y-3">
        {checks.map(check => (
          <li key={check.id} className="rounded-md border p-4">
            <div className="flex items-center justify-between gap-4">
              <span className="font-medium">{check.label}</span>
              <span
                className={`rounded-full px-2 py-0.5 text-xs font-medium ${statusStyles[check.status]}`}
              >
                {check.status}
              </span>
            </div>
            <p className="mt-1 text-sm">{check.message}</p>
            {check.value && (
              <p className="mt-2 break-words text-sm text-gray-500">
                “{check.value}”
              </p>
            )}
            {check.details.length > 0 && (
              <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-gray-600">
                {check.details.map(detail => (
                  <li key={detail} className="break-words">
                    {detail}
                  </li>
                ))}
              </ul>
            )}
          </li>
        ))}
      </ul>
    </section>
  );
}

export default function Home() {
  const [url, setUrl] = useState('');
  const [audit, setAudit] = useState<AuditReport | null>(null);
  const [crawl, setCrawl] = useState<CrawlReport | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [crawlError, setCrawlError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [crawling, setCrawling] = useState(false);

  async function runAudit(target: string) {
    setLoading(true);
    try {
      setAudit(await getJson<AuditReport>(`/audit?url=${target}`));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Audit failed');
    } finally {
      setLoading(false);
    }
  }

  async function runCrawl(target: string) {
    setCrawling(true);
    try {
      setCrawl(await getJson<CrawlReport>(`/crawl?url=${target}`));
    } catch (err) {
      setCrawlError(err instanceof Error ? err.message : 'Crawl failed');
    } finally {
      setCrawling(false);
    }
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setCrawlError(null);
    setAudit(null);
    setCrawl(null);

    const target = encodeURIComponent(url);
    runAudit(target);
    runCrawl(target);
  }

  const busy = loading || crawling;

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
          disabled={busy}
          className="rounded-md bg-black px-4 py-2 text-white disabled:opacity-50"
        >
          {busy ? 'Checking…' : 'Audit'}
        </button>
      </form>

      {error && <p className="mt-4 text-red-600">{error}</p>}

      {audit && (
        <>
          <p className="mt-8 text-sm text-gray-500">
            {audit.url} · HTTP {audit.status_code}
          </p>
          <CheckList title="Site" checks={audit.site_checks} />
          <CheckList title="Page" checks={audit.page_checks} />
        </>
      )}

      {crawling && (
        <p className="mt-8 text-sm text-gray-500">
          Crawling the whole site. This can take up to a minute…
        </p>
      )}

      {crawlError && <p className="mt-8 text-red-600">{crawlError}</p>}

      {crawl && (
        <CheckList
          title={`All pages (${crawl.pages_crawled} crawled)`}
          checks={crawl.checks}
        />
      )}
    </main>
  );
}
