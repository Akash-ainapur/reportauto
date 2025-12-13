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
    "Convincing the plagiarisim checker...",
    "Deleting 'As an AI language model'...",
    "Asking ChatGPT for a favor...",
    "Downloading more RAM...",
    "Calculating the meaning of life...",
    "Finding the any key...",
    "Optimizing code with if-else statements...",
    "Adding bugs to fix later...",
    "Drinking coffee...",
    "Pretending to work...",
    "Googling how to centre a div...",
    "Copying code from a YouTube tutorial...",
    "Updating dependencies...",
    "Breaking production...",
    "Fixing a typo...",
    "Git pushing force...",
    "Blaming the intern...",
    "Asking for a raise...",
    "Deploying on Friday...",
    "Ignoring warnings...",
    "Writing documentation (just kidding)...",
    "Commenting out broken code...",
    "Restarting the server...",
    "Clearing cache...",
    "Running in circles...",
    "Shaving yaks...",
    "Herding cats...",
    "Mining bitcoin...",
    "Training the AI...",
    "Overfitting the model...",
    "Underfitting the model...",
    "Fitting the model just right...",
    "Spinning the loading wheel...",
    "Counting pixels...",
    "Drawing triangles...",
    "Rendering polygons...",
    "Compiling shaders...",
    "Synthesizing voice...",
    "Generating buzzwords...",
    "Leveraging synergy...",
    "Disrupting the industry...",
    "Thinking outside the box...",
    "Circling back...",
    "Taking this offline...",
    "Low hanging fruit...",
    "Moving the needle...",
    "Touching base...",
    "Deep diving...",
    "Resulting...",
    "Actioning...",
    "Deliverabling...",
    "Impacting...",
    "Onboarding...",
    "Offboarding...",
];

const GamifiedLoader = ({ progress = 0 }) => {
    const [index, setIndex] = useState(0);

    useEffect(() => {
        const interval = setInterval(() => {
            setIndex((prev) => (prev + 1) % loadingMessages.length);
        }, 2000); // Cycle every 2 seconds
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="flex flex-col items-center justify-center p-8 text-center space-y-6 w-full max-w-md">
            <div className="relative w-32 h-32 mb-4">
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
                    {Math.round(progress)}%
                </div>
            </div>

            <div className="w-full bg-white/10 rounded-full h-2.5 mb-4 overflow-hidden">
                <motion.div
                    className="bg-gradient-to-r from-primary to-purple-500 h-2.5 rounded-full"
                    initial={{ width: 0 }}
                    animate={{ width: `${progress}%` }}
                    transition={{ duration: 0.5 }}
                />
            </div>

            <div className="h-16 overflow-hidden flex items-center justify-center">
                <AnimatePresence mode="wait">
                    <motion.p
                        key={index}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        transition={{ duration: 0.3 }}
                        className="text-lg text-purple-200 font-medium px-4"
                    >
                        "{loadingMessages[index]}"
                    </motion.p>
                </AnimatePresence>
            </div>
        </div>
    );
};

export default GamifiedLoader;
