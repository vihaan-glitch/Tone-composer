import { useEffect, useState } from "react";
import Card from "../components/ui/Card";
import Button from "../components/ui/Button";
import Textarea from "../components/ui/Textarea";
import Slider from "../components/ui/Slider";
import { postBlob } from "../lib/api";

export default function AITone() {
  const [prompt, setPrompt] = useState("");
  const [bpm, setBpm] = useState(120);
  const [density, setDensity] = useState(0.8);
  const [brightness, setBrightness] = useState(0.7);
  const [guidance, setGuidance] = useState(4.0);
  const [duration, setDuration] = useState(12);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);

  useEffect(
    () => () => {
      if (audioUrl) {
        URL.revokeObjectURL(audioUrl);
      }
    },
    [audioUrl]
  );

  async function onGenerate() {
    setError(null);
    if (!prompt.trim()) {
      setError("Please describe the mood/instruments before generating.");
      return;
    }
    setLoading(true);
    try {
      const wav = await postBlob("/api/gemini/audio/wav", {
        prompt,
        bpm,
        density,
        brightness,
        guidance,
        duration_seconds: duration,
      });
      if (audioUrl) {
        URL.revokeObjectURL(audioUrl);
      }
      setAudioUrl(URL.createObjectURL(wav));
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : "Gemini generation failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <h1 className="title-font text-4xl font-semibold text-ink">AI Tone Composer</h1>
      <Card className="p-8">
        <p className="text-muted leading-relaxed">
          Generate audio by describing the fusion mood (ragas, jazz colors,
          instrumentation). Adjust tempo, density, brightness, and guidance strength to steer the
          output before auditioning or downloading a WAV.
        </p>
        <div className="mt-4 text-xs text-muted">
          Tip: keep prompts vivid but concise (mood + instruments + tempo) so Gemini can follow the
          arc you have in mind.
        </div>
      </Card>

      <Card className="p-8">
        <label className="block text-sm font-medium text-ink">
          Prompt
          <div className="mt-2">
            <Textarea
              value={prompt}
              onChange={(event) => setPrompt(event.currentTarget.value)}
              rows={6}
              placeholder="Cinematic raga mix with swelling Rhodes, tablas, and layered percussion..."
            />
          </div>
        </label>

        <div className="mt-6 grid grid-cols-1 gap-6 md:grid-cols-2">
          <Slider label="Tempo (BPM)" min={60} max={180} value={bpm} step={5} onChange={setBpm} />
          <Slider label="Duration (sec)" min={8} max={30} value={duration} step={2} onChange={setDuration} />
          <Slider label="Density" min={0.3} max={1.0} value={density} step={0.05} onChange={setDensity} />
          <Slider
            label="Brightness"
            min={0.0}
            max={1.0}
            value={brightness}
            step={0.05}
            onChange={setBrightness}
          />
          <Slider
            label="Guidance"
            min={1.0}
            max={12.0}
            step={0.5}
            value={guidance}
            onChange={setGuidance}
          />
        </div>

        <div className="mt-6">
          <Button onClick={onGenerate} disabled={loading}>
            {loading ? "Generating..." : "Generate Gemini Audio"}
          </Button>
          {error && <div className="mt-3 text-sm text-red-700">{error}</div>}
        </div>
      </Card>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card className="p-8">
          <h2 className="title-font text-xl font-semibold text-ink">Preview</h2>
          <div className="mt-4">
            {audioUrl ? (
              <audio controls src={audioUrl} className="w-full" />
            ) : (
              <div className="text-sm text-muted">Generate a tone to hear a preview.</div>
            )}
          </div>
          {audioUrl && (
            <div className="mt-4 rounded-2xl bg-white/60 p-4 text-sm text-muted">
              Download the result from your device playback controls.
            </div>
          )}
        </Card>

        <Card className="p-8">
          <h2 className="title-font text-xl font-semibold text-ink">Prompt Inspiration</h2>
          <ul className="mt-4 list-disc pl-6 text-sm text-muted space-y-2">
            <li>Layered Rhodes pads bursting into tabla grooves at 130 BPM.</li>
            <li>Dreamy drone + sparse fretless bass with interlocking tabla/resonator riffs.</li>
            <li>Ambient jazz stabs with sitar swells for a cinematic nocturnal landscape.</li>
          </ul>
        </Card>
      </div>
    </>
  );
}
