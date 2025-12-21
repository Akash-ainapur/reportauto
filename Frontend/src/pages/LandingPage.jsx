import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import { Sparkles, ArrowRight } from "lucide-react";
import { SignInButton, SignedIn, SignedOut } from "@clerk/clerk-react";

const LandingPage = () => {
    return (
        <div className="min-h-screen pt-24 pb-0 px-4 flex flex-col bg-background">
            <Navbar />

            <div className="flex-grow flex items-center justify-center">
                {/* Hero Section */}
                <div className="max-w-4xl mx-auto text-center space-y-12 mb-20">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.8 }}
                    >
                        <h1 className="text-4xl md:text-6xl font-extrabold pb-4 bg-clip-text text-transparent bg-gradient-to-r from-white via-purple-200 to-purple-400 leading-tight">
                            The Report Tool Your Future Self <br /> Will Thank You For.
                        </h1>
                    </motion.div>

                    <motion.p
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.3 }}
                        className="text-xl md:text-2xl text-gray-400 max-w-3xl mx-auto leading-relaxed"
                    >
                        Auto-generate Major & Mini Project reports that tick <span className="text-white font-semibold">every MVJ checkbox</span>. More time for the group chat, less time cursing at page margins.
                    </motion.p>

                    <motion.div
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: 0.5 }}
                        className="pt-8 flex justify-center"
                    >
                        <SignedOut>
                            <SignInButton mode="modal">
                                <button className="group relative px-8 py-4 bg-white text-black text-lg font-bold rounded-full overflow-hidden transition-all hover:scale-105 hover:shadow-[0_0_40px_rgba(255,255,255,0.5)]">
                                    <div className="absolute inset-0 bg-gradient-to-r from-purple-400 to-pink-400 opacity-0 group-hover:opacity-20 transition-opacity" />
                                    <span className="flex items-center gap-2">
                                        Get Started <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                                    </span>
                                </button>
                            </SignInButton>
                        </SignedOut>

                        <SignedIn>
                            <Link to="/generate">
                                <button className="group relative px-8 py-4 bg-gradient-to-r from-primary to-purple-600 text-white text-lg font-bold rounded-full overflow-hidden transition-all hover:scale-105 hover:shadow-[0_0_40px_rgba(168,85,247,0.5)]">
                                    <span className="flex items-center gap-2">
                                        Go to Dashboard <Sparkles className="w-5 h-5 animate-pulse" />
                                    </span>
                                </button>
                            </Link>
                        </SignedIn>
                    </motion.div>
                </div>
            </div>

            <Footer />
        </div>
    );
};

export default LandingPage;
