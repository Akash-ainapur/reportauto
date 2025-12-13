import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { signInWithRedirect, signInWithEmailAndPassword, createUserWithEmailAndPassword, getRedirectResult } from "firebase/auth";
import { auth, googleProvider } from "../firebase";
import GlassCard from "../components/GlassCard";
import { cn } from "../lib/utils";
import { Mail, Lock, User, ArrowRight } from "lucide-react";

const AuthPage = () => {
    const [isLogin, setIsLogin] = useState(true);
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    // Check for redirect result on mount
    useEffect(() => {
        getRedirectResult(auth)
            .then((result) => {
                if (result) {
                    navigate("/generate");
                }
            })
            .catch((error) => {
                console.error("Redirect Error:", error);
                setError(error.message);
            });
    }, []);

    // Auto-redirect if already logged in
    useEffect(() => {
        const unsubscribe = auth.onAuthStateChanged((user) => {
            if (user) {
                navigate("/generate");
            }
        });
        return () => unsubscribe();
    }, []);

    const handleAuth = async (e) => {
        e.preventDefault();
        setError("");
        setLoading(true);
        try {
            if (isLogin) {
                await signInWithEmailAndPassword(auth, email, password);
            } else {
                await createUserWithEmailAndPassword(auth, email, password);
            }
            navigate("/generate"); // Redirect to generator
        } catch (err) {
            setError(err.message.replace("Firebase:", "").trim());
        } finally {
            setLoading(false);
        }
    };

    const handleGoogleAuth = async () => {
        setError("");
        try {
            await signInWithRedirect(auth, googleProvider);
            // No navigate here, it happens after redirect
        } catch (err) {
            setError(err.message);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center p-4">
            <div className="w-full max-w-md">
                <GlassCard className="relative overflow-hidden">
                    {/* Header */}
                    <div className="text-center mb-8">
                        <h2 className="text-3xl font-bold text-white mb-2">
                            {isLogin ? "Welcome Back" : "Create Account"}
                        </h2>
                        <p className="text-gray-400 text-sm">
                            {isLogin ? "Enter your credentials to access your account" : "Join us and start automating today"}
                        </p>
                    </div>

                    {/* Setup Tabs */}
                    <div className="flex p-1 bg-black/20 rounded-xl mb-8 relative">
                        <div
                            className={cn(
                                "absolute top-1 bottom-1 w-[calc(50%-4px)] bg-primary/20 rounded-lg transition-all duration-300 ease-out",
                                isLogin ? "left-1" : "left-[calc(50%+4px)]"
                            )}
                        />
                        <button
                            onClick={() => setIsLogin(true)}
                            className={cn("flex-1 py-2 text-sm font-medium z-10 transition-colors", isLogin ? "text-white" : "text-gray-400")}
                        >
                            Login
                        </button>
                        <button
                            onClick={() => setIsLogin(false)}
                            className={cn("flex-1 py-2 text-sm font-medium z-10 transition-colors", !isLogin ? "text-white" : "text-gray-400")}
                        >
                            Sign Up
                        </button>
                    </div>

                    {/* Form */}
                    <form onSubmit={handleAuth} className="space-y-4">
                        <div className="space-y-2">
                            <label className="text-xs font-medium text-gray-400 ml-1">Email Address</label>
                            <div className="relative group">
                                <Mail className="absolute left-3 top-3 text-gray-500 group-focus-within:text-white transition-colors w-5 h-5" />
                                <input
                                    type="email"
                                    required
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    className="w-full bg-black/20 border border-white/10 rounded-xl py-2.5 pl-10 pr-4 text-white focus:outline-none focus:border-primary/50 focus:bg-black/40 transition-all placeholder:text-gray-600"
                                    placeholder="student@example.com"
                                />
                            </div>
                        </div>

                        <div className="space-y-2">
                            <label className="text-xs font-medium text-gray-400 ml-1">Password</label>
                            <div className="relative group">
                                <Lock className="absolute left-3 top-3 text-gray-500 group-focus-within:text-white transition-colors w-5 h-5" />
                                <input
                                    type="password"
                                    required
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    className="w-full bg-black/20 border border-white/10 rounded-xl py-2.5 pl-10 pr-4 text-white focus:outline-none focus:border-primary/50 focus:bg-black/40 transition-all placeholder:text-gray-600"
                                    placeholder="••••••••"
                                />
                            </div>
                        </div>

                        {error && (
                            <p className="text-red-400 text-xs text-center bg-red-500/10 py-2 rounded-lg">{error}</p>
                        )}

                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full py-3 bg-gradient-to-r from-purple-600 to-pink-600 rounded-xl text-white font-bold hover:shadow-[0_0_20px_rgba(168,85,247,0.4)] hover:scale-[1.02] active:scale-[0.98] transition-all flex items-center justify-center gap-2 group"
                        >
                            {loading ? "Processing..." : (
                                <>
                                    {isLogin ? "Sign In" : "Get Started"}
                                    <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                                </>
                            )}
                        </button>
                    </form>

                    <div className="my-6 flex items-center gap-4">
                        <div className="h-px bg-white/10 flex-1" />
                        <span className="text-xs text-gray-500 font-medium">OR CONTINUE WITH</span>
                        <div className="h-px bg-white/10 flex-1" />
                    </div>

                    <button
                        onClick={handleGoogleAuth}
                        className="w-full py-2.5 bg-white/5 border border-white/10 rounded-xl text-white font-medium hover:bg-white/10 transition-colors flex items-center justify-center gap-2"
                    >
                        <svg viewBox="0 0 24 24" className="w-5 h-5" fill="currentColor">
                            <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4" />
                            <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853" />
                            <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05" />
                            <path d="M12 4.63c1.61 0 3.06.56 4.21 1.64l3.16-3.16C17.45 1.19 14.97 0 12 0 7.7 0 3.99 2.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335" />
                        </svg>
                        Google
                    </button>
                </GlassCard>
            </div>
        </div>
    );
};

export default AuthPage;
