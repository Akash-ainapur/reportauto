import { Linkedin, Instagram, Heart } from "lucide-react";

const Footer = () => {
    return (
        <footer className="w-full border-t-3 border-black bg-white mt-24">
            <div className="max-w-7xl mx-auto px-4 py-12 grid md:grid-cols-3 gap-10">

                {/* Brand Section */}
                <div className="space-y-3">
                    <h3 className="text-2xl font-heading uppercase tracking-wide text-black pb-2 border-b-2 border-black inline-block">PROJECT_HACK.exe</h3>
                    <p className="text-black font-mono text-sm leading-relaxed max-w-xs">
                        Automating academic excellence so you can focus on... whatever else you do.
                    </p>
                </div>

                {/* Quick Links */}
                <div className="flex flex-col md:items-center space-y-3">
                    <h4 className="text-black font-heading text-lg uppercase tracking-wider bg-yellow-300 px-2 border-2 border-black shadow-neo -rotate-2 inline-block">Quick Links</h4>
                    <ul className="space-y-2 text-black font-bold text-sm text-center md:text-left mt-4">
                        <li className="hover:underline hover:bg-black hover:text-white transition-colors cursor-pointer px-2 py-1">FEATURES</li>
                        <li className="hover:underline hover:bg-black hover:text-white transition-colors cursor-pointer px-2 py-1">PRICING</li>
                        <li className="hover:underline hover:bg-black hover:text-white transition-colors cursor-pointer px-2 py-1">DOCS</li>
                    </ul>
                </div>

                {/* Socials / Extra */}
                <div className="md:text-right space-y-4">
                    <p className="font-mono text-xs text-black">
                        NO REFUNDS.<br />
                        NO WARRANTIES.<br />
                        PURE VIBES.
                    </p>
                </div>
            </div>

            {/* Bottom Bar */}
            <div className="border-t-3 border-black py-4 bg-black text-white">
                <p className="text-center font-mono text-xs uppercase">
                    © {new Date().getFullYear()} PROJECT_HACK.exe // ALL RIGHTS RESERVED
                </p>
            </div>
        </footer>
    );
};

export default Footer;
