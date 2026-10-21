export type CheckStatus = 'pass' | 'warn' | 'fail';

export type CheckResult = {
  id: string;
  label: string;
  status: CheckStatus;
  message: string;
  value?: string | null;
};

export type AuditReport = {
  url: string;
  status_code: number;
  site_checks: CheckResult[];
  page_checks: CheckResult[];
};
