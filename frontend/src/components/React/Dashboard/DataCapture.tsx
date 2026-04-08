export default function DataCapture() {
  return (
    <div className="card-base h-full flex flex-col items-center justify-center text-center space-y-8 shadow-(--shadow-ambient)">
      <h2 className="text-2xl font-display font-bold text-primary">
        ¿Qué movimiento hiciste hoy?
      </h2>
      
      <div className="flex items-center justify-center gap-6">
        {/* Left: Camera Button */}
        <button className="p-4 rounded-full bg-(--color-surface-container-high) text-on-surface hover:scale-105 transition-transform" aria-label="Escanear recibo">
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
        </button>

        {/* Middle: Microphone Button (Bigger, Primary Green, Pulsating) */}
        <button className="p-6 rounded-full bg-secondary text-white animate-pulse hover:scale-110 transition-transform shadow-(--shadow-ambient)" aria-label="Grabar audio">
          <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
          </svg>
        </button>

        {/* Right: Keyboard Button */}
        <button className="p-4 rounded-full bg-(--color-surface-container-high) text-on-surface hover:scale-105 transition-transform" aria-label="Ingreso manual">
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
          </svg>
        </button>
      </div>
    </div>
  );
}