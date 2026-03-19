import { ArrowLeft, Mic, MicOff, Play, Repeat2, Send, Square, Volume2, VolumeX } from 'lucide-react';
import { useEffect, useMemo, useRef, useState } from 'react';

import { fetchVoiceMentors, fetchVoiceUsage, sendVoiceMentorMessage, trackGrowthEvent } from '../api/auth';
import { AuthUser, VoiceMentor, VoiceUsage } from '../types';
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
  onerror: (() => void) | null;
  onend: (() => void) | null;
  start: () => void;
  stop: () => void;
};

function voiceSettings(mentorId: string): { rate: number; pitch: number } {
  if (mentorId === 'clara') return { rate: 0.95, pitch: 1.25 };
  if (mentorId === 'maya') return { rate: 1.0, pitch: 1.15 };
  if (mentorId === 'ethan') return { rate: 0.95, pitch: 0.95 };
  return { rate: 0.9, pitch: 0.9 };
}

export default function VoiceChatScreen({ user, onBack, onUpgrade }: Props) {
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
    recognitionRef.current.onerror = () => setVoiceState('idle');
    recognitionRef.current.onend = () => {
      setVoiceState((prev) => (prev === 'listening' ? 'idle' : prev));
    };
    recognitionRef.current.onresult = async (event) => {
      const text = event.results[0]?.[0]?.transcript?.trim() || '';
      if (!text) return;
      setTranscript(text);
      await submitMessage(text);
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

  const startSession = async () => {
    setSessionActive(true);
    setVoiceState('idle');
    await trackGrowthEvent('voice_session_started', { mentor_id: selectedMentorId });
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

  const speakText = async (text: string) => {
    if (!audioAvailable || muted) return;
    if (typeof window === 'undefined' || !window.speechSynthesis || typeof SpeechSynthesisUtterance === 'undefined') return;

    setVoiceState('speaking');
    const utterance = new SpeechSynthesisUtterance(text);
    const cfg = voiceSettings(selectedMentorId);
    utterance.rate = cfg.rate;
    utterance.pitch = cfg.pitch;
    utterance.onend = () => setVoiceState('idle');
    speechRef.current = utterance;
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(utterance);
  };

  const submitMessage = async (text: string) => {
    if (!sessionActive || !selectedMentorId || !text.trim() || isVoiceBlocked) return;
    setError('');
    setVoiceState('thinking');
    const clean = text.trim();
    try {
      const response = await sendVoiceMentorMessage(selectedMentorId, clean);
      setTranscript(response.transcript);
      setVoiceUsage(response.voice_usage);
      setConversation((prev) => [...prev, { role: 'user', text: clean }, { role: 'mentor', text: response.reply }]);
      setInput('');
      if (response.audio_available) {
        await speakText(response.tts_text || response.reply);
      } else {
        setVoiceState('idle');
      }
    } catch (err) {
      setVoiceState('idle');
      const message = err instanceof Error ? err.message : 'Falha ao conversar com mentor por voz.';
      setError(message);
      if (message === VOICE_FREE_LIMIT_MESSAGE) {
        setVoiceUsage((prev) => {
          if (!prev || prev.plan !== 'FREE' || !prev.limit) {
            return { plan: 'FREE', used: 6, limit: 6, remaining: 0, blocked: true };
          }
          return { ...prev, used: prev.limit, remaining: 0, blocked: true };
        });
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

  const handleUpgradeClick = async () => {
    await trackGrowthEvent('voice_upgrade_cta_clicked');
    await onUpgrade();
  };

  const handleMentorChange = async (mentorId: string) => {
    setSelectedMentorId(mentorId);
    await trackGrowthEvent('voice_mentor_selected', { mentor_id: mentorId });
  };

  return (
    <div className="min-h-screen bg-background-light pb-8">
      <header className="sticky top-0 z-30 border-b border-slate-200 bg-white/90 backdrop-blur-md">
        <div className="mx-auto flex h-16 max-w-md items-center justify-between px-4">
          <button onClick={onBack} className="rounded-full p-2 hover:bg-slate-100">
            <ArrowLeft size={20} />
          </button>
          <p className="text-sm font-black tracking-wide">🎙️ Mentores de Voz</p>
          <span className="rounded-full bg-primary/10 px-2 py-1 text-[10px] font-black uppercase text-primary">{voiceState}</span>
        </div>
      </header>

      <main className="mx-auto max-w-md space-y-4 px-4 pt-5">
        <>
          {isVoiceBlocked ? (
            <section className="rounded-xl border border-amber-200 bg-amber-50 p-4">
              <p className="text-sm font-bold text-amber-900">{VOICE_FREE_LIMIT_MESSAGE}</p>
              <button onClick={handleUpgradeClick} className="mt-3 w-full rounded-xl bg-slate-900 px-4 py-3 text-sm font-bold text-white">
                Desbloquear agora
              </button>
            </section>
          ) : null}
          {error ? <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div> : null}

          {!audioAvailable ? (
            <div className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-xs text-slate-600">
              Audio indisponivel neste dispositivo. O chat continua em texto.
            </div>
          ) : null}
          {!recognitionAvailable ? (
            <div className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-xs text-slate-600">
              Captura de voz indisponivel. Use o campo de texto como fallback.
            </div>
          ) : null}

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

          <section className="rounded-xl border border-slate-200 bg-white p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-black">Mentor selecionado</p>
                <p className="text-xs text-slate-600">{selectedMentor?.name || 'Carregando...'}</p>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setMuted((prev) => !prev)}
                  aria-label={muted ? 'Ativar audio' : 'Mutar audio'}
                  className="rounded-lg border border-slate-300 bg-white px-2 py-1 text-xs font-semibold text-slate-700"
                >
                  {muted ? <VolumeX size={14} /> : <Volume2 size={14} />}
                </button>
                <button
                  onClick={() => void replayLast()}
                  aria-label="Repetir ultima resposta"
                  className="rounded-lg border border-slate-300 bg-white px-2 py-1 text-xs font-semibold text-slate-700"
                >
                  <Repeat2 size={14} />
                </button>
              </div>
            </div>

            <div className="mt-3 grid grid-cols-2 gap-2">
              <button
                onClick={() => void startSession()}
                disabled={sessionActive || !selectedMentorId || isVoiceBlocked}
                className="inline-flex items-center justify-center gap-2 rounded-xl bg-slate-900 px-3 py-3 text-sm font-bold text-white disabled:opacity-60"
              >
                <Play size={16} />
                Iniciar conversa
              </button>
              <button
                onClick={() => void endSession()}
                disabled={!sessionActive}
                className="inline-flex items-center justify-center gap-2 rounded-xl border border-slate-300 bg-white px-3 py-3 text-sm font-bold text-slate-700 disabled:opacity-60"
              >
                <Square size={16} />
                Encerrar
              </button>
            </div>

            <div className="mt-3 flex gap-2">
              <button
                onClick={startListening}
                aria-label="Falar com microfone"
                disabled={!sessionActive || !recognitionAvailable || isVoiceBlocked}
                className="inline-flex items-center justify-center rounded-xl bg-primary px-3 py-3 text-white disabled:opacity-50"
              >
                {voiceState === 'listening' ? <MicOff size={16} /> : <Mic size={16} />}
              </button>
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ou digite sua frase em ingles..."
                className="flex-1 rounded-xl border border-slate-300 px-3 py-2 text-sm"
              />
              <button
                onClick={() => void submitMessage(input)}
                aria-label="Enviar mensagem de voz"
                disabled={!sessionActive || !input.trim() || isVoiceBlocked}
                className="inline-flex items-center justify-center rounded-xl border border-slate-300 bg-white px-3 py-2 text-slate-700 disabled:opacity-50"
              >
                <Send size={16} />
              </button>
            </div>
          </section>

          <section className="rounded-xl border border-slate-200 bg-white p-4">
            <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">Transcricao</p>
            <p className="mt-1 text-sm text-slate-800">{transcript || 'Aguardando sua fala...'}</p>
          </section>

          <section className="rounded-xl border border-slate-200 bg-white p-4">
            <p className="text-sm font-black">Conversa</p>
            <div className="mt-3 space-y-2">
              {conversation.length === 0 ? <p className="text-sm text-slate-500">Inicie para ver resposta em texto + audio.</p> : null}
              {conversation.map((line, idx) => (
                <div
                  key={`${line.role}-${idx}`}
                  className={`rounded-lg px-3 py-2 text-sm ${line.role === 'mentor' ? 'border border-slate-200 bg-slate-50' : 'ml-8 bg-primary text-white'}`}
                >
                  <p className="mb-1 text-[10px] font-bold uppercase opacity-70">{line.role === 'mentor' ? selectedMentor?.name || 'Mentor' : 'Voce'}</p>
                  <p>{line.text}</p>
                </div>
              ))}
            </div>
          </section>
        </>
      </main>
    </div>
  );
}
