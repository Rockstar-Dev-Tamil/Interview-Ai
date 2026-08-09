"use client";

import { useEffect, useRef, useState, memo } from "react";
import * as tf from "@tensorflow/tfjs";
import * as cocoSsd from "@tensorflow-models/coco-ssd";

export type FocusStatus = "INITIALIZING" | "READY" | "FOCUSED" | "ABSENT" | "DISTRACTED" | "ERROR" | "OFFLINE";

interface FocusCameraProps {
  onStatusChange?: (status: FocusStatus, message: string) => void;
}

export default memo(function FocusCamera({ onStatusChange }: FocusCameraProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [status, setStatus] = useState<FocusStatus>("OFFLINE");
  const [model, setModel] = useState<cocoSsd.ObjectDetection | null>(null);
  const [stream, setStream] = useState<MediaStream | null>(null);
  const requestRef = useRef<number>(0);

  useEffect(() => {
    if (model) {
      startCamera();
    }
  }, [model]);

  // Notify parent of status changes
  useEffect(() => {
    let message = "";
    switch (status) {
      case "INITIALIZING": message = "Initializing Neural Net..."; break;
      case "READY": message = "System Ready"; break;
      case "FOCUSED": message = "User Detected"; break;
      case "ABSENT": message = "Subject Absent!"; break;
      case "DISTRACTED": message = "Distraction Detected!"; break;
      case "ERROR": message = "Camera Error"; break;
      case "OFFLINE": message = "Proctoring Offline"; break;
    }
    onStatusChange?.(status, message);
  }, [status, onStatusChange]);

  // Load model once
  useEffect(() => {
    const loadModel = async () => {
      try {
        setStatus("INITIALIZING");
        
        // Attempt WebGL first, fallback to CPU
        try {
          await tf.setBackend('webgl');
          await tf.ready();
        } catch (e) {
          console.warn("WebGL failed, falling back to CPU", e);
          await tf.setBackend('cpu');
          await tf.ready();
        }

        const loadedModel = await cocoSsd.load();
        setModel(loadedModel);
        setStatus("READY");
      } catch (err) {
        console.error("Failed to load coco-ssd model", err);
        setStatus("ERROR");
      }
    };
    
    // We only load the model when the user enables it, or proactively if we want.
    // Let's load proactively so it's ready when they click "Enable".
    loadModel();
  }, []);

  const startCamera = async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { width: 320, height: 240 },
      });
      setStream(mediaStream);
      
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
        videoRef.current.onloadedmetadata = () => {
          videoRef.current?.play();
          if (canvasRef.current && videoRef.current) {
            canvasRef.current.width = videoRef.current.videoWidth;
            canvasRef.current.height = videoRef.current.videoHeight;
          }
          detectFrame();
        };
      }
    } catch (err) {
      console.error("Error accessing camera", err);
      setStatus("ERROR");
    }
  };

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach((track) => track.stop());
      setStream(null);
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    if (requestRef.current) {
      cancelAnimationFrame(requestRef.current);
    }
    setStatus("OFFLINE");
    
    // Clear canvas
    if (canvasRef.current) {
      const ctx = canvasRef.current.getContext("2d");
      if (ctx) {
        ctx.clearRect(0, 0, canvasRef.current.width, canvasRef.current.height);
      }
    }
  };

  const detectFrame = async () => {
    if (!videoRef.current || !canvasRef.current || !model) return;
    
    // Wait for video to have valid dimensions
    if (videoRef.current.readyState < 2) {
        requestRef.current = requestAnimationFrame(detectFrame);
        return;
    }

    try {
      const predictions = await model.detect(videoRef.current);
      
      const ctx = canvasRef.current.getContext("2d");
      if (ctx) {
        ctx.clearRect(0, 0, canvasRef.current.width, canvasRef.current.height);
        
        let personFound = false;
        let phoneDetected = false;

        predictions.forEach((prediction) => {
          // Draw boxes for persons or distractions
          if (prediction.score > 0.6) {
            if (prediction.class === "person") {
              personFound = true;
              
              // Draw cyan bracket style
              ctx.strokeStyle = "#00f3ff";
              ctx.shadowBlur = 10;
              ctx.shadowColor = "#00f3ff";
              ctx.lineWidth = 2;
              
              const [x, y, w, h] = prediction.bbox;
              ctx.strokeRect(x, y, w, h);
            } 
            else if (["cell phone", "laptop", "book"].includes(prediction.class)) {
              phoneDetected = true;
              
              // Draw red bracket style for distractions
              ctx.strokeStyle = "#ff2a2a";
              ctx.shadowBlur = 15;
              ctx.shadowColor = "#ff2a2a";
              ctx.lineWidth = 3;
              
              const [x, y, w, h] = prediction.bbox;
              ctx.strokeRect(x, y, w, h);
              
              ctx.fillStyle = "#ff2a2a";
              ctx.font = "16px monospace";
              ctx.fillText(prediction.class.toUpperCase(), x, y > 20 ? y - 5 : 20);
            }
          }
        });

        // Update status based on findings
        if (phoneDetected) {
          setStatus("DISTRACTED");
        } else if (personFound) {
          setStatus("FOCUSED");
        } else {
          setStatus("ABSENT");
        }
      }
    } catch (e) {
      // Ignore occasional detection errors from TFJS
    }

    // Continue loop
    setTimeout(() => {
        requestRef.current = requestAnimationFrame(detectFrame);
    }, 500); // 500ms between checks is enough for proctoring
  };
  
  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (stream) {
        stream.getTracks().forEach((track) => track.stop());
      }
      if (requestRef.current) {
        cancelAnimationFrame(requestRef.current);
      }
    };
  }, [stream]);

  return (
    <div className="flex flex-col gap-3 w-full mt-4">
      <div className="flex justify-between items-center">
        <h3 className="text-[10px] font-semibold text-text-tertiary uppercase tracking-wider">
          Proctoring Camera
        </h3>
        {status === "INITIALIZING" && <span className="text-[10px] text-primary animate-pulse">Initializing...</span>}
      </div>
      
      <div className={`relative w-full aspect-video bg-black rounded-lg overflow-hidden border ${
          status === "DISTRACTED" || status === "ABSENT" ? "border-red-500 shadow-[0_0_15px_rgba(239,68,68,0.5)]" : "border-primary/50"
      } transition-all duration-300 ${status === "INITIALIZING" ? "opacity-50" : ""}`}>
          <video
            ref={videoRef}
            className="absolute inset-0 w-full h-full object-cover transform scale-x-[-1]"
            playsInline
            muted
            autoPlay
          />
          <canvas
            ref={canvasRef}
            className="absolute inset-0 w-full h-full transform scale-x-[-1] z-10"
          />
          
          {/* Overlay scanning corners */}
          <div className="absolute inset-2 border-2 border-transparent pointer-events-none z-20 opacity-70"
               style={{
                   background: `
                       linear-gradient(to right, #00f3ff 2px, transparent 2px) 0 0,
                       linear-gradient(to bottom, #00f3ff 2px, transparent 2px) 0 0,
                       linear-gradient(to left, #00f3ff 2px, transparent 2px) 100% 0,
                       linear-gradient(to bottom, #00f3ff 2px, transparent 2px) 100% 0,
                       linear-gradient(to right, #00f3ff 2px, transparent 2px) 0 100%,
                       linear-gradient(to top, #00f3ff 2px, transparent 2px) 0 100%,
                       linear-gradient(to left, #00f3ff 2px, transparent 2px) 100% 100%,
                       linear-gradient(to top, #00f3ff 2px, transparent 2px) 100% 100%
                   `,
                   backgroundRepeat: "no-repeat",
                   backgroundSize: "20px 20px"
               }}
          />
        </div>
    </div>
  );
});
