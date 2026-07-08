'use client';

import { useState, useEffect } from 'react';
import UploadModal from './components/UploadModal';
type Messaggio = {
 ruolo: 'utente' | 'assistente';
 testo: string;
};

export default function Home() {
 const [messaggi, setMessaggi] = useState<Messaggio[]>([]);
 const [input, setInput] = useState('');
 const [caricamento, setCaricamento] = useState(false);
 const [prontoPerChat, setProntoPerChat] = useState(false);
 const [verificaIniziale, setVerificaIniziale] = useState(true);

 useEffect(() => {
  async function controllaIndice() {
   try {
    const res = await fetch('http://localhost:8000/stato');
    const dati = await res.json();
    if (dati.indice_presente) {
     setProntoPerChat(true);
    }
   } catch {
    // Se il backend non risponde, restiamo sulla modale.
   } finally {
    setVerificaIniziale(false);
   }
  }

  controllaIndice();
 }, []);

 async function invia() {
  if (!input.trim()) return;

  const domanda = input;
  setInput('');
  setMessaggi((prev) => [...prev, { ruolo: 'utente', testo: domanda }]);
  setCaricamento(true);

  try {
   const res = await fetch('http://localhost:8000/chiedi', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ testo: domanda }),
   });
   const dati = await res.json();
   setMessaggi((prev) => [
    ...prev,
    { ruolo: 'assistente', testo: dati.risposta },
   ]);
  } catch {
   setMessaggi((prev) => [
    ...prev,
    { ruolo: 'assistente', testo: 'Errore: il backend risponde?' },
   ]);
  } finally {
   setCaricamento(false);
  }
 }

 return (
  <div className='flex h-screen justify-center bg-gray-900 text-gray-100'>
   {!verificaIniziale && !prontoPerChat && (
    <UploadModal onCompletato={() => setProntoPerChat(true)} />
   )}

   <main className='flex w-full max-w-3xl flex-col px-6 py-6'>
    <div className='mb-4 flex items-center justify-between'>
     <h1 className='text-2xl font-bold text-purple-300'>Arcane famAIliar 🔮</h1>
     <button
      onClick={() => setProntoPerChat(false)}
      className='rounded border border-gray-600 px-3 py-1 text-sm text-gray-300 hover:bg-gray-800'
     >
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
      </div>
     ))}
     {caricamento && <div className='text-gray-400'>Sto pensando…</div>}
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
