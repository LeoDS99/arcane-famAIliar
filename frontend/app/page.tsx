'use client';

import { useState, useEffect } from 'react';
import LibreriaModal from './components/LibreriaModal';

type Fonte = {
 punteggio: number;
 testo: string;
};

type Messaggio = {
 ruolo: 'utente' | 'assistente';
 testo: string;
 fonti?: Fonte[];
};

export default function Home() {
 const [messaggi, setMessaggi] = useState<Messaggio[]>([]);
 const [input, setInput] = useState('');
 const [caricamento, setCaricamento] = useState(false);
 const [prontoPerChat, setProntoPerChat] = useState(false);
 const [verificaIniziale, setVerificaIniziale] = useState(true);
 const [documentoAttivo, setDocumentoAttivo] = useState<string | null>(null);
 useEffect(() => {
  // Piccola utility: aspetta 'ms' millisecondi.
  const aspetta = (ms: number) =>
   new Promise((resolve) => setTimeout(resolve, ms));

  async function controllaIndice() {
   const MAX_TENTATIVI = 5;
   const PAUSA_MS = 1000;

   for (let tentativo = 1; tentativo <= MAX_TENTATIVI; tentativo++) {
    try {
     const res = await fetch('http://localhost:8000/stato');
     const dati = await res.json();

     if (dati.indice_presente) {
      setProntoPerChat(true);
      setDocumentoAttivo(dati.documento);
     }
     // Il backend ha risposto: usciamo dal ciclo di retry.
     setVerificaIniziale(false);
     return;
    } catch {
     // Il backend non risponde ancora: aspetto e riprovo,
     // a meno che sia l'ultimo tentativo.
     if (tentativo < MAX_TENTATIVI) {
      await aspetta(PAUSA_MS);
     }
    }
   }

   // Esauriti i tentativi senza risposta: mostro la modale.
   setVerificaIniziale(false);
  }

  controllaIndice();
 }, []);

 function invia() {
  if (!input.trim()) return;

  const domanda = input;
  setInput('');
  setMessaggi((prev) => [...prev, { ruolo: 'utente', testo: domanda }]);
  setCaricamento(true);

  // Aggiungo subito una bolla vuota per l'assistente, che riempirò man mano.
  setMessaggi((prev) => [...prev, { ruolo: 'assistente', testo: '' }]);

  const sorgente = new EventSource(
   `http://localhost:8000/chiedi-stream?domanda=${encodeURIComponent(domanda)}`,
  );

  sorgente.onmessage = (evento) => {
   const dati = JSON.parse(evento.data);

   if (dati.completato) {
    sorgente.close();
    setCaricamento(false);
    return;
   }
   // Le fonti arrivano per prime: le attacco alla bolla dell'assistente.
   if (dati.fonti) {
    setMessaggi((prev) => {
     const aggiornati = [...prev];
     const ultimo = aggiornati[aggiornati.length - 1];
     aggiornati[aggiornati.length - 1] = { ...ultimo, fonti: dati.fonti };
     return aggiornati;
    });
    return;
   }
   // Appendo il frammento all'ultimo messaggio (la bolla dell'assistente).
   setMessaggi((prev) => {
    const aggiornati = [...prev];
    const ultimo = aggiornati[aggiornati.length - 1];
    aggiornati[aggiornati.length - 1] = {
     ...ultimo,
     testo: ultimo.testo + dati.frammento,
    };
    return aggiornati;
   });
  };

  sorgente.onerror = () => {
   sorgente.close();
   setCaricamento(false);
  };
 }

 return (
  <div className='flex h-screen justify-center bg-gray-900 text-gray-100'>
   {!verificaIniziale && !prontoPerChat && (
    <LibreriaModal
     documentoAttivo={documentoAttivo}
     chiudibile={documentoAttivo !== null}
     onAnnulla={() => setProntoPerChat(true)}
     onAttivato={async () => {
      // Dopo attivazione/upload, rileggo lo stato e entro in chat.
      const res = await fetch('http://localhost:8000/stato');
      const dati = await res.json();
      setDocumentoAttivo(dati.documento);
      setProntoPerChat(true);
     }}
    />
   )}

   <main className='flex w-full max-w-3xl flex-col px-6 py-6'>
    <div className='mb-4 flex items-center justify-between'>
     <h1 className='text-2xl font-bold text-purple-300'>Arcane famAIliar 🔮</h1>
     <button
      onClick={() => setProntoPerChat(false)}
      className='flex items-center gap-2 rounded-lg border border-gray-700 bg-gray-800/50 px-4 py-2 text-sm font-medium text-gray-300 transition-colors hover:border-purple-500 hover:text-purple-300'
     >
      <svg
       xmlns='http://www.w3.org/2000/svg'
       fill='none'
       viewBox='0 0 24 24'
       strokeWidth={1.5}
       stroke='currentColor'
       className='h-4 w-4'
      >
       <path
        strokeLinecap='round'
        strokeLinejoin='round'
        d='M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5M16.5 12 12 16.5m0 0L7.5 12m4.5 4.5V3'
       />
      </svg>
      Cambia PDF
     </button>
    </div>

    <div className='flex-1 space-y-3 overflow-y-auto'>
     {messaggi.map((m, i) => (
      <div
       key={i}
       className={m.ruolo === 'utente' ? 'text-right' : 'text-left'}
      >
       <span
        className={
         'inline-block max-w-[80%] rounded-lg px-3 py-2 text-left ' +
         (m.ruolo === 'utente'
          ? 'bg-purple-600 text-white'
          : 'bg-gray-700 text-gray-100')
        }
       >
        {m.testo}
       </span>

       {m.fonti && m.testo !== '' && (
        <details className='mt-1 max-w-[80%] text-xs text-gray-500'>
         <summary className='cursor-pointer hover:text-purple-400'>
          Fonti ({m.fonti.length})
         </summary>
         <div className='mt-2 space-y-2'>
          {m.fonti.map((f, j) => (
           <div key={j} className='rounded border border-gray-700 p-2'>
            <div className='mb-1 font-mono text-purple-400'>
             rilevanza {(f.punteggio * 100).toFixed(0)}%
            </div>
            <p className='text-gray-400'>{f.testo.slice(0, 200)}…</p>
           </div>
          ))}
         </div>
        </details>
       )}
      </div>
     ))}
     {caricamento && messaggi[messaggi.length - 1]?.testo === '' && (
      <div className='text-gray-400'>Sto pensando…</div>
     )}
    </div>

    <div className='mt-4 flex gap-2'>
     <input
      className='flex-1 rounded border border-gray-600 bg-gray-800 px-3 py-2 text-gray-100 placeholder-gray-400'
      value={input}
      onChange={(e) => setInput(e.target.value)}
      onKeyDown={(e) => e.key === 'Enter' && invia()}
      placeholder='Scrivi la tua domanda qui…'
     />
     <button
      onClick={invia}
      disabled={caricamento}
      className='rounded bg-purple-600 px-4 py-2 font-medium text-white hover:bg-purple-500 disabled:opacity-50'
     >
      Invia
     </button>
    </div>
   </main>
  </div>
 );
}
