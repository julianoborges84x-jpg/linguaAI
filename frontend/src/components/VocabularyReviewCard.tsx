import { PedagogyDashboardData } from '../types';

interface Props {
  data: PedagogyDashboardData;
  onReview: () => void;
}

export default function VocabularyReviewCard({ data, onReview }: Props) {
  return (
    <section className="rounded-xl border border-amber-200 bg-amber-50 p-4">
      <p className="text-xs font-semibold uppercase tracking-wider text-amber-700">Vocabulario em revisao</p>
      <p className="mt-1 text-2xl font-black text-amber-900">{data.words_in_review}</p>
      <p className="text-xs text-amber-700">Palavras para revisar com repeticao espacada.</p>
      <button type="button" onClick={onReview} className="mt-3 w-full rounded-lg border border-amber-300 bg-white px-3 py-2 text-sm font-bold text-amber-700">
        Revisar agora
      </button>
    </section>
  );
}
