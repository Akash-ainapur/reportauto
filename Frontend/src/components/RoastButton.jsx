import React, { useState } from 'react';
import { useLocation } from 'react-router-dom';
import { MessageCircle, X, Flame } from 'lucide-react';

const RoastButton = () => {
    const [isHovered, setIsHovered] = useState(false);
    const [isVisible, setIsVisible] = useState(true);
    // On the report form, sit above its sticky Next/Generate bar and shrink to an icon on phones
    const onForm = useLocation().pathname === '/generate';

    // User provided number
    const phoneNumber = "8317366952";

    // The "Roast" message
    const message = "Hey, honestly speaking - this app needs work. Here's what's annoying me... (don't hold back, tell me directly 😤)";

    const whatsappUrl = `https://wa.me/${phoneNumber}?text=${encodeURIComponent(message)}`;

    if (!isVisible) return null;

    return (
        <div
            className={`fixed right-4 md:right-6 z-50 flex flex-col items-end gap-2 font-sans ${onForm ? 'bottom-24 md:bottom-28' : 'bottom-6'}`}
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
        >
            {/* Tooltip/Cloud message */}
            <div
                className={`
          bg-white border-3 border-black p-3 mb-2 shadow-neo-lg 
          transition-all duration-300 origin-bottom-right
          ${isHovered ? 'scale-100 opacity-100' : 'scale-75 opacity-0 pointer-events-none'}
        `}
            >
                <p className="font-bold text-sm whitespace-nowrap">Don't hold back! 😤</p>
            </div>

            {/* Main Button */}
            <div className="relative group">
                <a
                    href={whatsappUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    aria-label="Send feedback on WhatsApp"
                    className="
            flex items-center justify-center gap-2
            bg-accent-coral hover:bg-primary-hover
            text-black font-bold border-3 border-black
            px-4 py-3 
            shadow-neo-lg active:shadow-none active:translate-x-[4px] active:translate-y-[4px]
            transition-all duration-200
            rounded-none
          "
                >
                    <Flame size={24} strokeWidth={2.5} />
                    <span className={`uppercase tracking-wider ${onForm ? 'hidden md:inline' : ''}`}>Roast Me</span>
                </a>

                {/* Close/Hide button (optional, in case it's annoying) */}
                <button
                    onClick={(e) => {
                        e.preventDefault();
                        setIsVisible(false);
                    }}
                    className="
            absolute -top-2 -left-2 
            bg-white border-2 border-black 
            p-1 hover:bg-black hover:text-white
            transition-colors
            opacity-0 group-hover:opacity-100
          "
                    title="Hide button"
                >
                    <X size={12} />
                </button>
            </div>
        </div>
    );
};

export default RoastButton;
