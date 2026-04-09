# Data Governance Reflection

## 1. Consent
If my script processed real user sound instead of the text-to-speech AI voices I used, we'd need strict consent.
A screen must pop up before the app ever uses the microphone. It should say: "We send your voice recordings to third parties like OpenAI for transcription. Audio may be temporarily stored on their servers. Do you agree?"
Users must click a clear "I Agree" button. In the app settings, there has to be a visible option to easily revoke consent, which would stop future recordings and delete anything pending.

## 2. Retention
File retention depends totally on the use case:
*   **(a) Study App:** Things like my generated `voice_alloy_sample.mp3` can be kept for months to save on the $0.015/1k chars API cost since it's just study material.
*   **(b) Customer Service:** Keep recordings for 30 days maximum just for QA audits, then delete them to protect caller privacy.
*   **(c) Medical Intake:** Highly sensitive. The raw audio must be deleted the literal second the text transcript is completed. If the law says we have to keep it, it needs serious encryption.

## 3. PII in Audio
Audio exposes way more PII than text. My test had a 92.3% text match because of a slight typo, but real human audio also captures voice biometrics—unique tones that act like a fingerprint. It grabs the speaker's emotional state (like stress or anger) which text strips out. It can even pick up background noise, like a specific train station announcement, revealing location data without the user meaning to.

## 4. Your Capstone
In Team Exercise 3, we decided on a "No audio" approach for our capstone to avoid these exact privacy issues. 
If we added it later, our whole data governance would completely change. We'd have to build microphone opt-in flows, and we'd need backend logic to instantly delete the temporary audio files right after the API returns the transcript, keeping only text in our database and it would also be more costly to talk to the CEO, but maybe we can add it in the future.
