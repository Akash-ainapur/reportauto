import { motion } from "framer-motion";
import { Check, Zap, FileText } from "lucide-react";
import GlassCard from "./GlassCard";
import { Link } from "react-router-dom";

const Pricing = () => {
    return (
        <section id="pricing" className="max-w-7xl mx-auto px-4 mb-24 scroll-mt-28">
            <div className="text-center mb-16">
                <motion.h2
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    className="text-4xl md:text-5xl font-bold text-white mb-4"
                >
                    Simple, Transparent Pricing
                </motion.h2>
                <motion.p
                    initial={{ opacity: 0 }}
                    whileInView={{ opacity: 1 }}
                    viewport={{ once: true }}
                    transition={{ delay: 0.2 }}
                    className="text-gray-400 max-w-2xl mx-auto text-lg"
                >
                    No hidden fees. Pay only when you generate.
                </motion.p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto">
                {/* Standard Plan */}
                <motion.div
                    initial={{ opacity: 0, x: -50 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: 0.1 }}
                >
                    <GlassCard className="h-full relative overflow-hidden group hover:border-purple-500/50 transition-all duration-300 flex flex-col">
                        <div className="absolute top-0 right-0 p-4 opacity-10">
                            <Zap className="w-24 h-24 text-white" />
                        </div>

                        <div className="p-4 relative z-10 flex-grow">
                            <h3 className="text-2xl font-bold text-white mb-2">Standard Report</h3>
                            <div className="flex items-baseline gap-1 my-6">
                                <span className="text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400">₹38</span>
                                <span className="text-gray-400">/ report</span>
                            </div>

                            <p className="text-gray-300 mb-6">Perfect for final project submissions and standard academic reports.</p>

                            <ul className="space-y-4 mb-8">
                                <li className="flex items-center gap-3 text-gray-300">
                                    <div className="p-1 bg-green-500/20 rounded-full"><Check className="w-3 h-3 text-green-400" /></div>
                                    Full Report Generation
                                </li>
                                <li className="flex items-center gap-3 text-gray-300">
                                    <div className="p-1 bg-green-500/20 rounded-full"><Check className="w-3 h-3 text-green-400" /></div>
                                    AI-Auto Formatting
                                </li>
                                <li className="flex items-center gap-3 text-gray-300">
                                    <div className="p-1 bg-green-500/20 rounded-full"><Check className="w-3 h-3 text-green-400" /></div>
                                    PDF & DOCX Export
                                </li>
                            </ul>
                        </div>

                        <Link to="/auth" className="mt-auto">
                            <button className="w-full py-3 rounded-xl bg-white text-black font-bold hover:scale-[1.02] active:scale-[0.98] transition-all">
                                Get Started
                            </button>
                        </Link>
                    </GlassCard>
                </motion.div>

                {/* Per Page Plan */}
                <motion.div
                    initial={{ opacity: 0, x: 50 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: 0.3 }}
                >
                    <GlassCard className="h-full relative overflow-hidden group hover:border-blue-500/50 transition-all duration-300 flex flex-col border-blue-500/20">
                        <div className="absolute top-0 right-0 p-4 opacity-10">
                            <FileText className="w-24 h-24 text-blue-400" />
                        </div>

                        <div className="p-4 relative z-10 flex-grow">
                            <div className="absolute -top-4 -right-4 bg-blue-500 text-white text-xs font-bold px-3 py-1 rounded-bl-xl">FLEXIBLE</div>
                            <h3 className="text-2xl font-bold text-white mb-2">Pay Per Page</h3>
                            <div className="flex items-baseline gap-1 my-6">
                                <span className="text-5xl font-extrabold text-white">₹1</span>
                                <span className="text-gray-400">/ page</span>
                            </div>

                            <p className="text-gray-300 mb-6">Ideal for smaller assignments or custom length documents.</p>

                            <ul className="space-y-4 mb-8">
                                <li className="flex items-center gap-3 text-gray-300">
                                    <div className="p-1 bg-blue-500/20 rounded-full"><Check className="w-3 h-3 text-blue-400" /></div>
                                    Pay only for what you need
                                </li>
                                <li className="flex items-center gap-3 text-gray-300">
                                    <div className="p-1 bg-blue-500/20 rounded-full"><Check className="w-3 h-3 text-blue-400" /></div>
                                    Same Premium Quality
                                </li>
                                <li className="flex items-center gap-3 text-gray-300">
                                    <div className="p-1 bg-blue-500/20 rounded-full"><Check className="w-3 h-3 text-blue-400" /></div>
                                    Quick Turnaround
                                </li>
                            </ul>
                        </div>

                        <Link to="/auth" className="mt-auto">
                            <button className="w-full py-3 rounded-xl bg-blue-600/20 border border-blue-500/30 text-blue-300 font-bold hover:bg-blue-600/30 transition-all">
                                Calculate Price
                            </button>
                        </Link>
                    </GlassCard>
                </motion.div>
            </div>
        </section>
    );
};

export default Pricing;
