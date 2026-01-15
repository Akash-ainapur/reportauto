import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import { ArrowRight } from "lucide-react";
import { SignInButton, SignedIn, SignedOut } from "@clerk/clerk-react";



// Asset Imports for Production
import retroMonitor from "../assets/retro_monitor.png";
import starburst from "../assets/starburst_new.png";
import squiggles from "../assets/hero_squiggles.png";

const LandingPage = () => {
    return (
        <div className="min-h-screen pt-24 pb-0 flex flex-col bg-transparent relative overflow-x-hidden text-left">
            <Navbar />

            {/* Main Content Area */}
            <div className="flex-grow flex items-center justify-center relative z-10 px-4 md:px-12 py-12">
                <div className="max-w-7xl mx-auto w-full grid grid-cols-1 md:grid-cols-2 gap-12 items-center">

                    {/* Left Column: Text & CTA */}
                    <div className="space-y-6 relative">
                        {/* Headline */}
                        <motion.h1
                            initial={{ opacity: 0, y: 50 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="text-5xl md:text-7xl font-black text-black leading-[0.9] uppercase tracking-tighter"
                        >
                            Report<br />
                            Generator For<br />
                            Procrastinators.
                        </motion.h1>

                        {/* Description Box */}
                        <motion.div
                            initial={{ opacity: 0, x: -50 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: 0.2 }}
                            className="neo-box p-6 bg-white relative max-w-lg z-20"
                        >
                            <p className="text-black font-mono text-lg md:text-xl font-bold leading-tight">
                                Auto-generate Major & Mini Project reports that tick every MVJ checkbox. <br />
                                100% formatted. 0% headache.
                            </p>
                        </motion.div>

                        {/* CTA Section */}
                        <motion.div
                            initial={{ opacity: 0, scale: 0.9 }}
                            animate={{ opacity: 1, scale: 1 }}
                            transition={{ delay: 0.4 }}
                            className="pt-4"
                        >
                            <SignedOut>
                                <SignInButton mode="modal">
                                    <button className="w-full md:w-auto text-xl md:text-5xl font-black bg-[#F4D73B] text-black px-6 py-3 md:px-8 md:py-4 border-4 border-black shadow-[8px_8px_0px_0px_#000000] hover:translate-x-1 hover:translate-y-1 hover:shadow-none transition-all flex items-center justify-center gap-4 uppercase font-heading">
                                        Start Now <ArrowRight className="w-8 h-8 md:w-10 md:h-10 border-2 border-black rounded-full p-1" />
                                    </button>
                                </SignInButton>
                            </SignedOut>
                            <SignedIn>
                                <Link to="/generate">
                                    <button className="w-full md:w-auto text-xl md:text-5xl font-black bg-[#F4D73B] text-black px-6 py-3 md:px-8 md:py-4 border-4 border-black shadow-[8px_8px_0px_0px_#000000] hover:translate-x-1 hover:translate-y-1 hover:shadow-none transition-all flex items-center justify-center gap-4 uppercase font-heading">
                                        Start Now <ArrowRight className="w-8 h-8 md:w-10 md:h-10 border-2 border-black rounded-full p-1" />
                                    </button>
                                </Link>
                            </SignedIn>
                        </motion.div>
                    </div>

                    {/* Right Column: Retro Image - Professionally Balanced */}
                    <div className="relative flex justify-center items-center w-full h-full p-6 md:p-0">
                        {/* 
                            Image Wrapper: 
                            - constrained to max-w-lg (approx 512px) for perfect desktop sizing. 
                            - w-full ensures it shrinks on mobile.
                            - relative positioning ensures stickers stay attached to the image.
                        */}
                        <div className="relative w-full max-w-lg">

                            {/* Starburst Sticker */}
                            <motion.div
                                animate={{ rotate: [0, 5, -5, 0] }}
                                transition={{ repeat: Infinity, duration: 4, ease: "easeInOut" }}
                                className="absolute -top-12 -left-12 z-30 w-32 md:w-48 transform -rotate-12"
                            >
                                <img src={starburst} alt="NEW!" className="w-full drop-shadow-[5px_5px_0_rgba(0,0,0,1)]" onError={(e) => e.target.style.display = 'none'} />
                            </motion.div>

                            {/* Main Monitor Image */}
                            <div className="relative z-10 w-full transform hover:scale-105 transition-transform duration-500 ease-out">
                                <img
                                    src={retroMonitor}
                                    alt="Retro Monitor"
                                    className="w-full h-auto object-contain drop-shadow-[16px_16px_0_rgba(0,0,0,1)]"
                                    onError={(e) => {
                                        e.target.style.display = 'none';
                                        e.target.parentElement.innerHTML = '<div class="w-full aspect-[4/3] bg-white border-4 border-black shadow-neo flex items-center justify-center font-bold text-2xl">RETRO MONITOR IMAGE MISSING</div>';
                                    }}
                                />
                            </div>

                            {/* Decor: Squiggles */}
                            <img
                                src={squiggles}
                                alt=""
                                className="absolute -z-10 -right-16 top-1/2 transform -translate-y-1/2 w-40 md:w-80 pointer-events-none opacity-90"
                                onError={(e) => e.target.style.display = 'none'}
                            />
                        </div>
                    </div>
                </div>
            </div>

            {/* Scrolling Marquee Footer */}
            <div className="fixed bottom-0 left-0 w-full bg-yellow-300 border-t-4 border-black py-3 z-50 overflow-hidden">
                <div className="animate-marquee whitespace-nowrap flex gap-12 text-xl font-bold font-mono text-black uppercase tracking-wider">
                    <span>*** Your HOD will love this ***</span>
                    <span>*** No more alignment issues ***</span>
                    <span>*** Format Verified ***</span>
                    <span>*** Saved my weekend ***</span>
                    <span>*** Your HOD will love this ***</span>
                    <span>*** No more alignment issues ***</span>
                    <span>*** Format Verified ***</span>
                    <span>*** Saved my weekend ***</span>
                </div>
            </div>

            <style jsx global>{`
                @keyframes marquee {
                    0% { transform: translateX(0); }
                    100% { transform: translateX(-50%); }
                }
                .animate-marquee {
                    animation: marquee 20s linear infinite;
                }
            `}</style>
        </div>
    );
};

export default LandingPage;
