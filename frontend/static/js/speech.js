// Web Speech API Multi-Lingual Voice Assistant for Patient Accessibility

class VoiceExplanationAssistant {
    constructor() {
        this.synth = window.speechSynthesis;
        this.utterance = null;
        this.isPlaying = false;
        this.voices = [];
        if (this.synth) {
            this.loadVoices();
            if (this.synth.onvoiceschanged !== undefined) {
                this.synth.onvoiceschanged = () => this.loadVoices();
            }
        }
    }

    loadVoices() {
        if (this.synth) {
            this.voices = this.synth.getVoices();
        }
    }

    getLanguageTag(langKey) {
        const langMap = {
            'en': 'en-IN',
            'hi': 'hi-IN',
            'kn': 'kn-IN',
            'te': 'te-IN',
            'ta': 'ta-IN'
        };
        return langMap[langKey] || 'en-IN';
    }

    speak(text, langKey = 'en') {
        if (!this.synth) {
            alert('Voice explanation is not supported in this browser.');
            return;
        }

        if (this.isPlaying) {
            this.stop();
        }

        if (this.voices.length === 0) {
            this.loadVoices();
        }

        const targetLangTag = this.getLanguageTag(langKey);
        this.utterance = new SpeechSynthesisUtterance(text);
        this.utterance.rate = 0.88; // Clear reading pace for regional languages

        // Search for matching native voice
        let matchedVoice = this.voices.find(v => 
            v.lang.toLowerCase() === targetLangTag.toLowerCase() || 
            v.lang.toLowerCase().startsWith(langKey.toLowerCase())
        );

        if (matchedVoice) {
            this.utterance.lang = matchedVoice.lang;
            this.utterance.voice = matchedVoice;
        } else {
            // Fallback to Indian English or available voice so audio NEVER fails
            let fallbackVoice = this.voices.find(v => v.lang.includes('IN') || v.lang.includes('en')) || this.voices[0];
            if (fallbackVoice) {
                this.utterance.voice = fallbackVoice;
                this.utterance.lang = fallbackVoice.lang;
            } else {
                this.utterance.lang = targetLangTag;
            }
        }

        this.utterance.onstart = () => {
            this.isPlaying = true;
            this.updateUI(true);
        };

        this.utterance.onend = () => {
            this.isPlaying = false;
            this.updateUI(false);
        };

        this.utterance.onerror = (err) => {
            console.warn('Speech synthesis playback fallback triggered:', err);
            this.isPlaying = false;
            this.updateUI(false);
        };

        this.synth.speak(this.utterance);
    }

    pause() {
        if (this.synth && this.isPlaying) {
            this.synth.pause();
        }
    }

    resume() {
        if (this.synth && this.synth.paused) {
            this.synth.resume();
        }
    }

    stop() {
        if (this.synth) {
            this.synth.cancel();
            this.isPlaying = false;
            this.updateUI(false);
        }
    }

    updateUI(playing) {
        const playBtn = document.getElementById('voicePlayBtn');
        const icon = document.getElementById('voiceIcon');
        if (playBtn && icon) {
            if (playing) {
                playBtn.classList.replace('btn-outline-primary', 'btn-danger');
                icon.className = 'fa-solid fa-square me-1';
                playBtn.title = 'Stop Voice Explanation';
            } else {
                playBtn.classList.replace('btn-danger', 'btn-outline-primary');
                icon.className = 'fa-solid fa-volume-high me-1';
                playBtn.title = 'Listen to Explanation';
            }
        }
    }
}

const voiceAssistant = new VoiceExplanationAssistant();

function toggleVoiceExplanation(textElementId, langKey = 'en') {
    const el = document.getElementById(textElementId);
    if (!el) return;

    if (voiceAssistant.isPlaying) {
        voiceAssistant.stop();
    } else {
        voiceAssistant.speak(el.innerText, langKey);
    }
}
