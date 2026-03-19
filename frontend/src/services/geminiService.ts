import { sendChatMessage } from '../api/auth';

export async function getChatResponse(message: string) {
  const response = await sendChatMessage(message);
  return response.reply || 'Desculpe, nao consegui processar sua mensagem.';
}
