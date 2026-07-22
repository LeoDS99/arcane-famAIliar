'use client';

import { useState, useEffect } from 'react';
import UploadModal from './UploadModal';

const URL_BACKEND = 'http://localhost:8000';

type Documento = {
 nome: string;
 indicizzato: boolean;
};

type Props = {
 documentoAttivo: string | null;
 chiudibile: boolean;
 onAttivato: () => void;
 onAnnulla: () => void;
};

export default function LibreriaModal({
 documentoAttivo,
 chiudibile,
 onAttivato,
 onAnnulla,
}: Props) {
 const [documenti, setDocumenti] = useState<Documento[]>([]);
 const [errore, setErrore] = useState('');
 const [mostraUpload, setMostraUpload] = useState(false);
const [indicizzando, setIndicizzando] = useState<string | null>(null);
const [progresso, setProgresso] = useState(0);
async function caricaLista() {
 try {
  const res = await fetch(`${URL_BACKEND}/documenti`);
  const dati = await res.json();
  setDocumenti(dati.documenti);
 } catch {
  setErrore('Impossibile caricare la libreria.');
 }
}

useEffect(() => {
 caricaLista();
}, []);

async function attiva(nome: string) {
 setErrore('');
 try {
  const res = await fetch(
   `${URL_BACKEND}/attiva?nome=${encodeURIComponent(nome)}`,
   { method: 'POST' },
  );
  if (!res.ok) {
   const dati = await res.json();
   setErrore(dati.detail ?? "Errore durante l'attivazione.");
   return;
  }
  onAttivato();
 } catch {
  setErrore('Impossibile contattare il server.');
 }
}

async function elimina(nome: string, evento: React.MouseEvent) {
 evento.stopPropagation();
 setErrore('');
 try {
  const res = await fetch(
   `${URL_BACKEND}/documenti/${encodeURIComponent(nome)}`,
   { method: 'DELETE' },
  );
  if (!res.ok) {
   setErrore('Impossibile eliminare il documento.');
   return;
  }
  caricaLista();
 } catch {
  setErrore('Impossibile contattare il server.');
 }
}

function indicizza(nome: string) {
 setErrore('');
 setIndicizzando(nome);
 setProgresso(0);

 const sorgente = new EventSource(
  `${URL_BACKEND}/indicizza-stream?nome=${encodeURIComponent(nome)}`,
 );

 sorgente.onmessage = (evento) => {
  const dati = JSON.parse(evento.data);

  if (dati.completato) {
   sorgente.close();
   setIndicizzando(null);
   onAttivato();
   return;
  }

  setProgresso(Math.round((dati.fatti / dati.totale) * 100));
 };

 sorgente.onerror = () => {
  sorgente.close();
  setIndicizzando(null);
  setErrore("Errore durante l'indicizzazione. Riprova.");
 };
}

if (mostraUpload) {
 return (
  <UploadModal
   chiudibile={true}
   onAnnulla={() => setMostraUpload(false)}
   onCompletato={onAttivato}
  />
 );
}

return (
 <div className='fixed inset-0 z-50 flex items-center justify-center bg-black/70'>
  <div className='w-full max-w-md rounded-lg bg-gray-800 p-6 text-gray-100'>
   <h2 className='mb-4 text-xl font-bold text-purple-300'>I tuoi documenti</h2>

   {errore && <p className='mb-3 text-sm text-red-400'>{errore}</p>}

   {documenti.length === 0 ? (
    <p className='mb-4 text-sm text-gray-400'>
     Nessun documento. Caricane uno per iniziare.
    </p>
   ) : (
    <ul className='mb-4 space-y-2'>
     {documenti.map((d) => (
      <li key={d.nome} className='flex items-center gap-2'>
       <button
        onClick={() => (d.indicizzato ? attiva(d.nome) : indicizza(d.nome))}
        disabled={indicizzando !== null}
        className={
         'flex flex-1 items-center justify-between rounded border px-3 py-2 text-left text-sm transition-colors ' +
         (d.nome === documentoAttivo
          ? 'border-purple-500 bg-purple-600/20 text-purple-200'
          : d.indicizzato
            ? 'border-gray-600 text-gray-200 hover:border-purple-500'
            : 'border-gray-700 text-gray-500')
        }
       >
        <span className='truncate'>{d.nome}</span>
        <span className='ml-2 shrink-0 text-xs'>
         {indicizzando === d.nome
          ? `${progresso}%`
          : d.nome === documentoAttivo
            ? '● attivo'
            : d.indicizzato
              ? 'pronto'
              : 'da indicizzare'}
        </span>
       </button>
       <button
        onClick={(e) => elimina(d.nome, e)}
        disabled={indicizzando !== null}
        className='shrink-0 rounded border border-gray-700 p-2 text-gray-500 hover:border-red-500 hover:text-red-400'
        title='Elimina'
       >
        ✕
       </button>
      </li>
     ))}
    </ul>
   )}

   <div className='flex gap-2'>
    {chiudibile && (
     <button
      onClick={onAnnulla}
      className='flex-1 rounded border border-gray-600 px-4 py-2 font-medium text-gray-300 hover:bg-gray-700'
     >
      Chiudi
     </button>
    )}
    <button
     onClick={() => setMostraUpload(true)}
     className='flex-1 rounded bg-purple-600 px-4 py-2 font-medium text-white hover:bg-purple-500'
    >
     Carica nuovo
    </button>
   </div>
  </div>
 </div>
);
}