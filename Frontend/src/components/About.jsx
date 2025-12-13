import { motion } from "framer-motion";
import { Sparkles, FileText, ShieldCheck, Rocket } from "lucide-react";
import GlassCard from "./GlassCard";

const About = () => {
    return (
        <section
            id="about"
            className="max-w-7xl mx-auto px-4 mb-24 scroll-mt-28"
        >
            {/* Header */}
            <div className="text-center mb-16">
                <motion.h2
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.6 }}
                    className="text-4xl md:text-5xl font-bold text-white mb-4"
                >
                    About ReportAuto
                </motion.h2>

                <motion.p
                    initial={{ opacity: 0 }}
                    whileInView={{ opacity: 1 }}
                    viewport={{ once: true }}
                    transition={{ delay: 0.2 }}
                    className="text-gray-400 max-w-3xl mx-auto text-lg"
                >
                    ReportAuto is built to eliminate repetitive academic formatting work and
                    empower students to focus on what truly matters — ideas, learning,
                    and innovation.
                </motion.p>
            </div>

            {/* Content Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">

                {/* Mission */}
                <motion.div
                    initial={{ opacity: 0, x: -40 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                >
                    <GlassCard className="h-full group hover:border-purple-500/40 transition-all">
                        <div className="flex items-start gap-4">
                            <div className="p-3 bg-purple-500/20 rounded-lg">
                                <Sparkles className="w-6 h-6 text-purple-300" />
                            </div>
                            <div>
                                <h3 className="text-2xl font-bold text-white mb-3">
                                    Our Mission
                                </h3>
                                <p className="text-gray-400 leading-relaxed">
                                    To automate end-to-end academic report creation using
                                    AI-driven intelligence while maintaining strict compliance
                                    with university-approved formats.
                                </p>
                            </div>
                        </div>
                    </GlassCard>
                </motion.div>

                {/* Problem */}
                <motion.div
                    initial={{ opacity: 0, x: 40 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                >
                    <GlassCard className="h-full group hover:border-blue-500/40 transition-all">
                        <div className="flex items-start gap-4">
                            <div className="p-3 bg-blue-500/20 rounded-lg">
                                <FileText className="w-6 h-6 text-blue-300" />
                            </div>
                            <div>
                                <h3 className="text-2xl font-bold text-white mb-3">
                                    The Problem We Solve
                                </h3>
                                <p className="text-gray-400 leading-relaxed">
                                    Students waste countless hours adjusting margins,
                                    fonts, certificates, and declarations instead of
                                    working on core project logic and documentation quality.
                                </p>
                            </div>
                        </div>
                    </GlassCard>
                </motion.div>

                {/* Trust */}
                <motion.div
                    initial={{ opacity: 0, y: 40 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                >
                    <GlassCard className="h-full group hover:border-green-500/40 transition-all">
                        <div className="flex items-start gap-4">
                            <div className="p-3 bg-green-500/20 rounded-lg">
                                <ShieldCheck className="w-6 h-6 text-green-300" />
                            </div>
                            <div>
                                <h3 className="text-2xl font-bold text-white mb-3">
                                    Built for Trust
                                </h3>
                                <p className="text-gray-400 leading-relaxed">
                                    Your academic data remains private, secure, and encrypted.
                                    ReportAuto never shares content with third parties and
                                    follows best security practices by design.
                                </p>
                            </div>
                        </div>
                    </GlassCard>
                </motion.div>

                {/* Vision */}
                <motion.div
                    initial={{ opacity: 0, y: 40 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: 0.1 }}
                >
                    <GlassCard className="h-full group hover:border-pink-500/40 transition-all">
                        <div className="flex items-start gap-4">
                            <div className="p-3 bg-pink-500/20 rounded-lg">
                                <Rocket className="w-6 h-6 text-pink-300" />
                            </div>
                            <div>
                                <h3 className="text-2xl font-bold text-white mb-3">
                                    Our Vision
                                </h3>
                                <p className="text-gray-400 leading-relaxed">
                                    To evolve ReportAuto into a full SaaS platform that
                                    supports reports, documentation, and submissions
                                    across universities worldwide.
                                </p>
                            </div>
                        </div>
                    </GlassCard>
                </motion.div>

            </div>
        </section>
    );
};

export default About;
