import { ArrowLeft, Mic, MicOff, Play, Square, Users } from 'lucide-react';
import { useEffect, useMemo, useRef, useState } from 'react';

import { fetchVoiceMentors, fetchVoiceUsage, sendChatMessage, sendVoiceMentorMessage, trackGrowthEvent } from '../api/auth';
import { AuthUser, VoiceMentor, VoiceUsage } from '../types';
import MentorAvatarCard from './MentorAvatarCard';
import VoiceConversationPanel from './VoiceConversationPanel';
import VoiceMentorPicker from './VoiceMentorPicker';

type VoiceState = 'idle' | 'listening' | 'thinking' | 'speaking';
const VOICE_FREE_LIMIT_MESSAGE = '🔒 Você atingiu o limite gratuito. Desbloqueie o PRO para continuar falando com seu mentor.';

interface Props {
  user: AuthUser;
  onBack: () => void;
  onUpgrade: () => Promise<void> | void;
}

interface VoiceLine {
  role: 'user' | 'mentor';
  text: string;
}

type SpeechRecognitionCtor = new () => {
  lang: string;
  continuous: boolean;
  interimResults: boolean;
  onstart: (() => void) | null;
  onresult: ((event: { results: ArrayLike<ArrayLike<{ transcript: string }>> }) => void) | null;
  onerror: ((event?: { error?: string }) => void) | null;
  onend: (() => void) | null;
  start: () => void;
  stop: () => void;
};

type MentorVoiceProfile = {
  gender: 'female' | 'male';
  rate: number;
  pitch: number;
};

const MENTOR_VOICE_PROFILE: Record<string, MentorVoiceProfile> = {
  clara: { gender: 'female', rate: 0.97, pitch: 1.2 },
  maya: { gender: 'female', rate: 1.0, pitch: 1.15 },
  noah: { gender: 'male', rate: 0.94, pitch: 0.92 },
  ethan: { gender: 'male', rate: 0.95, pitch: 0.9 },
};

function voiceSettings(mentorId: string): { rate: number; pitch: number } {
  const profile = MENTOR_VOICE_PROFILE[mentorId];
  if (profile) return { rate: profile.rate, pitch: profile.pitch };
  return { rate: 0.95, pitch: 1.0 };
}

const FEMALE_HINTS = ['female', 'samantha', 'victoria', 'ava', 'allison', 'zira', 'joanna', 'jenny', 'aria'];
const MALE_HINTS = ['male', 'david', 'daniel', 'alex', 'fred', 'matthew', 'guy', 'ryan', 'andrew'];

export function selectMentorVoice(mentorId: string, voices: SpeechSynthesisVoice[]): SpeechSynthesisVoice | null {
  if (!voices.length) return null;
  const profile = MENTOR_VOICE_PROFILE[mentorId] || { gender: 'male' as const, rate: 0.95, pitch: 1.0 };
  const genderHints = profile.gender === 'female' ? FEMALE_HINTS : MALE_HINTS;

  const enUs = voices.filter((voice) => voice.lang?.toLowerCase().startsWith('en-us'));
  const pool = enUs.length > 0 ? enUs : voices.filter((voice) => voice.lang?.toLowerCase().startsWith('en'));
  const preferredPool = pool.length > 0 ? pool : voices;

  const byGenderHint = preferredPool.find((voice) => {
    const name = `${voice.name} ${voice.voiceURI}`.toLowerCase();
    return genderHints.some((hint) => {
      const escaped = hint.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      return new RegExp(`\\b${escaped}\\b`, 'i').test(name);
    });
  });
  if (byGenderHint) return byGenderHint;

  const byNatural = preferredPool.find((voice) => {
    const name = `${voice.name} ${voice.voiceURI}`.toLowerCase();
    return name.includes('natural') || name.includes('neural') || name.includes('enhanced');
  });
  if (byNatural) return byNatural;

  return preferredPool[0] || null;
}

export default function LiveTutorScreen({ user, onBack, onUpgrade }: Props) {
  const [mentors, setMentors] = useState<VoiceMentor[]>([]);
  const [selectedMentorId, setSelectedMentorId] = useState('');
  const [voiceState, setVoiceState] = useState<VoiceState>('idle');
  const [conversation, setConversation] = useState<VoiceLine[]>([]);
  const [transcript, setTranscript] = useState('');
  const [input, setInput] = useState('');
  const [muted, setMuted] = useState(false);
  const [sessionActive, setSessionActive] = useState(false);
  const [error, setError] = useState('');
  const [audioAvailable, setAudioAvailable] = useState(true);
  const [recognitionAvailable, setRecognitionAvailable] = useState(true);
  const [voiceUsage, setVoiceUsage] = useState<VoiceUsage | null>(null);
  const [introDone, setIntroDone] = useState(false);
  const [availableVoices, setAvailableVoices] = useState<SpeechSynthesisVoice[]>([]);
  const speechRef = useRef<SpeechSynthesisUtterance | null>(null);
  const recognitionRef = useRef<InstanceType<SpeechRecognitionCtor> | null>(null);

  const selectedMentor = useMemo(
    () => mentors.find((item) => item.id === selectedMentorId) || null,
    [mentors, selectedMentorId],
  );

  useEffect(() => {
    void Promise.resolve(trackGrowthEvent('voice_mentor_opened')).catch(() => undefined);
    const canSpeak = typeof window !== 'undefined' && typeof window.speechSynthesis !== 'undefined';
    setAudioAvailable(canSpeak);
    if (canSpeak && window.speechSynthesis) {
      const loadVoices = () => setAvailableVoices(window.speechSynthesis.getVoices());
      loadVoices();
      window.speechSynthesis.onvoiceschanged = loadVoices;
    }

    const ctor = (window as unknown as { SpeechRecognition?: SpeechRecognitionCtor; webkitSpeechRecognition?: SpeechRecognitionCtor }).SpeechRecognition
      || (window as unknown as { SpeechRecognition?: SpeechRecognitionCtor; webkitSpeechRecognition?: SpeechRecognitionCtor }).webkitSpeechRecognition;
    if (!ctor) {
      setRecognitionAvailable(false);
      return;
    }
    setRecognitionAvailable(true);
    recognitionRef.current = new ctor();
    recognitionRef.current.lang = 'en-US';
    recognitionRef.current.continuous = false;
    recognitionRef.current.interimResults = false;
    recognitionRef.current.onstart = () => setVoiceState('listening');
    recognitionRef.current.onerror = (event) => {
      const permissionDenied = event?.error === 'not-allowed' || event?.error === 'service-not-allowed';
      setError(permissionDenied ? 'Permissao de microfone negada. Ative o microfone no navegador.' : 'Falha ao usar microfone.');
      setVoiceState('idle');
    };
    recognitionRef.current.onend = () => {
      setVoiceState((prev) => (prev === 'listening' ? 'idle' : prev));
    };
    recognitionRef.current.onresult = async (event) => {
      const text = event.results[0]?.[0]?.transcript?.trim() || '';
      if (!text) return;
      setTranscript(text);
      await submitMessage(text);
    };

    return () => {
      if (canSpeak && typeof window !== 'undefined' && window.speechSynthesis) {
        window.speechSynthesis.onvoiceschanged = null;
      }
    };
  }, []);

  useEffect(() => {
    const load = async () => {
      try {
        const [data, usage] = await Promise.all([fetchVoiceMentors(), fetchVoiceUsage()]);
        setMentors(data);
        setVoiceUsage(usage);
        if (data.length > 0) {
          setSelectedMentorId(data[0].id);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Falha ao carregar mentores de voz.');
      }
    };
    void load();
  }, []);

  const isVoiceBlocked = Boolean(voiceUsage?.blocked);

  const speakText = async (text: string) => {
    if (!audioAvailable || muted) return;
    if (typeof window === 'undefined' || !window.speechSynthesis || typeof SpeechSynthesisUtterance === 'undefined') return;

    setVoiceState('speaking');
    const utterance = new SpeechSynthesisUtterance(text);
    const cfg = voiceSettings(selectedMentorId);
    const selectedVoice = selectMentorVoice(selectedMentorId, availableVoices);
    utterance.lang = 'en-US';
    utterance.rate = cfg.rate;
    utterance.pitch = cfg.pitch;
    if (selectedVoice) {
      utterance.voice = selectedVoice;
    }
    utterance.onend = () => setVoiceState('idle');
    speechRef.current = utterance;
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(utterance);
  };

  const startSession = async () => {
    setSessionActive(true);
    setVoiceState('idle');
    setError('');
    await trackGrowthEvent('voice_session_started', { mentor_id: selectedMentorId });

    if (!introDone && selectedMentor) {
      const intro = `Hi! I am ${selectedMentor.name}, your live mentor. Tell me what you want to practice today.`;
      setConversation((prev) => [...prev, { role: 'mentor', text: intro }]);
      await speakText(intro);
      setIntroDone(true);
    }
  };

  const endSession = async () => {
    if (recognitionRef.current) recognitionRef.current.stop();
    if (speechRef.current && typeof window !== 'undefined' && window.speechSynthesis) {
      window.speechSynthesis.cancel();
    }
    setSessionActive(false);
    setVoiceState('idle');
    await trackGrowthEvent('voice_session_completed', { mentor_id: selectedMentorId, turns: conversation.length });
  };

  const submitMessage = async (text: string) => {
    if (!sessionActive || !selectedMentorId || !text.trim() || isVoiceBlocked) return;
    setError('');
    setVoiceState('thinking');
    const clean = text.trim();
    setConversation((prev) => [...prev, { role: 'user', text: clean }]);

    try {
      const response = await sendVoiceMentorMessage(selectedMentorId, clean);
      setTranscript(response.transcript);
      setVoiceUsage(response.voice_usage);
      setConversation((prev) => [...prev, { role: 'mentor', text: response.reply }]);
      setInput('');
      if (response.audio_available) {
        await speakText(response.tts_text || response.reply);
      } else {
        setVoiceState('idle');
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Falha ao conversar com mentor por voz.';
      if (message === VOICE_FREE_LIMIT_MESSAGE) {
        setVoiceUsage((prev) => {
          const limit = prev?.limit ?? 6;
          return { plan: 'FREE', used: limit, limit, remaining: 0, blocked: true };
        });
        setError(message);
        setVoiceState('idle');
        return;
      }

      try {
        const fallback = await sendChatMessage(clean);
        setConversation((prev) => [...prev, { role: 'mentor', text: fallback.reply }]);
        setError('Voz indisponivel agora. Respondi em texto para voce continuar.');
      } catch {
        setError(message);
      } finally {
        setVoiceState('idle');
      }
    }
  };

  const replayLast = async () => {
    const last = [...conversation].reverse().find((item) => item.role === 'mentor');
    if (!last) return;
    await trackGrowthEvent('voice_reply_replayed', { mentor_id: selectedMentorId });
    await speakText(last.text);
  };

  const startListening = () => {
    if (!sessionActive || !recognitionRef.current) return;
    setError('');
    recognitionRef.current.start();
  };

  const handleMentorChange = async (mentorId: string) => {
    setSelectedMentorId(mentorId);
    setIntroDone(false);
    await trackGrowthEvent('voice_mentor_selected', { mentor_id: mentorId });
  };

  const handleCycleMentor = async () => {
    if (mentors.length === 0) return;
    const idx = mentors.findIndex((item) => item.id === selectedMentorId);
    const next = mentors[(idx + 1) % mentors.length];
    await handleMentorChange(next.id);
  };

  const handleUpgradeClick = async () => {
    await trackGrowthEvent('voice_upgrade_cta_clicked');
    await onUpgrade();
  };

  return (
    <div className="min-h-screen bg-background-light pb-28">
      <header className="sticky top-0 z-40 border-b border-slate-200 bg-white/90 backdrop-blur-md">
        <div className="mx-auto flex h-16 max-w-md items-center justify-between px-4">
          <button type="button" onClick={onBack} className="rounded-full p-2 hover:bg-slate-100" aria-label="Voltar">
            <ArrowLeft size={20} />
          </button>
          <p className="text-sm font-black tracking-wide">Mentor ao Vivo</p>
          <button type="button" onClick={() => void handleCycleMentor()} className="rounded-full p-2 hover:bg-slate-100" aria-label="Trocar mentor">
            <Users size={18} />
          </button>
        </div>
      </header>

      <main className="mx-auto max-w-md space-y-4 px-4 pt-5">
        {isVoiceBlocked ? (
          <section className="rounded-xl border border-amber-200 bg-amber-50 p-4">
            <p className="text-sm font-bold text-amber-900">{VOICE_FREE_LIMIT_MESSAGE}</p>
            <button type="button" onClick={() => void handleUpgradeClick()} className="mt-3 w-full rounded-xl bg-slate-900 px-4 py-3 text-sm font-bold text-white">
              Desbloquear PRO
            </button>
          </section>
        ) : null}

        {error ? <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div> : null}

        {!audioAvailable ? (
          <div className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-xs text-slate-600">
            Audio indisponivel neste dispositivo. O tutor continua em texto.
          </div>
        ) : null}
        {!recognitionAvailable ? (
          <div className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-xs text-slate-600">
            Captura de voz indisponivel. Use o campo de texto como fallback.
          </div>
        ) : null}

        <MentorAvatarCard
          mentor={selectedMentor}
          state={voiceState}
          muted={muted}
          clientListening={voiceState === 'listening'}
          onToggleMute={() => setMuted((prev) => !prev)}
          onReplay={() => void replayLast()}
        />

        <section className="rounded-xl border border-slate-200 bg-white p-4">
          <div className="flex items-center justify-between">
            <p className="text-sm font-black">Escolha seu mentor</p>
            {voiceUsage?.plan === 'FREE' && voiceUsage.limit ? (
              <span className="rounded-full bg-slate-100 px-2 py-1 text-[10px] font-bold text-slate-600">
                {voiceUsage.used}/{voiceUsage.limit} usados
              </span>
            ) : null}
          </div>
          <div className="mt-3">
            <VoiceMentorPicker mentors={mentors} selectedMentorId={selectedMentorId} onSelect={(id) => void handleMentorChange(id)} />
          </div>
        </section>

        <section className="grid grid-cols-2 gap-2 rounded-xl border border-slate-200 bg-white p-4">
          <button
            type="button"
            onClick={() => void startSession()}
            disabled={sessionActive || !selectedMentorId || isVoiceBlocked}
            className="inline-flex items-center justify-center gap-2 rounded-xl bg-slate-900 px-3 py-3 text-sm font-bold text-white disabled:opacity-60"
          >
            <Play size={16} />
            Iniciar conversa
          </button>
          <button
            type="button"
            onClick={() => void endSession()}
            disabled={!sessionActive}
            className="inline-flex items-center justify-center gap-2 rounded-xl border border-slate-300 bg-white px-3 py-3 text-sm font-bold text-slate-700 disabled:opacity-60"
          >
            <Square size={16} />
            Encerrar
          </button>
        </section>

        <VoiceConversationPanel
          transcript={transcript}
          conversation={conversation}
          input={input}
          disabled={!sessionActive || !input.trim() || isVoiceBlocked}
          onInputChange={setInput}
          onSubmit={() => void submitMessage(input)}
          mentorName={selectedMentor?.name || 'Mentor'}
        />
      </main>

      <button
        type="button"
        onClick={startListening}
        aria-label="Falar com microfone"
        disabled={!sessionActive || !recognitionAvailable || isVoiceBlocked}
        className="fixed bottom-8 right-6 inline-flex size-14 items-center justify-center rounded-full bg-primary text-white shadow-xl disabled:opacity-50"
      >
        {voiceState === 'listening' ? <MicOff size={22} /> : <Mic size={22} />}
      </button>
    </div>
  );
}
