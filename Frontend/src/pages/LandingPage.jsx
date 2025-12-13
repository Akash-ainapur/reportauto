import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { FileText, Zap, Shield, Sparkles, Database, LayoutTemplate, Share2, Clock } from "lucide-react";
import GlassCard from "../components/GlassCard";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import About from "../components/About";
import Pricing from "../components/Pricing";

const LandingPage = () => {
    return (
        <div className="min-h-screen pt-24 pb-0 px-4 flex flex-col">
            <Navbar />

            <div className="flex-grow">
                {/* Hero Section */}
                <div className="max-w-7xl mx-auto text-center space-y-8 mb-24 mt-12">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.8 }}
                    >
                        <h1 className="text-5xl md:text-7xl font-extrabold pb-2 bg-clip-text text-transparent bg-gradient-to-r from-white via-purple-200 to-purple-400">
                            Automate Your Reports <br /> Like a Pro.
                        </h1>
                    </motion.div>

                    <motion.p
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.3 }}
                        className="text-xl text-gray-400 max-w-2xl mx-auto"
                    >
                        Stop wasting hours on formatting. Generate college-ready reports in seconds with our AI-powered tool.
                    </motion.p>

                    <motion.div
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: 0.5 }}
                    >
                        <Link to="/auth">
                            <button className="px-8 py-4 rounded-full bg-white text-black text-lg font-bold hover:scale-105 transition-transform shadow-[0_0_40px_rgba(255,255,255,0.3)]">
                                Start Generating Now
                            </button>
                        </Link>
                    </motion.div>
                </div>

                {/* Bento Grid Features - Enhanced */}
                <div id="features" className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-6 mb-20 scroll-mt-28">

                    {/* Feature 1: AI (Big Card) */}
                    <motion.div
                        className="md:col-span-2 md:row-span-2"
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.5 }}
                    >
                        <GlassCard className="h-full flex flex-col justify-between overflow-hidden relative group hover:border-purple-500/50 transition-colors">
                            <div className="absolute inset-0 bg-gradient-to-br from-purple-500/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
                            <div className="z-10 relative">
                                <div className="p-3 bg-purple-500/20 w-fit rounded-lg mb-4">
                                    <Sparkles className="text-purple-300 w-8 h-8" />
                                </div>
                                <h3 className="text-3xl font-bold text-white mb-4">AI-Powered Magic</h3>
                                <p className="text-gray-400 text-lg">
                                    Intelligent formatting that understands your content.
                                    Headers, margins, and citations are auto-generated to meet university standards perfectly.
                                </p>
                            </div>
                            <div className="absolute -right-10 -bottom-10 w-64 h-64 bg-purple-500/20 rounded-full blur-3xl group-hover:bg-purple-500/30 transition-colors" />
                        </GlassCard>
                    </motion.div>

                    {/* Feature 2: Speed */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ delay: 0.1, duration: 0.5 }}
                    >
                        <GlassCard className="h-full flex flex-col justify-between relative overflow-hidden group hover:-translate-y-2 transition-transform duration-300">
                            <div className="z-10">
                                <div className="p-3 bg-blue-500/20 w-fit rounded-lg mb-4">
                                    <Zap className="text-blue-300" />
                                </div>
                                <h3 className="text-xl font-bold text-white mb-2">Lightning Fast</h3>
                                <p className="text-gray-400 text-sm">Convert raw data to PDF in under 60 seconds flat.</p>
                            </div>
                        </GlassCard>
                    </motion.div>

                    {/* Feature 3: Security */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ delay: 0.2, duration: 0.5 }}
                    >
                        <GlassCard className="h-full flex flex-col justify-between relative overflow-hidden group hover:-translate-y-2 transition-transform duration-300">
                            <div className="z-10">
                                <div className="p-3 bg-green-500/20 w-fit rounded-lg mb-4">
                                    <Shield className="text-green-300" />
                                </div>
                                <h3 className="text-xl font-bold text-white mb-2">Secure & Private</h3>
                                <p className="text-gray-400 text-sm">Your data is encrypted and never shared with third parties.</p>
                            </div>
                        </GlassCard>
                    </motion.div>

                    {/* Feature 4: Templates */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ delay: 0.3, duration: 0.5 }}
                    >
                        <GlassCard className="h-full flex flex-col justify-between relative overflow-hidden group hover:-translate-y-2 transition-transform duration-300">
                            <div className="z-10">
                                <div className="p-3 bg-pink-500/20 w-fit rounded-lg mb-4">
                                    <LayoutTemplate className="text-pink-300" />
                                </div>
                                <h3 className="text-xl font-bold text-white mb-2">Pro Templates</h3>
                                <p className="text-gray-400 text-sm">Pre-designed templates for every engineering domain.</p>
                            </div>
                        </GlassCard>
                    </motion.div>

                    {/* Feature 5: History (New) */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ delay: 0.4, duration: 0.5 }}
                    >
                        <GlassCard className="h-full flex flex-col justify-between relative overflow-hidden group hover:-translate-y-2 transition-transform duration-300">
                            <div className="z-10">
                                <div className="p-3 bg-orange-500/20 w-fit rounded-lg mb-4">
                                    <Clock className="text-orange-300" />
                                </div>
                                <h3 className="text-xl font-bold text-white mb-2">Auto-Save</h3>
                                <p className="text-gray-400 text-sm">Never lose your progress. Edits save automatically.</p>
                            </div>
                        </GlassCard>
                    </motion.div>

                    {/* Feature 6: Export (Wide) */}
                    <motion.div
                        className="md:col-span-2"
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ delay: 0.5, duration: 0.5 }}
                    >
                        <GlassCard className="h-full flex flex-col justify-between overflow-hidden relative group hover:border-pink-500/50 transition-colors">
                            <div className="absolute inset-0 bg-gradient-to-br from-pink-500/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
                            <div className="z-10 flex items-center gap-6">
                                <div>
                                    <div className="p-3 bg-pink-500/20 w-fit rounded-lg mb-4">
                                        <FileText className="text-pink-300 w-6 h-6" />
                                    </div>
                                    <h3 className="text-2xl font-bold text-white mb-2">Universal Export</h3>
                                    <p className="text-gray-400">Download formatted reports in DOCX for editing or PDF for final submission.</p>
                                </div>
                                <Share2 className="w-24 h-24 text-pink-500/20 hidden md:block" />
                            </div>
                        </GlassCard>
                    </motion.div>

                </div>
            </div>

            {/* Project Roadmap Section */}
            <Pricing />

            <About />

            <Footer />
        </div>
    );
};

export default LandingPage;
