from pypdf import PdfReader

#Apro il pdf

lettore = PdfReader("documenti/lancer.pdf")

#Quante pagine ha?
print(f"Il PDF ha {len(lettore.pages)} pagine.")


#estraggo il testo dalla prima pagina

prima_pagina = lettore.pages[0]
testo = prima_pagina.extract_text()


#stampo i primi 500 caratteri
print(testo[:500])