'use client';

import { useEffect, useState, type FormEvent } from 'react';
import { CheckList } from '@/components/check-list';
import { PageList } from '@/components/page-list';
import { SpeedError, SpeedResult } from '@/components/speed-report';
import type { AuditReport, CrawlReport, SpeedReport } from '@/lib/types';

const API_URL = process.env.NEXT_PUBLIC_API_URL;

async function getJson<T>(path: string): Promise<T> {
  const res = await fetch(`${API_URL}${path}`);
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail ?? 'Request failed');
  return data;
}

export default function Home() {
  const [url, setUrl] = useState('');
  const [submittedUrl, setSubmittedUrl] = useState('');

  const [audit, setAudit] = useState<AuditReport | null>(null);
  const [crawl, setCrawl] = useState<CrawlReport | null>(null);
  const [speed, setSpeed] = useState<SpeedReport | null>(null);

  const [error, setError] = useState<string | null>(null);
  const [crawlError, setCrawlError] = useState<string | null>(null);
  const [speedError, setSpeedError] = useState<string | null>(null);

  const [loading, setLoading] = useState(false);
  const [crawling, setCrawling] = useState(false);
  const [testingSpeed, setTestingSpeed] = useState(false);

  const [seconds, setSeconds] = useState(0);
  const busy = loading || crawling || testingSpeed;

  useEffect(() => {
    if (!busy) return;
    const timer = setInterval(() => setSeconds(s => s + 1), 1000);
    return () => clearInterval(timer);
  }, [busy]);

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

  async function runSpeed(target: string) {
    setTestingSpeed(true);
    try {
      setSpeed(await getJson<SpeedReport>(`/speed?url=${target}`));
    } catch (err) {
      setSpeedError(err instanceof Error ? err.message : 'Speed test failed');
    } finally {
      setTestingSpeed(false);
    }
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setAudit(null);
    setCrawl(null);
    setSpeed(null);
    setError(null);
    setCrawlError(null);
    setSpeedError(null);
    setSeconds(0);
    setSubmittedUrl(url.startsWith('http') ? url : `https://${url}`);

    const target = encodeURIComponent(url);
    runAudit(target);
    runCrawl(target);
    runSpeed(target);
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
          <CheckList title="This page" checks={audit.page_checks} />
        </>
      )}

      {testingSpeed && (
        <p className="mt-8 text-sm text-gray-500">
          Testing page speed with Google… {seconds}s. Slow sites can take a few
          minutes.
        </p>
      )}
      {speedError && <SpeedError url={submittedUrl} message={speedError} />}
      {speed && <SpeedResult report={speed} />}

      {crawling && (
        <p className="mt-8 text-sm text-gray-500">
          Crawling the whole site… {seconds}s. Larger sites can take up to a
          minute.
        </p>
      )}
      {crawlError && <p className="mt-8 text-red-600">{crawlError}</p>}
      {crawl && (
        <>
          <CheckList
            title={`All pages (${crawl.pages_crawled} crawled)`}
            checks={crawl.checks}
          />
          <PageList pages={crawl.pages} />
        </>
      )}
    </main>
  );
}
