"use client";

import { useState } from "react";

const URL_BACKEND = "http://localhost:8000";

type Props = {
  onCompletato: () => void;
};

export default function UploadModal({ onCompletato }: Props) {
  const [file, setFile] = useState<File | null>(null);
  const [caricamento, setCaricamento] = useState(false);
  const [errore, setErrore] = useState("");

  async function carica() {
    if (!file) return;

    setCaricamento(true);
    setErrore("");

    try {
      const datiForm = new FormData();
      datiForm.append("file", file);

      const res = await fetch(`${URL_BACKEND}/carica`, {
        method: "POST",
        body: datiForm,
      });

      if (!res.ok) throw new Error("Errore durante l'indicizzazione");

      onCompletato();
    } catch {
      setErrore("Qualcosa è andato storto. Riprova.");
      setCaricamento(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70">
      <div className="w-full max-w-md rounded-lg bg-gray-800 p-6 text-gray-100">
        <h2 className="mb-2 text-xl font-bold text-purple-300">
          Carica un manuale PDF
        </h2>
        <p className="mb-4 text-sm text-gray-400">
          Scegli un PDF da indicizzare. L&apos;assistente risponderà basandosi su
          questo documento.
        </p>

        <input
          type="file"
          accept="application/pdf"
          onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          disabled={caricamento}
          className="mb-4 block w-full text-sm text-gray-300 file:mr-3 file:rounded file:border-0 file:bg-purple-600 file:px-3 file:py-2 file:text-white hover:file:bg-purple-500"
        />

        {errore && <p className="mb-3 text-sm text-red-400">{errore}</p>}

        <button
          onClick={carica}
          disabled={!file || caricamento}
          className="w-full rounded bg-purple-600 px-4 py-2 font-medium text-white hover:bg-purple-500 disabled:opacity-50"
        >
          {caricamento ? "Indicizzazione in corso…" : "Carica e indicizza"}
        </button>
      </div>
    </div>
  );
}