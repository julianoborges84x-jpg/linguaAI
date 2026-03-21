# Videochamada IA em Tempo Real - Arquitetura Inicial

## Objetivo

Evoluir o "Mentor ao Vivo" (voz + texto) para uma experiencia de videochamada em tempo real, com:

- audio bidirecional de baixa latencia,
- video local do aluno,
- avatar/tutor IA com resposta em tempo real,
- observabilidade e fallback seguro.

## Escopo de Fases

### Fase 1 (MVP pronto para producao)

- manter frontend atual como base,
- adicionar sessao realtime no backend com handshake,
- usar WebRTC para audio/video do aluno,
- manter resposta IA inicialmente em audio sintetizado (sem avatar gerado em video),
- fallback para modo voz/texto quando realtime indisponivel.

### Fase 2 (Avatar IA de video)

- integrar servico de avatar realtime (provider externo ou stack propria),
- sincronizar labial com TTS,
- trocar card estatico por stream de video do tutor.

### Fase 3 (Qualidade e escala)

- SFU para salas e alta concorrencia,
- ajuste adaptativo de bitrate,
- QoS e metricas por sessao,
- retentativas inteligentes em reconexao.

## Topologia Recomendada (MVP)

- Frontend (Vercel): UI + WebRTC client + captura de camera/microfone.
- API Backend (Render): autenticacao, orquestracao de sessao, autorizacao, billing.
- Realtime Gateway (novo servico): sinalizacao WebRTC e controle de sessao.
- LLM/TTS (servico IA): gera resposta textual e audio.

## Componentes Novos

### Backend

- `POST /realtime/sessions/start`
  - cria sessao realtime assinada para usuario autenticado.
- `POST /realtime/sessions/{id}/signal`
  - troca SDP/ICE.
- `POST /realtime/sessions/{id}/stop`
  - encerra sessao.
- tabela `realtime_sessions`
  - `id`, `user_id`, `mentor_id`, `status`, `started_at`, `ended_at`, `duration_seconds`, `fallback_reason`.

### Frontend

- `RealtimeMentorScreen.tsx`
  - estado de conexao (connecting/live/reconnecting/fallback),
  - player de audio remoto,
  - video local e quadro do tutor.
- `realtimeClient.ts`
  - cria `RTCPeerConnection`,
  - envia sinalizacao para backend,
  - monitora qualidade e reconexao.

## Regras de Fallback

- se handshake falhar > 8s, cair para modo `voice/chat` atual.
- se upstream IA indisponivel, responder mensagem amigavel sem erro 5xx para o usuario.
- registrar `fallback_reason` para analytics.

## Observabilidade

- evento `realtime_session_started`
- evento `realtime_session_failed`
- evento `realtime_session_fallback`
- evento `realtime_session_ended`
- metricas:
  - tempo de conexao,
  - latencia media de resposta,
  - taxa de quedas por minuto,
  - duracao media de sessao.

## Seguranca

- token curto de sessao realtime (expiracao de minutos),
- validacao de usuario por JWT,
- limite de taxa por usuario/IP,
- CORS estrito e `trusted hosts` para dominio final.

## Checklist de Implementacao (proxima iteracao)

1. Criar schema/model `realtime_sessions`.
2. Expor rotas `/realtime/sessions/*` no backend.
3. Criar `frontend/src/api/realtime.ts`.
4. Criar `frontend/src/components/RealtimeMentorScreen.tsx`.
5. Adicionar botao "Video ao vivo (beta)" no dashboard.
6. Implementar fallback automatico para `LiveTutorScreen`.
7. Testes de contrato e smoke de conexao.
