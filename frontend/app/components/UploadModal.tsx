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
  const [progresso, setProgresso] = useState(0);

  async function carica() {
   if (!file) return;

   setCaricamento(true);
   setErrore('');
   setProgresso(0);

   try {
    // Fase 1: carico il file sul backend.
    const datiForm = new FormData();
    datiForm.append('file', file);

    const res = await fetch(`${URL_BACKEND}/carica`, {
     method: 'POST',
     body: datiForm,
    });

    if (!res.ok) throw new Error('Errore durante il caricamento');

    const dati = await res.json();

    // Fase 2: avvio l'indicizzazione e ascolto il progresso via SSE.
    const sorgente = new EventSource(
     `${URL_BACKEND}/indicizza-stream?nome=${encodeURIComponent(dati.nome)}`,
    );

    sorgente.onmessage = (evento) => {
     const stato = JSON.parse(evento.data);

     if (stato.completato) {
      sorgente.close();
      onCompletato();
      return;
     }

     const percentuale = Math.round((stato.fatti / stato.totale) * 100);
     setProgresso(percentuale);
    };

    sorgente.onerror = () => {
     sorgente.close();
     setErrore("Errore durante l'indicizzazione. Riprova.");
     setCaricamento(false);
    };
   } catch {
    setErrore('Qualcosa è andato storto. Riprova.');
    setCaricamento(false);
   }
  }

  return (
   <div className='fixed inset-0 z-50 flex items-center justify-center bg-black/70'>
    <div className='w-full max-w-md rounded-lg bg-gray-800 p-6 text-gray-100'>
     <h2 className='mb-2 text-xl font-bold text-purple-300'>
      Carica un manuale PDF
     </h2>
     <p className='mb-4 text-sm text-gray-400'>
      Scegli un PDF da indicizzare. L&apos;assistente risponderà basandosi su
      questo documento.
     </p>

     <input
      type='file'
      accept='application/pdf'
      onChange={(e) => setFile(e.target.files?.[0] ?? null)}
      disabled={caricamento}
      className='mb-4 block w-full text-sm text-gray-300 file:mr-3 file:rounded file:border-0 file:bg-purple-600 file:px-3 file:py-2 file:text-white hover:file:bg-purple-500'
     />

     {errore && <p className='mb-3 text-sm text-red-400'>{errore}</p>}

     {caricamento && (
      <div className='mb-3'>
       <div className='mb-1 flex justify-between text-xs text-gray-400'>
        <span>Indicizzazione in corso…</span>
        <span>{progresso}%</span>
       </div>
       <div className='h-2 w-full overflow-hidden rounded bg-gray-700'>
        <div
         className='h-full bg-purple-500 transition-all duration-300'
         style={{ width: `${progresso}%` }}
        />
       </div>
      </div>
     )}

     <button
      onClick={carica}
      disabled={!file || caricamento}
      className='w-full rounded bg-purple-600 px-4 py-2 font-medium text-white hover:bg-purple-500 disabled:opacity-50'
     >
      {caricamento ? 'Attendi…' : 'Carica e indicizza'}
     </button>
    </div>
   </div>
  );
}