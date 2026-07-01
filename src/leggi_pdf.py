from pypdf import PdfReader

#Apro il pdf

lettore = PdfReader("documenti/lancer.pdf")

#Quante pagine ha?
print(f"Il PDF ha {len(lettore.pages)} pagine.")


#estraggo tutto il testo e lo accumulo
testo_completo = ""

for pagina in lettore.pages:
    testo_completo += pagina.extract_text()
    
#QUanto testo abbiamo raccolto ?
print(f"Estratti {len(testo_completo)} caratteri in totale\n")

#controlliamo i primi 500 caratteri
print(testo_completo[:500])