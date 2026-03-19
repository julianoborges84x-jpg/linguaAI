import { useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';

import { trackPublicGrowthEvent } from '../api/auth';

const REFERRAL_STORAGE_KEY = 'lingua_referral_code';

export default function InviteRedirectScreen() {
  const { code } = useParams<{ code: string }>();
  const navigate = useNavigate();

  useEffect(() => {
    if (code && code.trim()) {
      localStorage.setItem(REFERRAL_STORAGE_KEY, code.trim().toLowerCase());
      Promise.resolve(trackPublicGrowthEvent('referral_link_opened', { referral_code: code.trim().toLowerCase() })).catch(() => {
        // keep redirect flow resilient
      });
    }
    navigate('/login', { replace: true });
  }, [code, navigate]);

  return (
    <div className="min-h-screen bg-background-light flex items-center justify-center">
      <div className="rounded-xl border border-slate-200 bg-white px-5 py-4 text-sm text-slate-600">
        Preparando seu convite...
      </div>
    </div>
  );
}
