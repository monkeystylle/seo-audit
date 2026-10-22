import type { CheckStatus, SpeedReport } from '@/lib/types';
import { CheckCard, statusStyles } from './check-list';

function scoreStatus(score: number): CheckStatus {
  if (score >= 90) return 'pass';
  if (score >= 50) return 'warn';
  return 'fail';
}

export function SpeedResult({ report }: { report: SpeedReport }) {
  const status = scoreStatus(report.score);

  return (
    <section className="mt-8">
      <h2 className="text-lg font-semibold">Speed ({report.strategy})</h2>

      <div className="mt-3 flex items-center gap-4 rounded-md border p-4">
        <span
          className={`flex size-16 shrink-0 items-center justify-center rounded-full text-2xl font-semibold tabular-nums ${statusStyles[status]}`}
        >
          {report.score}
        </span>
        <p className="text-sm text-gray-600">
          Google&apos;s performance score out of 100, tested on a simulated
          mid-range phone. 90 and above is good, below 50 is poor.
        </p>
      </div>

      <ul className="mt-3 space-y-3">
        {report.checks.map(check => (
          <CheckCard key={check.id} check={check} />
        ))}
      </ul>
    </section>
  );
}

export function SpeedError({ url, message }: { url: string; message: string }) {
  const pagespeedLink = `https://pagespeed.web.dev/analysis?url=${encodeURIComponent(url)}`;

  return (
    <section className="mt-8">
      <h2 className="text-lg font-semibold">Speed</h2>
      <div className="mt-3 rounded-md border p-4 text-sm">
        <p>Google couldn&apos;t finish the speed test: {message}</p>
        <p className="mt-2">
          You can run it on Google&apos;s site instead:{' '}
          <a
            href={pagespeedLink}
            target="_blank"
            rel="noreferrer"
            className="underline"
          >
            open PageSpeed Insights
          </a>
        </p>
      </div>
    </section>
  );
}
