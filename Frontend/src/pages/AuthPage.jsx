import { SignIn } from "@clerk/clerk-react";
import Navbar from "../components/Navbar";

const AuthPage = () => {
    return (
        <div className="min-h-screen pt-24 pb-12 px-4 bg-retro-dots flex flex-col items-center justify-center">
            <Navbar />

            {/* Badge */}
            <div className="mb-8 transform -rotate-1">
                <span className="bg-retro-yellow text-black font-['Oswald'] font-bold uppercase px-4 py-1 border-2 border-black shadow-brutal-sm">
                    Access Terminal
                </span>
            </div>

            <div className="w-full max-w-md bg-white border-3 border-black p-1 shadow-brutal-lg">
                <div className="bg-white border-2 border-black p-8 flex justify-center">
                    <SignIn />
                </div>
            </div>
        </div>
    );
};

export default AuthPage;
