import { useState, type ReactNode } from 'react';
import { motion } from 'motion/react';
import {
  AlertCircle,
  Copy,
  Download,
  Image as ImageIcon,
  Instagram,
  Linkedin,
  Loader2,
  Send,
  Sparkles,
  Twitter,
} from 'lucide-react';
import { generatePlatformImage, generateSocialContent, SocialDrafts } from '../services/gemini';

type Tone = 'professional' | 'witty' | 'urgent';
type ImageSize = '1K' | '2K' | '4K';

interface PlatformResult {
  text: string;
  imageUrl: string | null;
  loading: boolean;
  error: string | null;
}

interface Props {
  onContinue: () => void;
}

export default function SocialGenScreen({ onContinue }: Props) {
  const [idea, setIdea] = useState('');
  const [tone, setTone] = useState<Tone>('professional');
  const [imageSize, setImageSize] = useState<ImageSize>('1K');
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState('');
  const [results, setResults] = useState<Record<keyof SocialDrafts, PlatformResult> | null>(null);

  const updatePlatform = (platform: keyof SocialDrafts, updates: Partial<PlatformResult>) => {
    setResults((prev) => {
      if (!prev) return prev;
      return { ...prev, [platform]: { ...prev[platform], ...updates } };
    });
  };

  const handleGenerate = async () => {
    if (!idea.trim()) return;
    setError('');
    setIsGenerating(true);
    setResults({
      linkedin: { text: '', imageUrl: null, loading: true, error: null },
      twitter: { text: '', imageUrl: null, loading: true, error: null },
      instagram: { text: '', imageUrl: null, loading: true, error: null },
    });

    try {
      const drafts = await generateSocialContent(idea, tone);
      setResults({
        linkedin: { text: drafts.linkedin.text, imageUrl: null, loading: true, error: null },
        twitter: { text: drafts.twitter.text, imageUrl: null, loading: true, error: null },
        instagram: { text: drafts.instagram.text, imageUrl: null, loading: true, error: null },
      });

      await Promise.all([
        generatePlatformImage(drafts.linkedin.imagePrompt, '4:3', imageSize)
          .then((url) => updatePlatform('linkedin', { imageUrl: url, loading: false }))
          .catch(() => updatePlatform('linkedin', { loading: false, error: 'Falha ao gerar imagem.' })),
        generatePlatformImage(drafts.twitter.imagePrompt, '16:9', imageSize)
          .then((url) => updatePlatform('twitter', { imageUrl: url, loading: false }))
          .catch(() => updatePlatform('twitter', { loading: false, error: 'Falha ao gerar imagem.' })),
        generatePlatformImage(drafts.instagram.imagePrompt, '1:1', imageSize)
          .then((url) => updatePlatform('instagram', { imageUrl: url, loading: false }))
          .catch(() => updatePlatform('instagram', { loading: false, error: 'Falha ao gerar imagem.' })),
      ]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Falha ao gerar conteudo.');
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100">
      <header className="border-b border-zinc-800 sticky top-0 bg-zinc-950/90 backdrop-blur">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-indigo-400" />
            <h1 className="font-bold">SocialGen AI</h1>
          </div>
          <button onClick={onContinue} className="rounded-lg bg-white text-zinc-900 px-4 py-2 text-sm font-bold">
            Ir para dashboard
          </button>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-8 grid lg:grid-cols-[360px_1fr] gap-8">
        <section className="space-y-4">
          <label className="text-sm font-semibold text-zinc-400 flex items-center gap-2"><ImageIcon size={16} /> Sua ideia</label>
          <textarea
            className="w-full h-36 rounded-xl bg-zinc-900 border border-zinc-800 p-3"
            placeholder="Ex: lancamento de um novo produto de IA..."
            value={idea}
            onChange={(e) => setIdea(e.target.value)}
          />
          <div className="grid grid-cols-3 gap-2">
            {(['professional', 'witty', 'urgent'] as Tone[]).map((t) => (
              <button
                key={t}
                onClick={() => setTone(t)}
                className={`py-2 rounded-lg text-sm border ${tone === t ? 'bg-indigo-600 border-indigo-500' : 'bg-zinc-900 border-zinc-800'}`}
              >
                {t}
              </button>
            ))}
          </div>
          <div className="grid grid-cols-3 gap-2">
            {(['1K', '2K', '4K'] as ImageSize[]).map((s) => (
              <button
                key={s}
                onClick={() => setImageSize(s)}
                className={`py-2 rounded-lg text-xs border ${imageSize === s ? 'bg-white text-zinc-900 border-white' : 'bg-zinc-900 border-zinc-800 text-zinc-300'}`}
              >
                {s}
              </button>
            ))}
          </div>
          {error ? <div className="rounded-lg bg-red-500/10 border border-red-500/30 p-3 text-sm text-red-300">{error}</div> : null}
          <button
            onClick={handleGenerate}
            disabled={isGenerating || !idea.trim()}
            className="w-full rounded-xl bg-indigo-600 py-3 font-bold disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {isGenerating ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
            {isGenerating ? 'Gerando...' : 'Gerar conteudo'}
          </button>
        </section>

        <section className="space-y-4">
          {!results ? (
            <div className="h-80 rounded-2xl border-2 border-dashed border-zinc-800 flex items-center justify-center text-zinc-500">
              Gere um conteudo para ver LinkedIn, Twitter/X e Instagram.
            </div>
          ) : (
            <>
              <PlatformCard icon={<Linkedin className="w-4 h-4 text-blue-400" />} title="LinkedIn" result={results.linkedin} />
              <PlatformCard icon={<Twitter className="w-4 h-4 text-sky-300" />} title="Twitter / X" result={results.twitter} />
              <PlatformCard icon={<Instagram className="w-4 h-4 text-pink-400" />} title="Instagram" result={results.instagram} />
            </>
          )}
        </section>
      </main>
    </div>
  );
}

function PlatformCard({ icon, title, result }: { icon: ReactNode; title: string; result: PlatformResult }) {
  return (
    <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="rounded-2xl border border-zinc-800 bg-zinc-900 p-4">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          {icon}
          <h3 className="font-semibold">{title}</h3>
        </div>
        <button
          onClick={() => navigator.clipboard.writeText(result.text || '')}
          className="rounded-lg p-2 hover:bg-zinc-800"
          title="Copiar texto"
        >
          <Copy className="w-4 h-4" />
        </button>
      </div>
      <p className="text-sm text-zinc-200 whitespace-pre-wrap min-h-16">{result.text || 'Gerando texto...'}</p>
      <div className="mt-3 rounded-xl border border-zinc-800 bg-zinc-950 overflow-hidden min-h-40 flex items-center justify-center">
        {result.imageUrl ? (
          <div className="w-full relative">
            <img src={result.imageUrl} alt={`${title} visual`} className="w-full object-cover" />
            <a
              className="absolute right-3 bottom-3 rounded-lg p-2 bg-zinc-900/80"
              href={result.imageUrl}
              download={`${title.toLowerCase()}-image.png`}
            >
              <Download className="w-4 h-4" />
            </a>
          </div>
        ) : result.error ? (
          <div className="text-xs text-red-300 flex items-center gap-2"><AlertCircle className="w-4 h-4" /> {result.error}</div>
        ) : (
          <Loader2 className="w-5 h-5 animate-spin text-zinc-400" />
        )}
      </div>
    </motion.div>
  );
}
