import type { CheckResult, CheckStatus } from '@/lib/types';

export const statusStyles: Record<CheckStatus, string> = {
  pass: 'bg-green-100 text-green-800',
  warn: 'bg-amber-100 text-amber-800',
  fail: 'bg-red-100 text-red-800',
};

export function CheckCard({ check }: { check: CheckResult }) {
  return (
    <li className="rounded-md border p-4">
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
  );
}

export function CheckList({
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
          <CheckCard key={check.id} check={check} />
        ))}
      </ul>
    </section>
  );
}
