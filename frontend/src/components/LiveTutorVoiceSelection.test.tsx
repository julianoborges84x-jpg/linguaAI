import { selectMentorVoice } from './LiveTutorScreen';

describe('selectMentorVoice', () => {
  it('prioriza voz feminina para clara/maya em en-US', () => {
    const voices = [
      { name: 'Google US English Male', lang: 'en-US', voiceURI: 'male' },
      { name: 'Google US English Female', lang: 'en-US', voiceURI: 'female' },
    ] as unknown as SpeechSynthesisVoice[];

    const voice = selectMentorVoice('clara', voices);
    expect(voice?.name).toContain('Female');
  });

  it('prioriza voz masculina para noah/ethan em en-US', () => {
    const voices = [
      { name: 'Google US English Female', lang: 'en-US', voiceURI: 'female' },
      { name: 'Google US English Male', lang: 'en-US', voiceURI: 'male' },
    ] as unknown as SpeechSynthesisVoice[];

    const voice = selectMentorVoice('ethan', voices);
    expect(voice?.name).toContain('Male');
  });
});
