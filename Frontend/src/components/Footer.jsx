import { Linkedin, Instagram, Heart } from "lucide-react";

const Footer = () => {
    return (
        <footer className="w-full border-t border-white/10 bg-black/30 backdrop-blur-xl mt-24">
            <div className="max-w-7xl mx-auto px-4 py-12 grid md:grid-cols-3 gap-10">

                {/* Brand Section */}
                <div className="space-y-3">
                    <h3 className="text-xl font-semibold text-white tracking-wide">ReportAuto</h3>
                    <p className="text-gray-400 text-sm leading-relaxed max-w-xs">
                        Automating academic excellence with AI-powered report generation.
                    </p>
                </div>

                {/* Quick Links */}
                <div className="flex flex-col md:items-center space-y-3">
                    <h4 className="text-white font-medium text-sm uppercase tracking-wider">Quick Links</h4>
                    <ul className="space-y-2 text-gray-300 text-sm">
                        <li className="hover:text-white transition-colors cursor-pointer">Features</li>
                        <li className="hover:text-white transition-colors cursor-pointer">Pricing</li>
                        <li className="hover:text-white transition-colors cursor-pointer">Documentation</li>
                        <li className="hover:text-white transition-colors cursor-pointer">Contact</li>
                    </ul>
                </div>

                {/* Contributors Removed as per request */}
                <div className="space-y-3 md:text-right">
                    {/* Empty placeholder to maintain grid layout or remove if you want 2 cols. 
                        User asked to remove "made by...". 
                        I will just remove the content but keep the div or remove it.
                        Grid is md:grid-cols-3. Ideally I switch to grid-cols-2 or leave empty/logo.
                        Let's just remove the text content.
                    */}
                </div>
            </div>

            {/* Bottom Bar */}
            <div className="border-t border-white/10 py-4">
                <p className="text-center text-gray-500 text-xs">
                    © {new Date().getFullYear()} ReportAuto. All Rights Reserved.
                </p>
            </div>
        </footer>
    );
};

export default Footer;
