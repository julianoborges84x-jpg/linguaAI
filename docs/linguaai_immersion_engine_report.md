# LinguaAI Immersion Engine - Arquitetura Produto + Growth

## 1) Arquitetura proposta

### Visao geral
- Arquitetura incremental sobre a base SaaS atual, sem quebrar auth/sessions/dashboard/growth/billing.
- Novo dominio `Immersion Engine` desacoplado em camadas:
  - `models/immersion.py`: persistencia de cenarios, sessoes, tutor, missoes, multiplayer, notificacoes.
  - `services/immersion_service.py`: regras de negocio de roleplay, analise de fluencia, personalizacao e growth loops.
  - `api/routes/immersion.py`: API REST para frontend mobile-first.
  - `schemas/immersion.py`: contratos de entrada/saida.
  - `alembic/versions/0008_immersion_engine_foundation.py`: migracao idempotente para escala.

### Principios
- Modularidade: novo bounded context `immersion`.
- Compatibilidade: nenhuma rota existente alterada.
- Persistencia para IA adaptativa: dados estruturados para personalizacao por usuario.
- Growth embutido no core: eventos, loops e gatilhos de notificacao nao sao "addon".

## 2) Novos modulos implementados

- `ImmersionScenario`: cenarios de vida real (aeroporto, restaurante, hotel, reuniao, entrevista, networking, viagem, hospital, policia, namoro).
- `RoleplayCharacter`: personagens IA com personalidade, sotaque, objetivo.
- `ImmersionSession` + `ImmersionTurn`: conversa real por turnos com scoring.
- `TutorProfile`: memoria adaptativa de erros, vocabulario fraco, pronuncia e confianca.
- `ImmersionMission` + `UserImmersionMissionProgress`: missoes reais com recompensa em XP.
- `MultiplayerChallenge`: estrutura base para modo multiplayer e desafios.
- `SmartNotificationQueue`: fila de push inteligente baseada em comportamento e risco de churn.

## 3) Endpoints novos

Base: `/immersion`

- `GET /scenarios`
- `GET /scenarios/{scenario_slug}/characters`
- `POST /sessions/start`
- `POST /sessions/{session_id}/turn`
- `POST /sessions/{session_id}/finish`
- `GET /dashboard`
- `GET /missions`
- `POST /missions/{mission_id}/claim`
- `POST /multiplayer/challenges`
- `POST /multiplayer/challenges/{challenge_id}/join`
- `POST /notifications/sync`
- `GET /landing`

## 4) Modelos de dados novos

### Core de imersao
- `immersion_scenarios`
- `roleplay_characters`
- `immersion_sessions`
- `immersion_turns`
- `tutor_profiles`

### Core de engajamento/growth
- `immersion_missions`
- `user_immersion_mission_progress`
- `multiplayer_challenges`
- `smart_notification_queue`

## 5) Componentes frontend novos

- `frontend/src/components/ImmersionScreen.tsx`:
  - Catalogo de cenarios real-world
  - Roleplay em tempo real (turnos)
  - Feedback imediato (hints)
  - Analise de fluencia (speed/fillers/grammar/pronunciation/score)
  - Missoes reais com claim de XP
- Integração no fluxo principal:
  - `App.tsx` com nova tela `immersion`
  - `DashboardScreen.tsx` com atalhos para Immersion Engine
  - `api/auth.ts` expandida com clientes de imersao
  - `types.ts` com novos contratos de dados

## 6) Mudancas no banco

- Migracao: `0008_immersion_engine_foundation`.
- Criadas tabelas/indexes para sessao de imersao, roleplay, tutor, missoes, multiplayer, notificacoes.
- Runtime fallback atualizado em `schema_compat.py` para garantir compatibilidade em ambientes com migracao atrasada.

## 7) Mecanismos de diferenciacao implementados

- Simulacoes de vida real por cenario.
- Roleplay por personagem com persona/sotaque/objetivo.
- Analise de fluencia com:
  - speaking speed
  - filler words
  - grammar mistakes
  - pronunciation score
- Tutor pessoal adaptativo com memoria de erros recorrentes e plano de foco.
- Progressao RPG de fluencia:
  - Turista, Viajante, Morador, Profissional, Especialista, Nativo.
- Conteudo infinito (seed dinamica + engine pronta para expansao automatica por IA).
- Multiplayer foundation (criar/entrar desafio).
- Push inteligente por gatilhos de risco/oportunidade.
- Landing API para LP de alta conversao com demo de tutor e sample de conversa.

## 8) Growth loops

- Referral + booster:
  - Convide amigo -> booster de XP temporario.
- Social virality:
  - Sessao concluida gera `share_token` para gravacao/compartilhamento.
- Habit loop:
  - Notificacao inteligente -> missao real -> XP -> novo desafio.
- Monetizacao:
  - Progressao e cenarios mais complexos prontos para camadas PRO (unlock por nivel/contexto).

## 9) Roadmap de escala (produto + tecnico)

### 0 -> 10k usuarios
- Foco: PMF por nicho inicial (viagem + trabalho).
- Tecnico:
  - Monolito atual + Postgres gerenciado.
  - Cache simples para cenarios/personagens.
  - Observabilidade basica (erro, latencia, funil onboarding).
- Growth:
  - LP com demo interativa curta.
  - Loop referral com recompensa instantanea.

### 10k -> 100k usuarios
- Foco: retencao D7/D30 e ativacao por roleplay.
- Tecnico:
  - Filas para jobs assinc (notificacoes, analise offline, eventos).
  - CDN para assets sociais/compartilhamento.
  - particionamento leve de analytics events.
- Growth:
  - desafios multiplayer semanais.
  - programa de creators (compartilhar roleplays).

### 100k -> 1M usuarios
- Foco: custo por sessao IA + internacionalizacao.
- Tecnico:
  - separacao de servico de inferencia/conversacao.
  - rate limiting por plano.
  - camada de feature flags e experimentacao A/B.
  - replica de leitura para dashboards/ranking.
- Growth:
  - parcerias B2B2C (escolas/comunidades/travel).
  - loops regionais com leaderboard local.

### 1M -> 10M usuarios
- Foco: confiabilidade global e unit economics.
- Tecnico:
  - arquitetura orientada a eventos (analytics, tutor, notificacoes).
  - modelos de custo hibrido (cached responses + realtime premium).
  - multi-regiao para latencia e resiliencia.
  - anti-abuse/fraud para referral e multiplayer.
- Growth:
  - marca de produto: "conversacao real em contexto real".
  - funil enterprise para upskilling corporativo.

## 10) Proximos incrementos recomendados (fase 2)

- STT/TTS real para pronuncia fonetica com waveform scoring.
- gravacao de clips reais com export social nativo.
- matchmaking de multiplayer por nivel/objetivo/fuso.
- orquestrador de conteudo infinito multi-idioma com curadoria de qualidade.
- notificacao omnichannel (push/email/whatsapp) com modelo de propensao.
