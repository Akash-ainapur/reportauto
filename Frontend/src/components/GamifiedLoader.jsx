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
        <div className="flex flex-col items-center justify-center p-8 text-center space-y-6 w-full max-w-md bg-white border-3 border-black shadow-neo">
            <div className="relative w-32 h-32 mb-4">
                {/* Retro Spinner */}
                <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                    className="absolute inset-0 rounded-none border-4 border-black border-t-primary border-r-black border-b-black border-l-black bg-transparent"
                />
                <motion.div
                    animate={{ rotate: -360 }}
                    transition={{ duration: 4, repeat: Infinity, ease: "linear" }}
                    className="absolute inset-4 rounded-none border-4 border-black border-b-accent-teal bg-transparent"
                />
                <div className="absolute inset-0 flex items-center justify-center font-heading text-3xl text-black font-bold">
                    {Math.round(progress)}%
                </div>
            </div>

            <div className="w-full bg-gray-200 border-2 border-black h-6 rounded-none overflow-hidden relative">
                <motion.div
                    className="bg-accent-purple h-full border-r-2 border-black"
                    initial={{ width: 0 }}
                    animate={{ width: `${progress}%` }}
                    transition={{ duration: 0.5 }}
                />

                {/* Striped overlay pattern */}
                <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNCIgaGVpZ2h0PSI0IiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPjxwYXRoIGQ9Ik0xIDRoMVYwSDF6IiBmaWxsPSIjMDAwIiBmaWxsLW9wYWNpdHk9IjAuMSIvPjwvc3ZnPg==')] opacity-30 pointer-events-none" />
            </div>

            <div className="h-20 flex items-center justify-center w-full border-2 border-dashed border-gray-400 bg-gray-50 p-2">
                <AnimatePresence mode="wait">
                    <motion.p
                        key={index}
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 1.1 }}
                        transition={{ duration: 0.2 }}
                        className="text-lg text-black font-mono font-bold px-4 uppercase"
                    >
                        "{loadingMessages[index]}"
                    </motion.p>
                </AnimatePresence>
            </div>
        </div>
    );
};

export default GamifiedLoader;
