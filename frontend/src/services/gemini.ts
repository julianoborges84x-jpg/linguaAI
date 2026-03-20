import { GoogleGenAI, Type } from '@google/genai';

const API_KEY = import.meta.env.VITE_GEMINI_API_KEY || '';

export interface SocialDrafts {
  linkedin: { text: string; imagePrompt: string };
  twitter: { text: string; imagePrompt: string };
  instagram: { text: string; imagePrompt: string };
}

function getClient() {
  if (!API_KEY) {
    throw new Error('GEMINI_API_KEY nao configurada. Defina VITE_GEMINI_API_KEY no frontend/.env.');
  }
  return new GoogleGenAI({ apiKey: API_KEY });
}

export async function generateSocialContent(idea: string, tone: string): Promise<SocialDrafts> {
  const ai = getClient();
  const prompt = `Generate social media content for the following idea: "${idea}".
Tone: ${tone}.
Return JSON with:
{
  "linkedin": { "text": "...", "imagePrompt": "..." },
  "twitter": { "text": "...", "imagePrompt": "..." },
  "instagram": { "text": "...", "imagePrompt": "..." }
}`;

  const response = await ai.models.generateContent({
    model: 'gemini-2.5-flash',
    contents: [{ role: 'user', parts: [{ text: prompt }] }],
    config: {
      responseMimeType: 'application/json',
      responseSchema: {
        type: Type.OBJECT,
        properties: {
          linkedin: {
            type: Type.OBJECT,
            properties: { text: { type: Type.STRING }, imagePrompt: { type: Type.STRING } },
            required: ['text', 'imagePrompt'],
          },
          twitter: {
            type: Type.OBJECT,
            properties: { text: { type: Type.STRING }, imagePrompt: { type: Type.STRING } },
            required: ['text', 'imagePrompt'],
          },
          instagram: {
            type: Type.OBJECT,
            properties: { text: { type: Type.STRING }, imagePrompt: { type: Type.STRING } },
            required: ['text', 'imagePrompt'],
          },
        },
        required: ['linkedin', 'twitter', 'instagram'],
      },
    },
  });

  return JSON.parse(response.text || '{}') as SocialDrafts;
}

export async function generatePlatformImage(
  prompt: string,
  aspectRatio: '1:1' | '4:3' | '16:9',
  size: '1K' | '2K' | '4K',
): Promise<string> {
  const ai = getClient();
  const response = await ai.models.generateContent({
    model: 'gemini-2.5-flash-image-preview',
    contents: [{ role: 'user', parts: [{ text: prompt }] }],
    config: {
      imageConfig: {
        aspectRatio,
        imageSize: size,
      },
    },
  });

  for (const part of response.candidates?.[0]?.content?.parts || []) {
    if (part.inlineData?.data) {
      return `data:image/png;base64,${part.inlineData.data}`;
    }
  }

  throw new Error('No image data returned from Gemini');
}
