// Configurazione dell'account (Firebase). Le chiavi di un'app web Firebase sono pubbliche
// per progetto: a proteggere i dati sono l'accesso con account e le regole di Firestore.
// Finche' qui sotto resta null, il Diario funziona senza account, solo su questo dispositivo.
//
// Per attivare l'account incolla qui l'oggetto che Firebase mostra in
// Impostazioni progetto -> Le tue app -> App web -> Configurazione SDK, per esempio:
// window.TDF_FIREBASE = {
//   apiKey: "AIza...",
//   authDomain: "nome-progetto.firebaseapp.com",
//   projectId: "nome-progetto",
//   appId: "1:123456789:web:abcdef"
// };
window.TDF_FIREBASE = null;
