import requests

def text_to_speech(text: str, speed: int = 100, pitch: int = 100, volume: int = 100, speaker: int = 0):
    """
    Convert text to speech using the fish audio API.
    """
    url = "https://api.fishaudio.example/text2speech"
    payload = {
        "text": text,
        "speed": speed,
        "pitch": pitch,
        "volume": volume,
        "speaker": speaker
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        return response.content
    else:
        raise Exception("Fish Audio TTS API Error: " + response.text)

if __name__ == "__main__":
    text = "こんにちは、カリフォルニアは良い天気です"
    audio_data = text_to_speech(text)
    with open("output.wav", "wb") as f:
        f.write(audio_data)
    print("Audio saved to output.wav")
