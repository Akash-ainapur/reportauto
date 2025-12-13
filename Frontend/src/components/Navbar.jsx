import { useState } from "react";
import { Link } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { Menu, X } from "lucide-react";
import { SignedIn, SignedOut, UserButton } from "@clerk/clerk-react";

const Navbar = () => {
    const [isOpen, setIsOpen] = useState(false);

    return (
        <nav className="fixed top-0 w-full z-50 px-4 py-4">
            <div className="max-w-7xl mx-auto glass rounded-2xl px-6 py-3 flex items-center justify-between">
                <Link to="/" className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-purple-400 to-pink-600">
                    ReportAuto
                </Link>

                {/* Desktop Menu */}
                <div className="hidden md:flex items-center space-x-8">
                    <a href="/#features" className="text-gray-300 hover:text-white transition-colors">Features</a>
                    <a href="/#pricing" className="text-gray-300 hover:text-white transition-colors">Pricing</a>
                    <a href="/#about" className="text-gray-300 hover:text-white transition-colors">About</a>

                    <SignedIn>
                        <UserButton afterSignOutUrl="/" />
                    </SignedIn>

                    <SignedOut>
                        <Link to="/auth">
                            <button className="px-6 py-2 rounded-xl bg-primary text-white font-medium hover:bg-primary/80 transition-all shadow-[0_0_20px_rgba(124,58,237,0.5)]">
                                Login / Sign Up
                            </button>
                        </Link>
                    </SignedOut>
                </div>

                {/* Mobile Toggle */}
                <button className="md:hidden text-white" onClick={() => setIsOpen(!isOpen)}>
                    {isOpen ? <X /> : <Menu />}
                </button>
            </div>

            {/* Mobile Menu */}
            <AnimatePresence>
                {isOpen && (
                    <motion.div
                        initial={{ opacity: 0, y: -20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                        className="absolute top-20 left-4 right-4 glass rounded-2xl p-6 flex flex-col space-y-4 md:hidden"
                    >
                        <a href="/#features" className="text-lg text-gray-300" onClick={() => setIsOpen(false)}>Features</a>
                        <a href="/#pricing" className="text-lg text-gray-300" onClick={() => setIsOpen(false)}>Pricing</a>

                        <SignedIn>
                            <div className="flex items-center gap-2">
                                <span className="text-white">Account:</span>
                                <UserButton afterSignOutUrl="/" />
                            </div>
                        </SignedIn>

                        <SignedOut>
                            <Link to="/auth" onClick={() => setIsOpen(false)} className="text-primary font-bold">Login / Sign Up</Link>
                        </SignedOut>
                    </motion.div>
                )}
            </AnimatePresence>
        </nav>
    );
};

export default Navbar;
