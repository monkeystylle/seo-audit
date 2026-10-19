'use client';

import { useEffect, useState } from 'react';

type Status = 'checking' | 'connected' | 'error';

export default function Home() {
  const [status, setStatus] = useState<Status>('checking');

  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/health`)
      .then(res => res.json())
      .then(data => setStatus(data.ok ? 'connected' : 'error'))
      .catch(() => setStatus('error'));
  }, []);

  return (
    <main className="flex min-h-screen items-center justify-center">
      <p className="text-lg">
        {status === 'checking' && 'Checking API…'}
        {status === 'connected' && 'API connected'}
        {status === 'error' &&
          'API not reachable. Is uvicorn running on port 8000?'}
      </p>
    </main>
  );
}
