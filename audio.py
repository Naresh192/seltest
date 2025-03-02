import streamlit as st
import subprocess
import shutil
from pathlib import Path
from TTS.api import TTS
from pydub import AudioSegment
import tempfile
import os

def separate_vocals(song_path, output_dir):
    """Separate vocals using Demucs"""
    try:
        subprocess.run(
            ["demucs", "--two-stems=vocals", str(song_path), "-o", str(output_dir)],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        song_name = song_path.stem
        model_dir = output_dir / "htdemucs" / song_name
        
        shutil.copy(model_dir / "vocals.wav", output_dir / "vocals.wav")
        shutil.copy(model_dir / "no_vocals.wav", output_dir / "accompaniment.wav")
        
        shutil.rmtree(output_dir / "htdemucs")
        
    except subprocess.CalledProcessError as e:
        st.error(f"Error during vocal separation: {e.stderr.decode()}")
        raise e
    except Exception as e:
        st.error(f"An error occurred during vocal separation: {str(e)}")
        raise e

def convert_mp3_to_wav(mp3_path, wav_path):
    """Convert audio format from MP3 to WAV"""
    try:
        audio = AudioSegment.from_mp3(mp3_path)
        audio.export(wav_path, format="wav")
    except Exception as e:
        st.error(f"Error converting MP3 to WAV: {str(e)}")
        raise e

def generate_voice(vocal_track_path, voice_sample_path, output_path):
    """Generate voice conversion using TTS"""
    try:
        tts = TTS(
            model_name="voice_conversion_models/multilingual/vctk/freevc24",
            progress_bar=False,
            gpu=False
        )
        tts.voice_conversion_to_file(
            source_wav=str(vocal_track_path),
            target_wav=str(voice_sample_path),
            file_path=str(output_path)
        )
    except Exception as e:
        st.error(f"Error generating new vocals: {str(e)}")
        raise e

def mix_tracks(instrumental_track_path, vocal_track_path, final_output_path):
    """Mix instrumental and vocal tracks"""
    try:
        instrumental = AudioSegment.from_wav(str(instrumental_track_path))
        vocals = AudioSegment.from_wav(str(vocal_track_path))
        mixed = instrumental.overlay(vocals)
        mixed.export(final_output_path, format="mp3")
    except Exception as e:
        st.error(f"Error mixing tracks: {str(e)}")
        raise e

def main():
    st.title("🎵 Song Voice Conversion Tool")
    st.markdown("Upload a sample voice and a song to create a new version with the converted voice!")

    with st.form("upload_form"):
        sample_voice = st.file_uploader("Sample Voice (MP3)", type=["mp3"])
        original_song = st.file_uploader("Original Song (MP3)", type=["mp3"])
        submitted = st.form_submit_button("Process Files")

    if submitted and sample_voice and original_song:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            try:
                # Save uploaded files
                sample_path = tmp_path / "sample_voice.mp3"
                sample_path.write_bytes(sample_voice.getvalue())
                
                original_path = tmp_path / "original_song.mp3"
                original_path.write_bytes(original_song.getvalue())

                # Processing steps
                with st.status("Processing...", expanded=True) as status:
                    st.write("Separating vocals and instrumentals...")
                    output_dir = tmp_path / "output"
                    output_dir.mkdir()
                    separate_vocals(original_path, output_dir)

                    st.write("Converting sample voice to WAV...")
                    voice_sample_wav = tmp_path / "voice_sample.wav"
                    convert_mp3_to_wav(sample_path, voice_sample_wav)

                    st.write("Generating new vocals...")
                    new_vocals_path = tmp_path / "new_vocals.wav"
                    generate_voice(output_dir / "vocals.wav", voice_sample_wav, new_vocals_path)

                    st.write("Mixing tracks...")
                    final_output = tmp_path / "final_output.mp3"
                    mix_tracks(output_dir / "accompaniment.wav", new_vocals_path, final_output)

                    status.update(label="Processing complete!", state="complete")

                # Provide download
                with open(final_output, "rb") as f:
                    st.download_button(
                        "Download Converted Song",
                        data=f,
                        file_name="converted_song.mp3",
                        mime="audio/mpeg",
                        type="primary"
                    )
            
            except Exception as e:
                st.error(f"An error occurred during processing: {str(e)}")

    elif submitted:
        st.error("Please upload both files before processing")

if __name__ == "__main__":
    main()
