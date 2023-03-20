# VoiceCommandRecogition

git clone https://github.com/MrDreadiest/VoiceCommandRecogition.git

Zainstalowanie lokalnego środowiska python

cd .\venv\
python -m venv env_voice_command_classification
.\env_voice_command_classification\Scripts\activate
pip install ipykernel
python -m ipykernel install --name=env_voice_command_classification
pip install tensorflow==2.8.0 tensorflow-gpu==2.8.0 tensorflow-io==0.25.0 tensorflow_datasets matplotlib
pip install wave librosa soundfile noisereduce seaborn pyaudio