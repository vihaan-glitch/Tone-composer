import streamlit as st

from gemini_music import GeminiMusicError, generate_gemini_music_audio

st.set_page_config(
    page_title="Gemini Lyria Composer",
    page_icon="🎹",
    layout="centered",
)

st.title("Gemini Lyria Music Generation")
st.markdown(
    """
    Generate real-time fusion tones directly from **Gemini Lyria** (the experimental live music model).
    This interface only exposes the Gemini audio path—no text-to-ABC or local synthesis is included anymore.
    """
)

st.info("Ensure `GEMINI_API_KEY` is defined before generating audio. The model used is `models/lyria-realtime-exp`.")

with st.form("gemini_audio_form"):
    prompt = st.text_area(
        "Describe the fusion mood/instruments:",
        height=160,
        placeholder="Lean into cinematic ragas with swelling Rhodes, tablas, and layered percussion...",
    )

    col1, col2 = st.columns(2)
    with col1:
        bpm = st.slider("Tempo (BPM)", min_value=60, max_value=200, value=120, step=5)
        density = st.slider("Density", min_value=0.3, max_value=1.0, value=0.8, step=0.05)
        duration_seconds = st.slider(
            "Duration (seconds)", min_value=8, max_value=30, value=16, step=2
        )
    with col2:
        brightness = st.slider("Brightness", min_value=0.0, max_value=1.0, value=0.7, step=0.05)
        guidance_strength = st.slider(
            "Guidance strength", min_value=1.0, max_value=12.0, value=4.0, step=0.5
        )

    submitted = st.form_submit_button("Generate Gemini Audio")

if submitted:
    if not prompt.strip():
        st.warning("Please add a prompt so the Gemini listener knows what to compose.")
    else:
        with st.spinner("Streaming audio from Gemini Lyria..."):
            try:
                audio_bytes = generate_gemini_music_audio(
                    prompt=prompt,
                    bpm=bpm,
                    density=density,
                    brightness=brightness,
                    guidance=guidance_strength,
                    duration_seconds=duration_seconds,
                )
            except GeminiMusicError as exc:
                st.error("Gemini Lyria generation failed.")
                st.write(f"`{exc}`")
                st.caption(
                    "Confirm `GEMINI_API_KEY` is set, has access to the live music model, and restart Streamlit if you just updated the key."
                )
            except Exception as exc:  # pragma: no cover
                st.error("Unexpected error while generating audio.")
                st.write(f"`{exc}`")
            else:
                st.success("Audio generated successfully.")
                st.audio(audio_bytes, format="audio/wav")
                st.download_button(
                    "Download WAV",
                    data=audio_bytes,
                    file_name="gemini-lyria.wav",
                    mime="audio/wav",
                )

with st.expander("Prompt inspiration"):
    st.markdown("- Cinematic raga meditation overlayed with rhythmic Rhodes swells.")
    st.markdown("- Sparse tabla loops + lush fretless bass, gradually introducing orchestral pads.")
    st.markdown("- Dreamy ambient drones with occasional jazz-influenced piano stabs.")
