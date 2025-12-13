import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import { Sparkles } from "lucide-react";

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
                        className="pt-4"
                    >
                        <Link to="/generate">
                            <button className="group relative px-10 py-5 rounded-full bg-white text-black text-xl font-bold hover:scale-105 transition-all shadow-[0_0_50px_rgba(255,255,255,0.2)] hover:shadow-[0_0_70px_rgba(255,255,255,0.4)] flex items-center gap-3 mx-auto">
                                <Sparkles className="w-6 h-6 text-purple-600 group-hover:rotate-12 transition-transform" />
                                Get Started
                            </button>
                        </Link>
                    </motion.div>
                </div>
            </div>

            <Footer />
        </div>
    );
};

export default LandingPage;
