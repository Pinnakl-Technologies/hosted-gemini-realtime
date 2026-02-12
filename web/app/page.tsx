'use client';

import { useState } from 'react';
import { LiveKitRoom, RoomAudioRenderer, useVoiceAssistant, useLocalParticipant } from '@livekit/components-react';
import '@livekit/components-styles';

function VoiceInterface() {
    const { state, audioTrack } = useVoiceAssistant();
    const { localParticipant } = useLocalParticipant();
    const [isMuted, setIsMuted] = useState(false);

    const toggleMute = async () => {
        if (localParticipant) {
            const newMutedState = !isMuted;
            await localParticipant.setMicrophoneEnabled(!newMutedState);
            setIsMuted(newMutedState);
        }
    };

    const isConnected = state === 'listening' || state === 'speaking' || state === 'thinking';

    return (
        <div className="relative flex flex-col items-center justify-center min-h-screen p-4 overflow-hidden">
            {/* Background Image with Overlay */}
            <div
                className="absolute inset-0 bg-cover bg-center bg-no-repeat"
                style={{
                    backgroundImage: 'url(/images/mithai-background.png)',
                    filter: 'brightness(0.7)'
                }}
            />

            {/* Gradient Overlay for better readability */}
            <div className="absolute inset-0 bg-gradient-to-br from-amber-900/40 via-orange-800/30 to-rose-900/40" />

            {/* Glassmorphism Card */}
            <div className="relative bg-white/10 backdrop-blur-xl rounded-3xl shadow-2xl p-8 w-full max-w-md border border-white/20">
                {/* Header */}
                <div className="text-center mb-8">
                    <h1 className="text-4xl font-bold text-white mb-2 drop-shadow-lg" style={{ fontFamily: 'Georgia, serif' }}>
                        رحمتِ شیریں
                    </h1>
                    <p className="text-amber-100 text-lg font-medium">Voice Assistant</p>
                </div>

                {/* Status Indicator */}
                <div className="flex items-center justify-center mb-8 bg-white/20 backdrop-blur-sm rounded-full py-3 px-6">
                    <div className={`w-4 h-4 rounded-full mr-3 ${isConnected ? 'bg-green-400 animate-pulse shadow-lg shadow-green-400/50' : 'bg-gray-400'
                        }`} />
                    <span className="text-sm font-semibold text-white">
                        {state === 'speaking' && '🗣️ Speaking...'}
                        {state === 'listening' && '👂 Listening...'}
                        {state === 'thinking' && '💭 Processing...'}
                        {state === 'idle' && '✨ Ready'}
                        {state === 'disconnected' && '⚠️ Disconnected'}
                    </span>
                </div>

                {/* Microphone Toggle */}
                <div className="flex justify-center mb-6">
                    <button
                        onClick={toggleMute}
                        disabled={!isConnected}
                        className={`p-8 rounded-full transition-all transform hover:scale-110 ${isMuted
                            ? 'bg-red-500 hover:bg-red-600 shadow-lg shadow-red-500/50'
                            : 'bg-gradient-to-br from-emerald-400 to-teal-500 hover:from-emerald-500 hover:to-teal-600 shadow-lg shadow-emerald-500/50'
                            } ${!isConnected && 'opacity-50 cursor-not-allowed'}`}
                    >
                        <svg
                            className="w-10 h-10 text-white drop-shadow-lg"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                        >
                            {isMuted ? (
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth={2}
                                    d="M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z"
                                />
                            ) : (
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth={2}
                                    d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
                                />
                            )}
                        </svg>
                    </button>
                </div>

                {/* Connection Info */}
                <div className="text-center text-sm text-amber-100 font-medium bg-white/10 backdrop-blur-sm rounded-full py-2 px-4">
                    {isConnected ? '🔗 Connected to agent' : '📞 Click call button to start'}
                </div>
            </div>

            <RoomAudioRenderer />
        </div>
    );
}

export default function Home() {
    const [token, setToken] = useState<string>('');
    const [isConnecting, setIsConnecting] = useState(false);
    const [isInCall, setIsInCall] = useState(false);

    const startCall = async () => {
        setIsConnecting(true);
        try {
            const response = await fetch('/api/token');
            const data = await response.json();
            setToken(data.token);
            setIsInCall(true);
        } catch (error) {
            console.error('Failed to start call:', error);
            alert('Failed to connect. Please try again.');
        } finally {
            setIsConnecting(false);
        }
    };

    const endCall = () => {
        setToken('');
        setIsInCall(false);
    };

    if (!isInCall) {
        return (
            <div className="relative flex flex-col items-center justify-center min-h-screen p-4 overflow-hidden">
                {/* Background Image with Overlay */}
                <div
                    className="absolute inset-0 bg-cover bg-center bg-no-repeat"
                    style={{
                        backgroundImage: 'url(/images/mithai-background.png)',
                        filter: 'brightness(0.7)'
                    }}
                />

                {/* Gradient Overlay */}
                <div className="absolute inset-0 bg-gradient-to-br from-amber-900/40 via-orange-800/30 to-rose-900/40" />

                {/* Glassmorphism Card */}
                <div className="relative bg-white/10 backdrop-blur-xl rounded-3xl shadow-2xl p-12 w-full max-w-md text-center border border-white/20">
                    <h1 className="text-5xl font-bold text-white mb-4 drop-shadow-lg" style={{ fontFamily: 'Georgia, serif' }}>
                        رحمتِ شیریں
                    </h1>
                    <p className="text-amber-100 text-xl mb-8 font-medium">AI Voice Assistant</p>

                    <button
                        onClick={startCall}
                        disabled={isConnecting}
                        className="w-28 h-28 bg-gradient-to-br from-green-400 to-emerald-500 hover:from-green-500 hover:to-emerald-600 disabled:from-gray-400 disabled:to-gray-500 rounded-full flex items-center justify-center shadow-2xl shadow-green-500/50 transition-all transform hover:scale-110 mx-auto"
                    >
                        <svg
                            className="w-14 h-14 text-white drop-shadow-lg"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                        >
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"
                            />
                        </svg>
                    </button>

                    <p className="text-base text-amber-100 mt-6 font-medium bg-white/10 backdrop-blur-sm rounded-full py-2 px-6 inline-block">
                        {isConnecting ? '⏳ Connecting...' : '📞 Tap to call'}
                    </p>
                </div>
            </div>
        );
    }

    return (
        <LiveKitRoom
            token={token}
            serverUrl={process.env.NEXT_PUBLIC_LIVEKIT_URL}
            connect={true}
            audio={true}
            video={false}
            onDisconnected={endCall}
        >
            <VoiceInterface />

            {/* End Call Button */}
            <div className="fixed bottom-8 left-1/2 transform -translate-x-1/2">
                <button
                    onClick={endCall}
                    className="w-20 h-20 bg-gradient-to-br from-red-500 to-rose-600 hover:from-red-600 hover:to-rose-700 rounded-full flex items-center justify-center shadow-2xl shadow-red-500/50 transition-all transform hover:scale-110 border-4 border-white/30"
                >
                    <svg
                        className="w-10 h-10 text-white drop-shadow-lg"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                    >
                        <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M16 8l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2M5 3a2 2 0 00-2 2v1c0 8.284 6.716 15 15 15h1a2 2 0 002-2v-3.28a1 1 0 00-.684-.948l-4.493-1.498a1 1 0 00-1.21.502l-1.13 2.257a11.042 11.042 0 01-5.516-5.517l2.257-1.128a1 1 0 00.502-1.21L9.228 3.683A1 1 0 008.279 3H5z"
                        />
                    </svg>
                </button>
            </div>
        </LiveKitRoom>
    );
}
