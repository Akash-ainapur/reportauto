import { useState } from "react";
import { Link } from "react-router-dom";
import { SignInButton, SignedIn, SignedOut, UserButton } from "@clerk/clerk-react";
import { Menu, X } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

const Navbar = () => {
    return (
        <nav className="fixed top-0 w-full z-50 bg-white border-b-4 border-black">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between items-center h-20">
                    {/* Logo */}
                    <Link to="/" className="flex items-center">
                        <span className="text-3xl font-black tracking-tighter uppercase font-heading bg-black text-white px-2 py-1 transform -rotate-1">
                            PROJECT_HACK
                        </span>
                        <span className="text-3xl font-black tracking-tighter uppercase font-heading ml-1">.exe</span>
                    </Link>

                    {/* Desktop Menu */}
                    <div className="flex items-center space-x-8">
                        <SignedIn>
                            <Link to="/generate">
                                <button className="neo-button px-6 py-2 bg-[#F4D73B] text-black text-lg">
                                    DASHBOARD
                                </button>
                            </Link>
                            <UserButton afterSignOutUrl="/" />
                        </SignedIn>
                        <SignedOut>
                            <SignInButton mode="modal">
                                <button className="font-heading uppercase text-xl px-8 py-2 bg-white text-black border-4 border-black shadow-[4px_4px_0_#000] hover:translate-x-1 hover:translate-y-1 hover:shadow-none transition-all font-bold">
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
