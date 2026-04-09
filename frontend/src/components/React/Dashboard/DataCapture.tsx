import { useState, useRef, useEffect } from 'react';
import { apiFetch, getAppContext } from '../../../lib/api';

type ProcessResult = {
  monto: number;
  descripcion: string;
  sub_categoria_id?: number;
};

export default function DataCapture() {
  const [captureMode, setCaptureMode] = useState<'none' | 'camera' | 'audio' | 'text'>('none');
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const [textInput, setTextInput] = useState('');
  const [isCameraActive, setIsCameraActive] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isConfirming, setIsConfirming] = useState(false);
  const [result, setResult] = useState<ProcessResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<BlobPart[]>([]);
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const streamRef = useRef<MediaStream | null>(null);

  // Limpieza al desmontar o cancelar
  useEffect(() => {
    return () => {
      stopCamera();
      if (mediaRecorderRef.current && isRecording) {
        mediaRecorderRef.current.stop();
      }
    };
  }, [isRecording]);

  // Asignar el stream a la etiqueta de video una vez que se renderice
  useEffect(() => {
    if (isCameraActive && videoRef.current && streamRef.current) {
      videoRef.current.srcObject = streamRef.current;
    }
  }, [isCameraActive, captureMode]);

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
    setIsCameraActive(false);
  };

  // --- Funciones para la Cámara ---
  const handleCameraClick = async () => {
    try {
      // Pedir permisos y obtener stream de video (preferencia de cámara trasera)
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { facingMode: 'environment' } 
      });
      streamRef.current = stream;
      setIsCameraActive(true);
      setCaptureMode('camera');
    } catch (err) {
      console.error('Error al acceder a la cámara:', err);
      // Fallback: Si no hay permisos o no hay cámara soportada, usar el input de archivos nativo
      fileInputRef.current?.click();
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setImageFile(e.target.files[0]);
      setCaptureMode('camera');
    }
  };

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const capturePhoto = () => {
    if (videoRef.current && canvasRef.current) {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const context = canvas.getContext('2d');
      
      if (context) {
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        canvas.toBlob((blob) => {
          if (blob) {
            const file = new File([blob], "captura.jpg", { type: "image/jpeg" });
            setImageFile(file);
            stopCamera(); // Apagar la cámara web después de tomar la foto
          }
        }, 'image/jpeg');
      }
    }
  };

  // --- Funciones para el Micrófono ---
  const handleAudioClick = async () => {
    if (isRecording) {
      // Detener grabación
      mediaRecorderRef.current?.stop();
      setIsRecording(false);
    } else {
      // Iniciar grabación
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const mediaRecorder = new MediaRecorder(stream);
        mediaRecorderRef.current = mediaRecorder;
        audioChunksRef.current = [];

        mediaRecorder.ondataavailable = (e) => {
          if (e.data.size > 0) audioChunksRef.current.push(e.data);
        };

        mediaRecorder.onstop = () => {
          const blob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
          setAudioBlob(blob);
          stream.getTracks().forEach((track) => track.stop()); // Apagar el micrófono
        };

        mediaRecorder.start();
        setIsRecording(true);
        setCaptureMode('audio');
      } catch (err) {
        console.error('Error al acceder al micrófono:', err);
        alert('No se pudo acceder al micrófono para grabar.');
      }
    }
  };

  // --- Funciones para el Texto ---
  const handleTextClick = () => setCaptureMode('text');

  // --- Resetear estados ---
  const resetCapture = () => {
    setCaptureMode('none');
    setImageFile(null);
    setAudioBlob(null);
    setTextInput('');
    setResult(null);
    setError(null);
    stopCamera();
    if (isRecording && mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  // --- Llamadas a la API ---
  const processCapture = async () => {
    setIsProcessing(true);
    setError(null);
    try {
      const token = await (window as any).Clerk?.session?.getToken() as string | null;
      const authHeader: Record<string, string> = token ? { Authorization: `Bearer ${token}` } : {};
      let response: Response;

      if (captureMode === 'text') {
        response = await fetch('/api/upload/texto', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', ...authHeader },
          body: JSON.stringify({ texto: textInput }),
        });
      } else if (captureMode === 'audio' && audioBlob) {
        const formData = new FormData();
        formData.append('file', audioBlob, 'audio.webm');
        response = await fetch('/api/upload/audio', { method: 'POST', headers: authHeader, body: formData });
      } else if (captureMode === 'camera' && imageFile) {
        const formData = new FormData();
        formData.append('file', imageFile);
        response = await fetch('/api/upload/imagen', { method: 'POST', headers: authHeader, body: formData });
      } else {
        return;
      }

      if (!response.ok) {
        const text = await response.text();
        throw new Error(text || `Error ${response.status}`);
      }

      const data: ProcessResult = await response.json();
      setResult(data);
    } catch (err: any) {
      setError(err.message ?? 'Error al procesar. Intenta de nuevo.');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="card-base h-full flex flex-col items-center justify-center text-center space-y-8 shadow-(--shadow-ambient)">
      <h2 className="text-2xl font-display font-bold text-primary">
        ¿Qué movimiento hiciste hoy?
      </h2>
      
      {/* Input de archivo oculto para subir imágenes */}
      <input
        type="file"
        accept="image/*"
        ref={fileInputRef}
        onChange={handleFileChange}
        className="hidden"
      />

      {/* Estado Inicial: Botones de Captura */}
      {captureMode === 'none' && (
        <div className="flex items-center justify-center gap-4 sm:gap-6 animate-in fade-in zoom-in duration-300">
          <button onClick={handleCameraClick} className="p-4 rounded-full bg-(--color-surface-container-high) text-on-surface hover:scale-105 transition-transform" aria-label="Escanear recibo">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
          </button>

          <button onClick={handleAudioClick} className="p-6 rounded-full bg-secondary text-white animate-pulse hover:scale-110 transition-transform shadow-(--shadow-ambient)" aria-label="Grabar audio">
            <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" /></svg>
          </button>

          <button onClick={handleTextClick} className="p-4 rounded-full bg-(--color-surface-container-high) text-on-surface hover:scale-105 transition-transform" aria-label="Ingreso manual">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" /></svg>
          </button>
        </div>
      )}

      {/* Estado: Captura de Texto */}
      {captureMode === 'text' && (
        <div className="w-full space-y-4 animate-in fade-in duration-300">
          <textarea
            className="input-field min-h-30 resize-none border-outline-variant/30 border"
            placeholder="Ej: Gasté $400 en gasolina..."
            value={textInput}
            onChange={(e) => setTextInput(e.target.value)}
            autoFocus
          />
          <div className="flex gap-4 justify-center mt-2">
            <button onClick={resetCapture} className="btn-secondary text-sm px-6 py-2">Cancelar</button>
            <button onClick={processCapture} className="btn-primary text-sm px-6 py-2" disabled={!textInput || isProcessing}>
              {isProcessing ? 'Procesando...' : 'Procesar'}
            </button>
          </div>
        </div>
      )}

      {/* Estado: Cámara - Vista Previa o En vivo */}
      {captureMode === 'camera' && (
        <div className="w-full space-y-4 animate-in fade-in duration-300 flex flex-col items-center">
          {isCameraActive ? (
            <>
              <div className="w-full max-w-75 rounded-xl overflow-hidden border border-outline-variant/30 relative shadow-sm bg-black">
                <video ref={videoRef} autoPlay playsInline className="object-cover w-full h-full min-h-62.5" />
                <canvas ref={canvasRef} className="hidden" />
              </div>
              <div className="flex gap-6 justify-center items-center mt-4">
                <button onClick={resetCapture} className="p-4 rounded-full bg-(--color-surface-container-high) text-on-surface hover:scale-105 transition-transform" aria-label="Cancelar" title="Cancelar">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
                </button>
                <button onClick={capturePhoto} className="p-5 rounded-full bg-primary text-white hover:scale-110 transition-transform shadow-(--shadow-ambient)" aria-label="Tomar Foto" title="Tomar Foto">
                  <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" fill="none"/><circle cx="12" cy="12" r="6"/></svg>
                </button>
                <button onClick={handleUploadClick} className="p-4 rounded-full bg-(--color-surface-container-high) text-on-surface hover:scale-105 transition-transform" aria-label="Subir imagen desde galería" title="Subir desde galería">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>
                </button>
              </div>
            </>
          ) : imageFile ? (
            <>
              <div className="w-full max-w-55 h-55 rounded-xl overflow-hidden border border-outline-variant/30 relative shadow-sm">
                <img src={URL.createObjectURL(imageFile)} alt="Recibo capturado" className="object-cover w-full h-full" />
              </div>
              <div className="flex gap-6 justify-center items-center mt-4">
                <button onClick={resetCapture} className="p-4 rounded-full bg-(--color-surface-container-high) text-on-surface hover:scale-105 transition-transform" aria-label="Descartar recibo" title="Descartar recibo">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                </button>
                <button onClick={processCapture} disabled={isProcessing} className="p-5 rounded-full bg-primary text-white hover:scale-110 transition-transform shadow-(--shadow-ambient) disabled:opacity-50 disabled:cursor-not-allowed" aria-label="Procesar recibo" title="Procesar recibo">
                  {isProcessing
                    ? <svg className="w-8 h-8 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v3m0 12v3m9-9h-3M6 12H3m15.364-6.364l-2.121 2.121M8.757 15.243l-2.121 2.121M18.364 18.364l-2.121-2.121M8.757 8.757L6.636 6.636" /></svg>
                    : <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" /></svg>
                  }
                </button>
              </div>
            </>
          ) : null}
        </div>
      )}

      {/* Estado: Audio - Grabando o Reproduciendo */}
      {captureMode === 'audio' && (
        <div className="w-full space-y-4 animate-in fade-in duration-300 flex flex-col items-center">
          {isRecording ? (
            <div className="space-y-4 flex flex-col items-center">
              <div className="w-16 h-16 rounded-full bg-red-500 text-white flex items-center justify-center animate-pulse shadow-lg shadow-red-500/30">
                <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2a3 3 0 00-3 3v7a3 3 0 006 0V5a3 3 0 00-3-3z"/><path d="M19 10v2a7 7 0 01-14 0v-2H3v2a9 9 0 008 8.94V22h2v-2.06A9 9 0 0021 12v-2h-2z"/></svg>
              </div>
              <p className="text-on-surface/60 font-medium animate-pulse">Grabando tu voz...</p>
              <button onClick={handleAudioClick} className="btn-secondary text-sm px-6 py-2 bg-red-50! text-red-600! hover:bg-red-100! mt-2">Detener Grabación</button>
            </div>
          ) : audioBlob ? (
            <div className="space-y-4 w-full flex flex-col items-center">
              <audio controls src={URL.createObjectURL(audioBlob)} className="w-full max-w-70" />
              <div className="flex gap-6 justify-center items-center mt-4">
                <button onClick={resetCapture} className="p-4 rounded-full bg-(--color-surface-container-high) text-on-surface hover:scale-105 transition-transform" aria-label="Descartar audio" title="Descartar audio">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                </button>
                <button onClick={processCapture} disabled={isProcessing} className="p-5 rounded-full bg-primary text-white hover:scale-110 transition-transform shadow-(--shadow-ambient) disabled:opacity-50 disabled:cursor-not-allowed" aria-label="Procesar audio" title="Procesar audio">
                  {isProcessing
                    ? <svg className="w-8 h-8 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v3m0 12v3m9-9h-3M6 12H3m15.364-6.364l-2.121 2.121M8.757 15.243l-2.121 2.121M18.364 18.364l-2.121-2.121M8.757 8.757L6.636 6.636" /></svg>
                    : <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" /></svg>
                  }
                </button>
              </div>
            </div>
          ) : null}
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="w-full rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600 flex items-start gap-2">
          <svg className="w-4 h-4 mt-0.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
          <span>{error}</span>
        </div>
      )}

      {/* Resultado extraído */}
      {result && (
        <div className="w-full space-y-4">
          <div className="rounded-2xl border border-outline-variant/30 bg-(--color-surface-container-low) p-5 space-y-3 text-left">
            <p className="text-xs font-bold uppercase tracking-wider text-on-surface/40">Transacción detectada</p>
            <div className="flex items-end justify-between gap-4">
              <div>
                <p className="text-sm text-on-surface/60">Descripción</p>
                <p className="font-semibold text-on-surface">{result.descripcion}</p>
              </div>
              <div className="text-right shrink-0">
                <p className="text-sm text-on-surface/60">Monto</p>
                <p className="text-2xl font-extrabold text-secondary">
                  {new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN' }).format(result.monto)}
                </p>
              </div>
            </div>
          </div>
          <div className="flex gap-4 justify-center">
            <button onClick={resetCapture} className="btn-secondary text-sm px-6 py-2">Descartar</button>
            <button
              onClick={async () => {
                if (!result) return;
                setIsConfirming(true);
                try {
                  const { cuentaId, tenantId } = await getAppContext();
                  await apiFetch('/transacciones/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                      monto: result.monto,
                      fecha_operacion: new Date().toISOString(),
                      descripcion: result.descripcion,
                      cuenta_id: cuentaId,
                      sub_categoria_id: result.sub_categoria_id ?? 1,
                      tenant_id: tenantId,
                    }),
                  });
                  resetCapture();
                } catch (err: any) {
                  setError(err.message);
                } finally {
                  setIsConfirming(false);
                }
              }}
              disabled={isConfirming}
              className="btn-primary text-sm px-6 py-2"
            >
              {isConfirming ? 'Guardando...' : 'Confirmar'}
            </button>
          </div>
        </div>
      )}

    </div>
  );
}