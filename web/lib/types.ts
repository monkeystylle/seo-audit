export type CheckStatus = 'pass' | 'warn' | 'fail';

export type CheckResult = {
  id: string;
  label: string;
  status: CheckStatus;
  message: string;
  value?: string | null;
  details: string[];
};

export type AuditReport = {
  url: string;
  status_code: number;
  site_checks: CheckResult[];
  page_checks: CheckResult[];
};

export type CrawledPage = {
  url: string;
  status_code: number;
  found_on: string | null;
  title: string | null;
  meta_description: string | null;
  h1_count: number;
  checks: CheckResult[];
};

export type CrawlReport = {
  start_url: string;
  pages_crawled: number;
  checks: CheckResult[];
  pages: CrawledPage[];
};

export type SpeedReport = {
  url: string;
  strategy: 'mobile' | 'desktop';
  score: number;
  checks: CheckResult[];
};
