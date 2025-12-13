import { motion, AnimatePresence } from "framer-motion";
import { useState, useEffect } from "react";

const loadingMessages = [
    "Bribing the external examiner...",
    "Formatting margins so your HOD doesn't yell...",
    "Stealing words from Wikipedia...",
    "Consulting Stack Overflow...",
    "Adding 'Artificial Intelligence' to the abstract...",
    "Generating random pie charts...",
    "Making it look like you worked hard...",
];

const GamifiedLoader = () => {
    const [index, setIndex] = useState(0);

    useEffect(() => {
        const interval = setInterval(() => {
            setIndex((prev) => (prev + 1) % loadingMessages.length);
        }, 2500);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="flex flex-col items-center justify-center p-8 text-center space-y-6">
            <div className="relative w-32 h-32">
                <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 4, repeat: Infinity, ease: "linear" }}
                    className="absolute inset-0 rounded-full border-4 border-transparent border-t-primary border-r-purple-500 blur-sm"
                />
                <motion.div
                    animate={{ rotate: -360 }}
                    transition={{ duration: 8, repeat: Infinity, ease: "linear" }}
                    className="absolute inset-2 rounded-full border-4 border-transparent border-b-cyan-500 border-l-blue-500 blur-sm"
                />
                <div className="absolute inset-0 flex items-center justify-center font-bold text-2xl text-white">
                    AI
                </div>
            </div>

            <div className="h-8 overflow-hidden">
                <AnimatePresence mode="wait">
                    <motion.p
                        key={index}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                        className="text-lg text-purple-200 font-medium"
                    >
                        {loadingMessages[index]}
                    </motion.p>
                </AnimatePresence>
            </div>
        </div>
    );
};

export default GamifiedLoader;
