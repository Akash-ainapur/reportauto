import { X, ShieldAlert, CheckCircle2 } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

const DisclaimerModal = ({ isOpen, onClose }) => {
    return (
        <AnimatePresence>
            {isOpen && (
                <div className="fixed inset-0 z-[70] flex items-center justify-center p-4">
                    {/* Backdrop */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={onClose}
                        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
                    />

                    {/* Modal */}
                    <motion.div
                        initial={{ scale: 0.9, opacity: 0, rotate: -2 }}
                        animate={{ scale: 1, opacity: 1, rotate: 0 }}
                        exit={{ scale: 0.9, opacity: 0, rotate: 2 }}
                        className="relative bg-white border-4 border-black shadow-[8px_8px_0_#000] p-6 md:p-8 max-w-lg w-full z-10"
                    >
                        {/* Decorative Header */}
                        <div className="absolute -top-6 -left-6 bg-yellow-400 border-4 border-black px-4 py-2 shadow-[4px_4px_0_#000] rotate-[-5deg]">
                            <span className="font-heading font-black text-xl uppercase">Real Talk 🚨</span>
                        </div>

                        <button
                            onClick={onClose}
                            className="absolute top-4 right-4 p-1 hover:bg-gray-100 border-2 border-transparent hover:border-black transition-all"
                        >
                            <X className="w-6 h-6" />
                        </button>

                        <div className="mt-6 space-y-6">
                            <h2 className="text-3xl font-heading uppercase text-stroke text-black leading-tight">
                                Wait! Don't Submit Yet!
                            </h2>

                            <div className="space-y-4 font-mono text-sm md:text-base">
                                <p className="font-bold bg-purple-100 p-3 border-l-4 border-black">
                                    Use your brain, not just the bot. 🧠
                                </p>

                                <ul className="space-y-3 list-none">
                                    <li className="flex items-start gap-3">
                                        <ShieldAlert className="w-6 h-6 text-red-500 shrink-0 mt-0.5" />
                                        <span>
                                            <strong>AI Hallucinations are real.</strong> It might invent a citation or a fact. Double-check everything.
                                        </span>
                                    </li>
                                    <li className="flex items-start gap-3">
                                        <div className="w-6 h-6 shrink-0 flex items-center justify-center font-bold text-blue-600">?</div>
                                        <span>
                                            <strong>It's a Draft, not a Final.</strong> Start with this, then add your own flavor. Profs can smell generic ChatGPT text.
                                        </span>
                                    </li>
                                    <li className="flex items-start gap-3">
                                        <CheckCircle2 className="w-6 h-6 text-green-600 shrink-0 mt-0.5" />
                                        <span>
                                            <strong>You are responsible.</strong> If there is a mistake in the report, "The AI did it" is not a valid excuse.
                                        </span>
                                    </li>
                                </ul>
                            </div>

                            <button
                                onClick={onClose}
                                className="w-full neo-button bg-green-400 text-black py-4 text-lg md:text-xl border-4 hover:shadow-none hover:translate-x-1 hover:translate-y-1 transition-all flex items-center justify-center gap-2 group"
                            >
                                <span>I PROMISE I READ THIS</span>
                                <span className="group-hover:scale-125 transition-transform">🤝</span>
                            </button>
                        </div>
                    </motion.div>
                </div>
            )}
        </AnimatePresence>
    );
};

export default DisclaimerModal;
