import type { CheckStatus, CrawledPage } from '@/lib/types';
import { CheckCard, statusStyles } from './check-list';

function countStatus(page: CrawledPage, status: CheckStatus) {
  return page.checks.filter(check => check.status === status).length;
}

function isBroken(page: CrawledPage) {
  return page.status_code === 0 || page.status_code >= 400;
}

function sortByIssues(pages: CrawledPage[]) {
  return [...pages].sort((a, b) => {
    if (isBroken(a) !== isBroken(b)) return isBroken(a) ? -1 : 1;
    const fails = countStatus(b, 'fail') - countStatus(a, 'fail');
    if (fails !== 0) return fails;
    return countStatus(b, 'warn') - countStatus(a, 'warn');
  });
}

function pathOf(url: string) {
  const { pathname, search } = new URL(url);
  return pathname + search;
}

function PageRow({ page }: { page: CrawledPage }) {
  const fails = countStatus(page, 'fail');
  const warns = countStatus(page, 'warn');

  return (
    <details className="rounded-md border">
      <summary className="flex cursor-pointer items-center justify-between gap-4 p-4">
        <span className="min-w-0 truncate font-medium" title={page.url}>
          {pathOf(page.url)}
        </span>
        <span className="flex shrink-0 gap-2 text-xs font-medium">
          {isBroken(page) ? (
            <span className={`rounded-full px-2 py-0.5 ${statusStyles.fail}`}>
              {page.status_code || 'no response'}
            </span>
          ) : (
            <>
              {fails > 0 && (
                <span
                  className={`rounded-full px-2 py-0.5 ${statusStyles.fail}`}
                >
                  {fails} fail
                </span>
              )}
              {warns > 0 && (
                <span
                  className={`rounded-full px-2 py-0.5 ${statusStyles.warn}`}
                >
                  {warns} warn
                </span>
              )}
              {fails === 0 && warns === 0 && (
                <span
                  className={`rounded-full px-2 py-0.5 ${statusStyles.pass}`}
                >
                  all pass
                </span>
              )}
            </>
          )}
        </span>
      </summary>

      <div className="border-t p-4">
        {isBroken(page) ? (
          <p className="text-sm">
            This page didn&apos;t load. It&apos;s linked from {page.found_on}.
          </p>
        ) : (
          <ul className="space-y-3">
            {page.checks.map(check => (
              <CheckCard key={check.id} check={check} />
            ))}
          </ul>
        )}
      </div>
    </details>
  );
}

export function PageList({ pages }: { pages: CrawledPage[] }) {
  return (
    <section className="mt-8">
      <h2 className="text-lg font-semibold">Page by page</h2>
      <p className="mt-1 text-sm text-gray-500">
        Pages with the most problems are listed first. Click a page to see its
        checks.
      </p>
      <div className="mt-3 space-y-2">
        {sortByIssues(pages).map(page => (
          <PageRow key={page.url} page={page} />
        ))}
      </div>
    </section>
  );
}
