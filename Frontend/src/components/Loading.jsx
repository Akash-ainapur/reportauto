import React, { useState, useEffect } from 'react';

const Loading = ({ progress = 0 }) => {
    const [currentMessage, setCurrentMessage] = useState(0);

    const messages = [
        "Feeding coffee to the AI...",
        "Aligning margins pixel by pixel...",
        "Bribing external examiner...",
        "Generating academic jargon...",
        "Pretending to work hard...",
        "Adding fancy diagrams...",
        "Making it look professional...",
        "Almost there..."
    ];

    useEffect(() => {
        const messageInterval = setInterval(() => {
            setCurrentMessage(prev => (prev + 1) % messages.length);
        }, 2000);

        return () => clearInterval(messageInterval);
    }, [messages.length]);

    return (
        <div className="fixed inset-0 z-50 bg-white flex items-center justify-center p-4 relative overflow-hidden">
            {/* Animated Background Elements */}
            <div className="absolute top-10 left-10 w-16 h-16 bg-retro-yellow border-3 border-black animate-bounce"></div>
            <div className="absolute top-20 right-20 w-12 h-12 bg-retro-coral border-3 border-black animate-spin" style={{ animationDuration: '3s' }}></div>
            <div className="absolute bottom-20 left-1/4 w-20 h-20 bg-retro-purple border-3 border-black animate-pulse"></div>

            <div className="max-w-3xl w-full relative z-10">
                {/* Loading Card */}
                <div className="bg-white border-3 border-black shadow-brutal-xl p-8 md:p-12">
                    {/* Title */}
                    <div className="text-center mb-12">
                        <h1 className="font-['Oswald'] text-5xl md:text-6xl font-bold uppercase mb-4">
                            COOKING
                            <br />
                            <span className="text-retro-yellow">YOUR REPORT</span>
                        </h1>
                        <p className="text-xl font-bold text-black/70">
                            This might take 30-60 seconds...
                        </p>
                    </div>

                    {/* Retro Progress Bar */}
                    <div className="mb-8">
                        <div className="bg-white border-3 border-black h-16 relative overflow-hidden">
                            {/* Segmented Progress */}
                            <div className="absolute inset-0 flex">
                                {[...Array(20)].map((_, i) => {
                                    const segmentProgress = (i + 1) * 5;
                                    const isFilled = progress >= segmentProgress;
                                    return (
                                        <div
                                            key={i}
                                            className={`flex-1 border-r-2 border-black transition-all duration-300 ${isFilled ? 'bg-retro-yellow' : 'bg-white'
                                                }`}
                                        ></div>
                                    );
                                })}
                            </div>

                            {/* Percentage */}
                            <div className="absolute inset-0 flex items-center justify-center">
                                <span
                                    className="font-['Oswald'] text-3xl font-bold"
                                    data-testid="loading-percentage"
                                >
                                    {progress}%
                                </span>
                            </div>
                        </div>
                    </div>

                    {/* Loading Messages */}
                    <div className="bg-black text-white border-3 border-black p-6 min-h-[100px] flex items-center justify-center">
                        <p
                            className="font-['VT323'] text-2xl text-center animate-pulse"
                            data-testid="loading-message"
                        >
                            &gt; {messages[currentMessage]}
                        </p>
                    </div>

                    {/* Pixel Art Loader */}
                    <div className="mt-8 flex justify-center gap-2">
                        {[...Array(5)].map((_, i) => (
                            <div
                                key={i}
                                className="w-4 h-4 bg-black border-2 border-black animate-bounce"
                                style={{
                                    animationDelay: `${i * 0.1}s`,
                                    animationDuration: '0.6s'
                                }}
                            ></div>
                        ))}
                    </div>

                    {/* Fun Fact */}
                    <div className="mt-12 text-center">
                        <div className="inline-block bg-retro-coral border-3 border-black px-6 py-3 rotate-[-1deg] shadow-brutal-sm">
                            <p className="font-bold text-sm">
                                💡 FACT: You're saving ~5 hours of formatting hell right now!
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Loading;
