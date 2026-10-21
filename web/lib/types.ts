export type CheckStatus = 'pass' | 'warn' | 'fail';

export type CheckResult = {
  id: string;
  label: string;
  status: CheckStatus;
  message: string;
  value?: string | null;
};

export type PageAudit = {
  url: string;
  status_code: number;
  checks: CheckResult[];
};
