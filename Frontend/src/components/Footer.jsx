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

                {/* Contributors */}
                <div className="space-y-3 md:text-right">
                    <p className="text-sm text-gray-300 flex md:justify-end items-center gap-2">
                        Made with <Heart className="w-4 h-4 text-red-500 fill-red-500" /> by
                    </p>

                    <div className="flex flex-col gap-3 md:items-end">

                        {/* Contributor 1 */}
                        <div className="flex items-center gap-3 bg-white/5 rounded-full px-4 py-2 hover:bg-white/10 transition-colors">
                            <span className="text-white font-medium text-sm">Akshay H</span>
                            <div className="flex gap-2">
                                <a
                                    href="https://www.linkedin.com/in/akshay-h-335abb293"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-blue-400 hover:text-blue-300 transition-colors"
                                >
                                    <Linkedin className="w-4 h-4" />
                                </a>
                                <a
                                    href="#"
                                    className="text-pink-400 hover:text-pink-300 transition-colors"
                                >
                                    <Instagram className="w-4 h-4" />
                                </a>
                            </div>
                        </div>

                        {/* Contributor 2 */}
                        <div className="flex items-center gap-3 bg-white/5 rounded-full px-4 py-2 hover:bg-white/10 transition-colors">
                            <span className="text-white font-medium text-sm">Akash Ainapur</span>
                            <div className="flex gap-2">
                                <a
                                    href="https://linkedin.com/in/akashainapur"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-blue-400 hover:text-blue-300 transition-colors"
                                >
                                    <Linkedin className="w-4 h-4" />
                                </a>
                                <a
                                    href="#"
                                    className="text-pink-400 hover:text-pink-300 transition-colors"
                                >
                                    <Instagram className="w-4 h-4" />
                                </a>
                            </div>
                        </div>

                    </div>
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
