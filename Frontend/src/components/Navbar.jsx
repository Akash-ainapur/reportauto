import { useState } from "react";
import { Link } from "react-router-dom";
import { SignInButton, SignedIn, SignedOut, UserButton } from "@clerk/clerk-react";
import { Menu, X } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

const Navbar = () => {
    return (
        <nav className="fixed top-0 w-full z-50 bg-white border-b-4 border-black">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex flex-col md:flex-row justify-between items-center h-auto md:h-20 py-4 md:py-0 gap-4 md:gap-0">
                    {/* Logo */}
                    <Link to="/" className="flex items-center group">
                        <span className="text-2xl md:text-3xl font-black tracking-tighter uppercase font-heading bg-black text-white px-2 py-1 transform -rotate-1 group-hover:rotate-0 transition-transform">
                            PROJECT_HACK
                        </span>
                        <span className="text-2xl md:text-3xl font-black tracking-tighter uppercase font-heading ml-1">.exe</span>
                    </Link>

                    {/* Desktop Menu */}
                    <div className="flex items-center space-x-4 md:space-x-8">
                        <SignedIn>
                            <Link to="/generate">
                                <button className="neo-button px-4 py-1 text-sm md:px-6 md:py-2 bg-[#F4D73B] text-black md:text-lg border-2 md:border-4">
                                    DASHBOARD
                                </button>
                            </Link>
                            <div className="scale-75 md:scale-100">
                                <UserButton afterSignOutUrl="/" />
                            </div>
                        </SignedIn>
                        <SignedOut>
                            <SignInButton mode="modal">
                                <button className="font-heading uppercase text-sm md:text-xl px-4 py-1 md:px-8 md:py-2 bg-white text-black border-2 md:border-4 border-black shadow-[2px_2px_0_#000] md:shadow-[4px_4px_0_#000] hover:translate-x-1 hover:translate-y-1 hover:shadow-none transition-all font-bold">
                                    LOGIN
                                </button>
                            </SignInButton>
                        </SignedOut>
                    </div>
                </div>
            </div>
        </nav>
    );
};

export default Navbar;
