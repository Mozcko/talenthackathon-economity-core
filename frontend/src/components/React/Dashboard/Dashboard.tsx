import { useState, useEffect, useRef } from 'react';
import rudySad from '../../../assets/rudy_sad.png';
import rudyAngry from '../../../assets/rudy_angry.jpeg';
import rudyHappy from '../../../assets/rudy_happy.png';
import DataCapture from './DataCapture';

export default function Dashboard() {
  // --- Rudy Face Rotation Logic ---
  const faces = [rudySad, rudyAngry, rudyHappy];
  const [faceIndex, setFaceIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setFaceIndex((prev) => (prev + 1) % faces.length);
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  // --- Voice Detection Chunk (ported/kept) ---
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<BlobPart[]>([]);

  const handleAudioClick = async () => {
    if (isRecording) {
      mediaRecorderRef.current?.stop();
      setIsRecording(false);
    } else {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const mediaRecorder = new MediaRecorder(stream);
        mediaRecorderRef.current = mediaRecorder;
        audioChunksRef.current = [];

        mediaRecorder.ondataavailable = (e) => {
          if (e.data.size > 0) audioChunksRef.current.push(e.data);
        };

        mediaRecorder.onstop = () => {
          stream.getTracks().forEach((track) => track.stop());
        };

        mediaRecorder.start();
        setIsRecording(true);
      } catch (err) {
        console.error('Error al acceder al micrófono:', err);
      }
    }
  };

  return (
    <div className="h-full flex flex-col items-center justify-center p-6 space-y-12">
      {/* Rudy Presentation Layer */}
      <div className="relative flex flex-col items-center">
        
        {/* Speech Bubble */}
        <div className="mb-8 relative animate-in fade-in slide-in-from-bottom-4 duration-700">
          <div className="bg-surface-container-lowest p-6 rounded-3xl shadow-ambient border border-outline-variant/20 max-w-sm">
            <p className="text-on-surface text-lg font-display font-bold leading-tight">
              ¡Hola! Soy Rudy. <br />
              <span className="text-secondary">¿Qué movimiento financiero registramos hoy?</span>
            </p>
          </div>
          {/* Speech Bubble Tail */}
          <div className="absolute -bottom-2 left-1/2 -translate-x-1/2 w-6 h-6 bg-surface-container-lowest rotate-45 border-b border-r border-outline-variant/20 shadow-[4px_4px_10px_rgba(0,0,0,0.02)]"></div>
        </div>

        {/* Rudy Animated Face */}
        <div className="w-56 h-56 rounded-full overflow-hidden border-8 border-white shadow-ambient bg-surface-container-high transition-transform hover:scale-105 duration-500">
          <img 
            src={typeof faces[faceIndex] === 'string' ? faces[faceIndex] : (faces[faceIndex] as any).src} 
            alt="Rudy Face" 
            className="w-full h-full object-cover transition-opacity duration-500"
          />
        </div>
      </div>

    </div>
  );
}
